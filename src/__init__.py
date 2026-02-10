from fastapi import FastAPI
from src.books.routes import book_router

version = "1"

app = FastAPI(
    title="Bookly",
    description="A REST api for a book review system",
    version=version
)

app.include_router(book_router , prefix="/api/{version}/books" , tags=["books"])