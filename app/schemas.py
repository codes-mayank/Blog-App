from pydantic import BaseModel
from datetime import datetime


# Blog Schemas
class BlogBase(BaseModel):
    title: str
    body: str


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BlogBase):
    pass


class BlogOut(BlogBase):
    id: int
    slug: str
    author_id: int
    created_at: datetime


class BlogOutWithAuthor(BlogBase):
    id: int
    slug: str
    author_id: int
    created_at: datetime
    author_fullname: str
    author_username: str


# Token Schemas
class Token(BaseModel):
    sub: str
    user_id: int
    email: str


# User Schemas
class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


class UserIn(UserBase):
    password: str
    

class UserInDB(UserBase):
    id: int
    hashed_password: str
    disabled: bool | None = None


class UserOut(UserBase):
    id: int


class UserLogin(BaseModel):
    username_or_email: str
    password: str

