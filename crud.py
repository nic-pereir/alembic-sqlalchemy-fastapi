from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models
import schemas


class DuplicateEmailError(Exception):
    """Raised when an author's email already exists in the database."""


class AuthorNotFoundError(Exception):
    """Raised when a referenced author does not exist."""


# AUTHORS
def create_author(db: Session, author: schemas.AuthorCreate) -> models.Author:
    db_author = models.Author(name=author.name, email=author.email)
    db.add(db_author)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError(author.email)
    db.refresh(db_author)
    return db_author

 
def get_authors(db: Session, skip: int = 0, limit: int = 100) -> list[models.Author]:
    stmt = select(models.Author).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_author(db: Session, author_id: int) -> Optional[models.Author]:
    return db.get(models.Author, author_id)


def update_author(
    db: Session, author_id: int, data: schemas.AuthorUpdate) -> Optional[models.Author]:
    db_author = get_author(db, author_id)
    if db_author is None:
        return None

    db_author.name = data.name
    db_author.email = data.email
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError(data.email)
    db.refresh(db_author)
    return db_author
 

def delete_author(db: Session, author_id: int) -> bool:
    db_author = get_author(db, author_id)
    if db_author is None:
        return False
    db.delete(db_author)
    db.commit()
    return True


# BOOKS
def create_book(db: Session, book: schemas.BookCreate) -> Optional[models.Book]:
    author = get_author(db, book.author_id)
    if author is None:
        return None

    db_book = models.Book(title=book.title, author_id=book.author_id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    author_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
) -> list[models.Book]:
    stmt = select(models.Book)

    if author_id is not None:
        stmt = stmt.where(models.Book.author_id == author_id)

    if search:
        stmt = stmt.where(models.Book.title.ilike(f"%{search}%"))

    if sort:
        # "title" -> ascending, "-title" -> descending
        descending = sort.startswith("-")
        field_name = sort[1:] if descending else sort
        column = getattr(models.Book, field_name, None)
        if column is not None:
            stmt = stmt.order_by(column.desc() if descending else column.asc())

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.get(models.Book, book_id)


def update_book(
    db: Session, book_id: int, data: schemas.BookUpdate) -> Optional[models.Book]:
    db_book = get_book(db, book_id)
    if db_book is None:
        return None

    author = get_author(db, data.author_id)
    if author is None:
        raise AuthorNotFoundError(data.author_id)

    db_book.title = data.title
    db_book.author_id = data.author_id
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if db_book is None:
        return False
    db.delete(db_book)
    db.commit()
    return True
