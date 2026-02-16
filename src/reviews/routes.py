from fastapi import APIRouter, Depends, HTTPException, status
from src.db.models import User
from src.reviews.schemas import ReviewCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.reviews.service import ReviewService
from src.auth.dependencies import get_curr_user
from src.auth.dependencies import RoleChecker
from src.db.models import Review

admin_role_checker = RoleChecker(["admin"])
user_role_checker = RoleChecker(["user", "admin"])

review_router = APIRouter()
review_service = ReviewService()


@review_router.post("/book/{book_uid}")
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_curr_user),
    session: AsyncSession = Depends(get_session),
    check_role=Depends(user_role_checker),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review


@review_router.get("/")
async def get_all_reviews(
    session: AsyncSession = Depends(get_session), check_role=Depends(admin_role_checker)
):
    reviews = await review_service.get_all_reviews(session)

    if reviews:
        return reviews

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Reviews not found!"
    )


@review_router.get("/{review_id}")
async def get_review(review_id: str, session: AsyncSession = Depends(get_session), check_role = Depends(user_role_checker)):
    result = await review_service.get_review(review_id, session)

    if result:
        return result

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
    )

@review_router.delete("/{review_id}")
async def delete_review(review_id: str, session: AsyncSession = Depends(get_session), check_role = Depends(user_role_checker)):
    await review_service.delete_review(review_id, session)
    return "Book deletion success"