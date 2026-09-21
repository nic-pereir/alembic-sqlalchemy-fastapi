# Library API

A small CRUD API for **authors** and **books**, built with **FastAPI**,
**SQLAlchemy 2.x** (ORM) and **Alembic** (database migrations).

This project was built as the reference implementation for Week 9 of the
backend mentorship: integrating a FastAPI application with a relational
database through an ORM.

## Stack

- **FastAPI** — web framework and request/response validation
- **SQLAlchemy 2.x** — ORM (`Mapped`, `mapped_column`, `relationship`)
- **Alembic** — schema migrations
- **Pydantic v2** — request/response schemas
- **PostgreSQL** (recommended) or **SQLite** (default, zero setup)

## Project structure

```
library-api/
├── main.py                # FastAPI app and routes
├── models.py              # SQLAlchemy ORM models (Author, Book)
├── schemas.py              # Pydantic schemas
├── crud.py                 # Database access layer
├── database.py              # Engine, Session, Base
├── alembic.ini               # Alembic configuration
├── alembic/
│   ├── env.py                 # Migration environment (wired to models.py)
│   ├── script.py.mako          # Template for new migrations
│   └── versions/
│       └── 0001_create_authors_and_books.py
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

By default the app uses a local SQLite file (`library.db`) — no extra setup
needed. To use PostgreSQL instead (recommended for this exercise), set:

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/library"
```

## Running the migrations

Schema changes are managed with Alembic, not `create_all()`:

```bash
alembic upgrade head
```

This creates the `authors` and `books` tables (with the `author_id` foreign
key and the unique constraint on `authors.email`).

To create a new migration after changing a model:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Running the API

```bash
uvicorn main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## Endpoints

### Authors

| Method | Path                        | Description                          |
|--------|-----------------------------|---------------------------------------|
| POST   | `/authors`                  | Create an author                     |
| GET    | `/authors`                  | List authors (`skip`, `limit`)       |
| GET    | `/authors/{id}`              | Get one author                       |
| PUT    | `/authors/{id}`              | Update an author                     |
| DELETE | `/authors/{id}`              | Delete an author                     |
| GET    | `/authors/{id}/books`         | List an author's books               |

### Books

| Method | Path            | Description                                               |
|--------|-----------------|-------------------------------------------------------------|
| POST   | `/books`        | Create a book (validates that `author_id` exists)          |
| GET    | `/books`        | List books, with filters (see below)                       |
| GET    | `/books/{id}`    | Get one book                                               |
| PUT    | `/books/{id}`    | Update a book                                               |
| DELETE | `/books/{id}`    | Delete a book                                               |

`GET /books` query parameters:

- `skip`, `limit` — pagination
- `author_id` — only books from this author
- `search` — case-insensitive match on `title`
- `sort` — `title` (ascending) or `-title` (descending)

Example:

```
GET /books?search=dom&sort=title&author_id=1&limit=10
```

## Status codes

| Situation                        | Status |
|-----------------------------------|--------|
| Resource created                  | 201    |
| Resource fetched / updated        | 200    |
| Resource deleted                  | 204    |
| Resource not found                | 404    |
| Duplicate author email            | 409    |
| Invalid request body              | 422    |

## Data model

```
Author 1 ──────< N Book
```

- `Author.email` has a unique constraint — creating or updating an author
  with an email that already exists returns `409 Conflict`.
- `Book.author_id` is a foreign key to `Author.id` — creating or updating a
  book with a non-existent `author_id` returns `404 Not Found`.
- Deleting an author cascades and deletes their books
  (`cascade="all, delete-orphan"`).

## Notes on relationship loading

`Author.books` uses SQLAlchemy's default **lazy loading**: the related
books are only fetched from the database the first time `author.books` is
accessed. For an endpoint like `GET /authors/{id}/books` that always needs
the books, this means two queries are issued (one for the author, one for
the books) instead of one.

For better performance on read-heavy endpoints, this could be changed to
eager loading with `selectinload(Author.books)` (issues a second query but
avoids the N+1 problem when loading many authors at once) or
`joinedload(Author.books)` (a single query with a `JOIN`, better for
loading one author with its books). Both are worth exploring once you're
comfortable with the default lazy behavior.
