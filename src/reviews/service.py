from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.schemas import ReviewCreateModel
from fastapi import HTTPException, status
from sqlmodel import select
from src.db.models import Review
from fastapi import Depends
from src.db.main import get_session
from sqlmodel import desc

user_service = UserService()
book_service = BookService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid, session)
            user = await user_service.get_user_by_email(user_email, session)

            review_data_dict = review_data.model_dump()

            new_review = Review(**review_data_dict)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()

            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            )

    async def get_all_reviews(self , session: AsyncSession = Depends(get_session)):
        statement = select(Review)

        result = await session.exec(statement)

        reviews = result.all()

        return reviews
    

    async def get_review(self, review_uid: str, session: AsyncSession = Depends(get_session)):
        statement = select(Review).where(Review.uid == review_uid).order_by(desc(Review.rating))

        result = await session.exec(statement)

        return result.first()
    
    async def delete_review(self, review_uid: str, session: AsyncSession = Depends(get_session)):
        review = await self.get_review(review_uid, session)

        if review:
            await session.delete(review)
            await session.commit()

            return "Review deletion success"
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")