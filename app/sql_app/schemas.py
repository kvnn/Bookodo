from pydantic import BaseModel


class BookCreate(BaseModel):
    original_id: int
    title: str
    isbn: str
    language: str
    pages: int
    rating_average: float
    rating_count: int
    review_count: int
    image_url: str

class Book(BookCreate):
    id: int

class ListCreate(BaseModel):
    title: str

class ListBookCreate(BaseModel):
    book_id: int
    new_list_title: str = None
    existing_list_id: int = None

class List(ListCreate):
    id: int

class CreateListImageRequest(BaseModel):
    list_id: int

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserCreateRequest(UserLoginRequest):
    pass