from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr

class UserRegistration(BaseModel):
    login: str
    password: constr(min_length=8, max_length=50)
    first_name: str | None
    last_name: str | None
    email: EmailStr
    

class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class ChangeCredentials(BaseModel):
    new_login: str | None
    old_password: str
    new_password: str | None


class LoginHistoryToDB(BaseModel):
    user_id: str
    user_agent: str
    login_dt: datetime


class LoginHistorySingleRecord(BaseModel):
    user_agent: str
    login_dt: datetime


class LoginHistoryResponse(BaseModel):
    login_history: list[LoginHistorySingleRecord]


class UserProfile(BaseModel):
    user_id: UUID
    registration_dt: datetime
    active: bool
    is_staff: bool
    role_id: UUID


class NewRole(BaseModel):
    name: str
    description: str
