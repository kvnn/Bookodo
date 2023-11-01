import json
import logging

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload

from utils import get_scene_image_url
from sql_app.models import Book, List, User
from sql_app.schemas import BookCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


''' Users '''
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

''' Books '''
def get_books(db: Session):
    books = db.query(Book).order_by(Book.title.asc()).all()
    return jsonable_encoder(books)

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def create_book(db: Session, book: BookCreate):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    return db_book

''' Lists '''
def _add_img_url_to_lists(lists):
    for list in lists:
        if list.image_filename:
            list.image_url = get_scene_image_url(list.image_filename)
    return lists

def get_lists(db:Session, user_id: int = None):
    user_lists = []

    all_lists = db.query(List).options(joinedload(List.books)).filter(
        List.user_id != user_id
    ).order_by(
        List.dateadded.desc()
    ).all()

    if user_id:
        user_lists = db.query(List).options(joinedload(List.books)).filter(
            List.user_id == user_id
        ).order_by(
            List.dateadded.desc()
        ).all()
    
    all_lists = _add_img_url_to_lists(all_lists)
    user_lists = _add_img_url_to_lists(user_lists)

    return jsonable_encoder({
        'all_lists': all_lists,
        'user_lists': user_lists
    })

def create_list(
    db: Session,
    title: str,
    user_id: int
):      
    db_list = List(title=title, user_id=user_id)
    db.add(db_list)
    db.commit()
    return db_list

def add_book_to_list(
    db: Session,
    list_id = int,
    book_id = int
):
    list = db.query(List).filter(
        List.id == list_id
    ).first()
    
    book = get_book_by_id(db, book_id)
    list.books.append(book)
    db.commit()
    return list
