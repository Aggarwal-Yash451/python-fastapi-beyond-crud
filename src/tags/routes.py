from fastapi import APIRouter, Depends
from src.tags.service import TagService
from src.auth.dependencies import RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from typing import List
from src.tags.schemas import TagModel, TagAddModel, TagCreateModel
from src.books.models import Book

user_role_checker = RoleChecker(["user", "admin"])
tag_router = APIRouter()
tag_service = TagService()


@tag_router.get("/", response_model=List[TagModel])
async def get_all_tags(session: AsyncSession = Depends(get_session), role_check = Depends(user_role_checker)):
    tags = await tag_service.get_all_tags(session)

    return tags

@tag_router.post("/")
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session), role_check = Depends(user_role_checker)):
    tag_added = await tag_service.add_tag(tag_data, session)

    return tag_added

@tag_router.post("/book/{book_uid}/tags", response_model=Book)
async def add_tag_to_book(book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session), role_check = Depends(user_role_checker)):
    book_with_tag = await tag_service.add_tag_to_book(book_uid, tag_data, session)

    return book_with_tag

@tag_router.put("/{tag_uid}", response_model=TagModel)
async def update_tag(tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session), role_check = Depends(user_role_checker)):
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)

    return updated_tag

@tag_router.delete("/{tag_uid}")
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session), role_check = Depends(user_role_checker)):
    await tag_service.delete_tag(tag_uid, session)
    return "Tag deleted success"

