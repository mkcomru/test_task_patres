from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("readers.id"), nullable=False)
    borrow_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    return_date = Column(DateTime(timezone=True))
    
    book = relationship("Book")
    reader = relationship("Reader") 