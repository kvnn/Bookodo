import asyncio
import json
import logging
import os
from typing import List

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import redis

from config import settings
from scripts import import_books_from_json
from services.list_image import ListImageService
from services.auth import AuthService
from sql_app import crud, models
from sql_app.database import get_db, engine, SessionLocal
from sql_app.schemas import CreateListImageRequest, UserCreateRequest, UserLoginRequest, ListCreate, ListBookCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

redis_url = settings.redis_url
redis_client = redis.from_url(redis_url)

app.mount("/static", StaticFiles(directory="static"), name="static")

''' Seed our db '''
db = SessionLocal()
if not db.query(models.Book).first():
    import_books_from_json()

''' end Seed '''


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("base.html", {
        "request": request
    })

@app.get("/books", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    return JSONResponse(content={"books": crud.get_books(db)})

@app.get("/lists", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db), user: str = Depends(AuthService.get_current_user)):
    print(f'user is {user}')
    return JSONResponse(content={"lists": crud.get_lists(db, user.id if user else None)})

@app.post("/lists")
async def create_list(data: ListCreate, db: Session = Depends(get_db), user: str = Depends(AuthService.get_current_user)):
    # this endpoint requires user auth
    if not user:
        raise HTTPException(status_code=401, detail="Authorization required. Please register or sign in.")
    try:
        crud.create_list(
            db = db,
            title = data.title,
            user_id = user.id
        )
        lists = crud.get_lists(db, user_id=user.id if user else None)
        return JSONResponse(content={"success": True})
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)

@app.post("/lists/book")
async def add_book_to_list(data: ListBookCreate, db: Session = Depends(get_db), user: str = Depends(AuthService.get_current_user)):
    # this endpoint requires user auth
    if not user:
        raise HTTPException(status_code=401, detail="Authorization required. Please register or sign in.")
    try:
        if data.new_list_title:
            # new_list_title takes preference because at this time existing_list_id will always exist due to form implementation on front-end
            list = crud.create_list(
                db,
                title = data.new_list_title,
                user_id = user.id
            )
            crud.add_book_to_list(
                db,
                list_id = list.id,
                book_id = data.book_id
            )
        else:
            crud.add_book_to_list(
                db,
                list_id = data.existing_list_id,
                book_id = data.book_id
            )

        lists = crud.get_lists(db, user_id=user.id if user else None)
        return JSONResponse(content={"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

@app.post("/register")
async def register(data: UserCreateRequest, db: Session = Depends(get_db)):
    user_token = AuthService.create_user(db, data)
    return JSONResponse(content={
        "access_token": user_token,
        "token_type": "bearer",
        "username": data.username
    })


@app.post("/login")
async def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    access_token = AuthService.login(db, data)
    if access_token:
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "username": data.username
        })
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post('/lists/image')
def generate_list_image(data: CreateListImageRequest, db: Session = Depends(get_db)):
    task_id, error = ListImageService.generate_list_image(db, data)
    if task_id:
        return JSONResponse(content={"task_id": task_id})
    return JSONResponse(content={"error": error})


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        if not await is_valid_task_id(task_id):
            await websocket.send_text(json.dumps({"error": f"Invalid task ID {task_id}"}))
            return

        await subscribe_to_task_updates(websocket, task_id)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


async def is_valid_task_id(task_id):
    try:
        return redis_client.exists(task_id)
    except Exception as e:
        logger.error(f"Error while validating task ID: {e}")
        return False


async def subscribe_to_task_updates(websocket, task_id):
    try:
        # Start a separate task to send updates while the task is running
        await asyncio.create_task(send_task_updates(websocket, task_id))
    except Exception as e:
        logger.error(f"Error while subscribing to task updates: {e}")


async def send_task_updates(websocket, task_id):
    try:
        while True:
            # TODO: if determine if the celery backend is down / task is not running
            # and handle appropriately
            task_details = AsyncResult(task_id)
            
            print(f'task_details for {task_id} is {task_details.result} with state {task_details.state}')

            if task_details.ready():
                logger.info(f'send_task_updates] clearing task result={task_details.result}')
                await send_task_result(websocket, task_id, task_details.result, completed=True)
                await clear_task_id(task_id)
                break
            else:
                await send_task_result(websocket, task_id, task_details.result)

            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error while sending task updates: {e}")


async def send_task_result(websocket, task_id, result, completed=False):
    try:
        # Attempt to serialize the result to JSON
        try:
            payload = {
                "task_id": task_id,
                "task_results": result,
                "completed": completed
            }
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.warn(f'[send_task_result] send for {result} due to error {e}')
        
    except Exception as e:
        logger.error(f"Error sending task result over WebSocket: {e}")


async def clear_task_id(task_id):
    try:
        redis_client.delete(task_id)
    except Exception as e:
        logger.error(f"Error clearing task ID: {e}")