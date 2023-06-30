from pydantic import BaseModel, EmailStr, constr

class UserRegistration(BaseModel):
    login: str
    password: constr(min_length=8, max_length=50)
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    

class UserLogin(BaseModel):
    login: str
    password: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    user_id: str
    refresh_token: str


class TokenData(BaseModel):
    token_data: str

