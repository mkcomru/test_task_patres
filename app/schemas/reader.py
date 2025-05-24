from typing import Optional
from pydantic import BaseModel, EmailStr


class ReaderBase(BaseModel):
    name: str
    email: EmailStr


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class ReaderInDBBase(ReaderBase):
    id: int

    class Config:
        orm_mode = True


class Reader(ReaderInDBBase):
    pass 