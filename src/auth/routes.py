from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from src.auth.schemas import UserCreateModel, UserLoginModel, UserBookModel
from src.auth.service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.schemas import PasswordResetRequestModel, PasswordResetConfirm
from src.auth.utils import (
    create_access_token,
    verify_pwd,
    create_url_safe_token,
    decode_url_safe_token,
    generate_pwd_hash
)
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer
from src.db.redis import add_jti_to_blocklist
from src.auth.dependencies import get_curr_user, RoleChecker
from src.auth.schemas import EmailModel
from src.mail import create_message, mail
from src.config import Config

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to the app</h1>"

    message = create_message(recipients=emails, subject="Welcome", body=html)

    await mail.send_message(message)

    return {"message": "Email sent success"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    isPresent = await user_service.user_exists(email, session)

    if isPresent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User already present"
        )

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">  link </a> to verify your email</p>
"""

    message = create_message(
        recipients=[email], subject="Email verification", body=html_message
    )

    bg_tasks.add_task(mail.send_message, message)

    return {
        "message": "Account created. Check your email for verification!!",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verification success"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login_user(
    user_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        pass_valid = verify_pwd(password, user.password_hash)

        if pass_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password"
    )


@auth_router.get("/refresh_token")
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid")


@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(
    user=Depends(get_curr_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out success"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email
    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href="{link}">  link </a> to reset your password</p>
"""

    message = create_message(
        recipients=[email], subject="Email verification", body=html_message
    )

    await mail.send_message(message)

    return JSONResponse(
        content={
            "message": "Password reset link sent to your email",
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post("/password-reset-confirm/{token}")
async def reset_password_confrim(token: str, passwords: PasswordResetConfirm , session: AsyncSession = Depends(get_session)):

    if passwords.confirm_new_password != passwords.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Passwords don't match")
    
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        hash_password = generate_pwd_hash(password=passwords.new_password)
        await user_service.update_user(user, {"password_hash": hash_password}, session)

        return JSONResponse(
            content={"message": "Password reset success"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


