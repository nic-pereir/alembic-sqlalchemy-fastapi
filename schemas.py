from pydantic import BaseModel, ConfigDict, EmailStr

# AUTHORS
class AuthorBase(BaseModel):
    name: str
    email: EmailStr


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

# BOOKS
class BookBase(BaseModel):
    title: str


class BookCreate(BookBase):
    author_id: int


class BookUpdate(BookBase):
    author_id: int


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int


class BookSummary(BaseModel):
    """Slim book representation used inside AuthorBooksOut."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class AuthorBooksOut(BaseModel):
    """Response shape for GET /authors/{author_id}/books."""

    author: str
    books: list[BookSummary]
