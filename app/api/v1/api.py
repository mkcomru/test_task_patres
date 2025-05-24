from fastapi import APIRouter

from app.api.v1 import auth, books, readers, borrowed_books

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(readers.router, prefix="/readers", tags=["readers"])
api_router.include_router(borrowed_books.router, prefix="/borrowed-books", tags=["borrowed-books"])