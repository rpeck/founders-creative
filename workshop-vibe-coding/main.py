from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Models ---
class Review(BaseModel):
    rating: int
    comment: str

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    reviews: List[Review] = []

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str

class ReviewCreate(BaseModel):
    rating: int
    comment: str

# --- In-memory database ---
db: List[Book] = [
    Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Classic", reviews=[]),
    Book(id=2, title="To Kill a Mockingbird", author="Harper Lee", genre="Classic", reviews=[Review(rating=5, comment="A masterpiece!")])
]
next_book_id = 3

# --- Endpoints ---
@app.get("/books", response_model=List[Book])
def get_books():
    """
    Retrieve a list of all books.
    """
    return db

@app.post("/books", response_model=Book, status_code=201)
def add_book(book: BookCreate):
    """
    Add a new book to the collection.
    """
    global next_book_id
    new_book = Book(
        id=next_book_id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        reviews=[]
    )
    db.append(new_book)
    next_book_id += 1
    return new_book

@app.post("/books/{book_id}/reviews", response_model=Book)
def add_review_to_book(book_id: int, review: ReviewCreate):
    """
    Add a review to a specific book.
    """
    book_to_update = None
    for book in db:
        if book.id == book_id:
            book_to_update = book
            break
    
    if not book_to_update:
        raise HTTPException(status_code=404, detail="Book not found")
    
    new_review = Review(rating=review.rating, comment=review.comment)
    book_to_update.reviews.append(new_review)
    
    return book_to_update

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    """
    Delete a specific book.
    """
    book_to_delete = next((book for book in db if book.id == book_id), None)
    
    if not book_to_delete:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.remove(book_to_delete)
    return 