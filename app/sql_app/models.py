from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, Float, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TimestampMixin:
    dateadded = Column(DateTime, default=datetime.utcnow, nullable=False)
    dateupdated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


# association table for the Book / List m2m relationship
list_book = Table(
    "list_book",
    Base.metadata,
    Column("list_id", ForeignKey("lists.id")),
    Column("book_id", ForeignKey("books.id"))
)

class Book(Base, TimestampMixin):
    __tablename__ = 'books'
    
    id: Mapped[int] = mapped_column(primary_key=True)

    original_id = Column(Integer, unique=True)
    title = Column(String(255), nullable=False)
    isbn = Column(String(50),unique=True, nullable=True)
    language = Column(String(2), nullable=False)
    pages = Column(Integer, nullable=False)
    rating_average = Column(Float, nullable=False)
    rating_count = Column(Integer, nullable=False)
    review_count = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=False)


class List(Base, TimestampMixin):
    __tablename__ = 'lists'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    books: Mapped[List[Book]] = relationship(secondary=list_book)
    title = Column(String(50), nullable=False)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    image_filename = Column(String(255), nullable=True)
    
    @property
    def book_titles(self):
        return ', '.join([book.title for book in self.books])


