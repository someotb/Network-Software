import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    id: str | None = None
    name: str
    date: str


books: dict[str, Book] = {}


@app.get("/bookings")
async def get_books():
    return books


@app.get("/bookings/{id}")
async def get_book(id: str):
    book = books.get(id)
    if not book:
        raise HTTPException(status_code=404)
    return book


@app.post("/bookings", status_code=201)
async def post_book(book: Book):
    book.id = str(uuid.uuid4())
    books[book.id] = book
    return book


@app.put("/bookings/{id}")
async def put_book(id: str, updated_book: Book):
    if id not in books:
        raise HTTPException(status_code=404)

    updated_book.id = id
    books[id] = updated_book
    return updated_book


@app.delete("/bookings/{id}")
async def delete_book(id: str):
    book = books.get(id)
    if not book:
        raise HTTPException(status_code=404)

    books.pop(id)
