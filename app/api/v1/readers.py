from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_reader
from app.database.base import get_db
from app.models.user import User
from app.schemas.reader import Reader, ReaderCreate, ReaderUpdate
from app.security.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[Reader])
def read_readers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    readers = crud_reader.get_readers(db, skip=skip, limit=limit)
    return readers


@router.post("/", response_model=Reader, status_code=status.HTTP_201_CREATED)
def create_reader(
    reader_in: ReaderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    reader = crud_reader.get_reader_by_email(db, email=reader_in.email)
    if reader:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Читатель с таким email уже существует",
        )
    reader = crud_reader.create_reader(db, reader=reader_in)
    return reader


@router.get("/{reader_id}", response_model=Reader)
def read_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    reader = crud_reader.get_reader(db, reader_id=reader_id)
    if reader is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден",
        )
    return reader


@router.put("/{reader_id}", response_model=Reader)
def update_reader(
    reader_id: int,
    reader_in: ReaderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    reader = crud_reader.get_reader(db, reader_id=reader_id)
    if reader is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден",
        )
    
    if reader_in.email and reader_in.email != reader.email:
        db_reader = crud_reader.get_reader_by_email(db, email=reader_in.email)
        if db_reader:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Читатель с таким email уже существует",
            )
    
    reader = crud_reader.update_reader(db, db_reader=reader, reader_in=reader_in)
    return reader


@router.delete("/{reader_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    reader = crud_reader.get_reader(db, reader_id=reader_id)
    if reader is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден",
        )
    crud_reader.delete_reader(db, db_reader=reader)
    return None