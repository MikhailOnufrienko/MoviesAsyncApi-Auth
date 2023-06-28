from pydantic import BaseModel, EmailStr, constr

class UserRegistration(BaseModel):
    login: str
    password: constr(min_length=8, max_length=50)
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    