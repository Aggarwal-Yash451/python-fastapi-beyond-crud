from fastapi import status, HTTPException, APIRouter, Depends
from src.books.models import Book, BookCreateModel, BookUpdateModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from uuid import UUID

book_router = APIRouter()
book_service = BookService()


@book_router.get("", response_model=list[Book], status_code=status.HTTP_200_OK)
async def get_all_books(session: AsyncSession = Depends(get_session)):
    return await book_service.get_all_books(session)


@book_router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    newBook: BookCreateModel, session: AsyncSession = Depends(get_session)
):
    return await book_service.create_book(newBook, session)


@book_router.get("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book_by_id(book_uid: UUID, session: AsyncSession = Depends(get_session)):
    book_found = await book_service.get_book(book_uid, session)

    if book_found:
        return book_found

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.patch("/{book_uid}", status_code=status.HTTP_200_OK)
async def edit_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book:
        return updated_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.delete("/{book_uid}", status_code=status.HTTP_200_OK)
async def delete_book(book_uid: UUID, session: AsyncSession = Depends(get_session)):
    deleted_book = await book_service.delete_book(book_uid, session)

    if delete_book:
        return deleted_book

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
