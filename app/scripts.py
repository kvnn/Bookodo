import json

from sql_app.crud import create_book
from sql_app.database import SessionLocal
from sql_app.schemas import BookCreate

def import_books_from_json(filepath = 'books.json'):
    db = SessionLocal()

    # Import JSON data
    with open(filepath, 'r') as f:
        books_data = json.load(f)

    # Insert books into database
    for book_data in books_data:
        book_data['original_id'] = book_data['id']
        del book_data['id']
        
        isbn = book_data.get('isbn')
        if isbn and len(isbn) == 0:
            book_data['isbn'] = None
 
        try:
            create_book(db, BookCreate(**book_data))
            print(f'successfully imported book {book_data["title"]}')
        except Exception as e:
            print(f'error improting book {book_data["title"]}: {e}')