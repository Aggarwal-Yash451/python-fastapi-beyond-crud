from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status
from src.db.models import Tag
from sqlmodel import select, desc
from src.tags.schemas import TagAddModel, TagCreateModel
from src.books.service import BookService

book_service = BookService()


class TagService:
    async def get_all_tags(self, session: AsyncSession = Depends(get_session)):
        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_tag(self, tag_uid: str, session: AsyncSession = Depends(get_session)):
        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.exec(statement)

        return result.first()

    async def add_tag_to_book(
        self,
        book_uid: str,
        tag_data: TagAddModel,
        session: AsyncSession = Depends(get_session),
    ):
        book = await book_service.get_book(book_uid, session)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        for tag_item in tag_data.tags:
            statement = select(Tag).where(tag_item.name == Tag.name)
            result = await session.exec(statement)

            tag = result.one_or_none()

            if not tag:
                tag = Tag(name=tag_item.name)

            book.tags.append(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)

        return book

    async def add_tag(
        self, tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
    ):
        statement = select(Tag).where(Tag.name == tag_data.name)

        result = await session.exec(statement)
        tag = result.first()

        if tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Tag already present"
            )

        new_tag = Tag(name=tag_data.name)

        session.add(new_tag)
        await session.commit()

        return new_tag

    async def update_tag(
        self,
        tag_uid: str,
        tag_data: TagCreateModel,
        session: AsyncSession = Depends(get_session),
    ):
        tag = await self.get_tag(tag_uid, session)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        update_data_dict = tag_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(tag, k, v)

        await session.commit()
        await session.refresh(tag)

        return tag

    async def delete_tag(
        self, tag_uid: str, session: AsyncSession = Depends(get_session)
    ):
        tag = await self.get_tag(tag_uid, session)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        await session.delete(tag)
        await session.commit()
