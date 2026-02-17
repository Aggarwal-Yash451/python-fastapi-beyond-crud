from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from src.books.models import BookCreateModel
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=4, max_length=8)
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime 
    updated_at: datetime 
    is_verified: bool
    password_hash: str = Field(exclude=True)
    
class UserBookModel(UserModel):
    books: List[BookCreateModel]
    reviews: List[ReviewModel]



class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=4, max_length=8)


class EmailModel(BaseModel):
    addresses: list[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_new_password: str