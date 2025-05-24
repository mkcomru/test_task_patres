from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.reader import Reader
from app.schemas.reader import ReaderCreate, ReaderUpdate


def get_reader(db: Session, reader_id: int) -> Optional[Reader]:
    return db.query(Reader).filter(Reader.id == reader_id).first()


def get_reader_by_email(db: Session, email: str) -> Optional[Reader]:
    return db.query(Reader).filter(Reader.email == email).first()


def get_readers(db: Session, skip: int = 0, limit: int = 100) -> List[Reader]:
    return db.query(Reader).offset(skip).limit(limit).all()


def create_reader(db: Session, reader: ReaderCreate) -> Reader:
    db_reader = Reader(**reader.dict())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader


def update_reader(db: Session, db_reader: Reader, reader_in: ReaderUpdate) -> Reader:
    update_data = reader_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_reader, field, value)
    
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader


def delete_reader(db: Session, db_reader: Reader) -> None:
    db.delete(db_reader)
    db.commit()