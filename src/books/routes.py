from fastapi import status, HTTPException, APIRouter
from src.books.models import Book
from src.books.book_data import books

book_router = APIRouter()

@book_router.get("", response_model=list[Book], status_code=status.HTTP_200_OK)
async def get_all_books():
    return books


@book_router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(newBook: Book):
    books.append(newBook.model_dump())
    return f"Book added success: {newBook}"


@book_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(id: int):
    for book in books:
        if book["id"] == id:
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.patch("/{id}", status_code=status.HTTP_200_OK)
async def edit_book(id: int, newBook: Book):
    for book in books:
        if book["id"] == id:
            book["title"] = newBook.title
            book["author"] = newBook.author
            book["page_count"] = newBook.page_count
            book["publisher"] = newBook.publisher
            book["language"] = newBook.language

            return f"Book edited success {book}"

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int):
    for book in books:
        if book["id"] == id:
            books.remove(book)
            return {"message": "Book deleted success", "book": book}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
