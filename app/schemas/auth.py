from pydantic import BaseModel, EmailStr

class EmailSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    token: str
    new_password: str