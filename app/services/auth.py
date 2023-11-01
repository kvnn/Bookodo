from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from config import settings
from sql_app import crud
from sql_app.database import SessionLocal
from sql_app.models import User
from sql_app.schemas import UserCreateRequest, UserLoginRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class AuthService:
    algo = "HS256"
    
    @classmethod
    def get_current_user(cls, token: str = Depends(oauth2_scheme)):
        print(f'token is {token}')
        user = None
        if not token:
            return None  # we don't want to force authentication at this point
        try:
            # Decode the token
            payload = jwt.decode(token, settings.secret_key, algorithms=[cls.algo])
            username = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            else:
                db = SessionLocal()
                user = crud.get_user_by_username(db, username)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user  # or return a user object based on the username
    
    @classmethod
    def get_password_hash(cls, password):
        return pwd_context.hash(password)
    
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def generate_access_token(cls, username):
        return jwt.encode({"sub": username}, settings.secret_key, algorithm=cls.algo)

    @classmethod
    def login(cls, db, login_data: UserLoginRequest):
        user = db.query(User).filter(User.username==login_data.username).first()
        if user and cls.verify_password(login_data.password, user.password):
            return cls.generate_access_token(user.username)

    @classmethod
    def create_user(cls, db, registration_data: UserCreateRequest):
        if db.query(User).filter(User.username==registration_data.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        # create the user
        new_user = User(username=registration_data.username)
        new_user.password = cls.get_password_hash(registration_data.password)
        db.add(new_user)
        db.commit()
        
        return cls.generate_access_token(registration_data.username)
