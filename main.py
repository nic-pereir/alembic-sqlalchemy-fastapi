from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

# Schema changes are managed with Alembic migrations (see the `alembic/`
# folder), so we intentionally do NOT call Base.metadata.create_all() here.

app = FastAPI(
    title="Library API",
    description=(
        "A small CRUD API for authors and books, built with FastAPI, "
        "SQLAlchemy 2.x (ORM) and Alembic (migrations)."
    ),
    version="1.0.0",
)


# AUTHORS
@app.post("/authors", response_model=schemas.AuthorOut, status_code=201, tags=["authors"])
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_author(db, author)
    except crud.DuplicateEmailError:
        raise HTTPException(status_code=409, detail="An author with this email already exists")


@app.get("/authors", response_model=list[schemas.AuthorOut], tags=["authors"])
def list_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_authors(db, skip=skip, limit=limit)


@app.get("/authors/{author_id}", response_model=schemas.AuthorOut, tags=["authors"])
def get_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author


@app.put("/authors/{author_id}", response_model=schemas.AuthorOut, tags=["authors"])
def update_author(author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    try:
        db_author = crud.update_author(db, author_id, author)
    except crud.DuplicateEmailError:
        raise HTTPException(status_code=409, detail="An author with this email already exists")
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author


@app.delete("/authors/{author_id}", status_code=204, tags=["authors"])
def delete_author(author_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_author(db, author_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Author not found")
    return None


@app.get("/authors/{author_id}/books", response_model=schemas.AuthorBooksOut, tags=["authors"])
def get_author_books(author_id: int, db: Session = Depends(get_db)):
    author = crud.get_author(db, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return schemas.AuthorBooksOut(author=author.name, books=author.books)


# BOOKS
@app.post("/books", response_model=schemas.BookOut, status_code=201, tags=["books"])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = crud.create_book(db, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_book


@app.get("/books", response_model=list[schemas.BookOut], tags=["books"])
def list_books(
    skip: int = 0,
    limit: int = 100,
    author_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: Optional[str] = Query(default=None, description="e.g. 'title' or '-title'"),
    db: Session = Depends(get_db),
):
    return crud.get_books(
        db, skip=skip, limit=limit, author_id=author_id, search=search, sort=sort
    )


@app.get("/books/{book_id}", response_model=schemas.BookOut, tags=["books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", response_model=schemas.BookOut, tags=["books"])
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    try:
        db_book = crud.update_book(db, book_id, book)
    except crud.AuthorNotFoundError:
        raise HTTPException(status_code=404, detail="Author not found")
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.delete("/books/{book_id}", status_code=204, tags=["books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return None
