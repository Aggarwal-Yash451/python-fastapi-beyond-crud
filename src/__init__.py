from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import auth_router

@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting ...")
    from src.books.db_models import Book
    await init_db()
    yield
    print("server is stopping ...")


version = "1"

app = FastAPI(
    title="Bookly",
    description="A REST api for a book review system",
    version=version,
    lifespan=life_span,
)

app.include_router(book_router, prefix="/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix="/api/{version}/auth", tags=["auth"])
