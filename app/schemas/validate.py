from pydantic import BaseModel, EmailStr


class EmailInput(BaseModel):
    email: EmailStr
