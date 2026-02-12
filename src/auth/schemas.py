from pydantic import BaseModel, Field
from datetime import datetime
import uuid

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


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=4, max_length=8)