from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class BorrowedBookBase(BaseModel):
    book_id: int
    reader_id: int


class BorrowBookCreate(BorrowedBookBase):
    pass


class ReturnBook(BaseModel):
    borrow_id: int


class BorrowedBookInDBBase(BorrowedBookBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class BorrowedBook(BorrowedBookInDBBase):
    pass


class BorrowedBookWithDetails(BorrowedBookInDBBase):
    book_title: str
    book_author: str
    reader_name: str
    reader_email: str 