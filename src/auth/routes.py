from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from src.auth.schemas import UserCreateModel, UserLoginModel
from src.auth.service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.schemas import UserModel
from src.auth.utils import create_access_token, decode_token, verify_pwd


auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    isPresent = await user_service.user_exists(email, session)

    if isPresent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User already present"
        )

    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post("/login")
async def login_user(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await UserService.get_user_by_email(email, session)

    if user is not None:
        pass_valid = verify_pwd(password, user.password_hash)

        
