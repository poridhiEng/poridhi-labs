# Database Integration with FastAPI


This guide walks you through the process of integrating FastAPI with SQLModel to create a simple RESTful API. FastAPI is a modern Python web framework for building APIs quickly and efficiently, while SQLModel simplifies working with SQL databases using Python classes.


## Overview of the Project
We will create a Bookstore API that allows users to perform CRUD operations (Create, Read, Update, Delete) on a database of books. The project includes features like:

- Defining a database schema using SQLModel.
- Exposing RESTful API endpoints using FastAPI.
- Managing a SQLite database (default) with flexibility for other databases via environment variables.

## **Step 1: Set Up the Environment**

**1. Create a folder for the project**:

Create a folder for the project:

```bash
mkdir fastapi-sqlmodel-app
cd fastapi-sqlmodel-app
```

**3. Install required libraries**:

```bash
pip install fastapi uvicorn sqlmodel mysql-connector-python sqlalchemy
```

**4. Create a `requirements.txt` file**:

Create a `requirements.txt` file and add the following dependencies:

```text
fastapi>=0.68.0
sqlmodel>=0.0.8
uvicorn>=0.15.0
python-dotenv>=0.19.0
```
Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## **Step 2: Directory Structure**
    
Create the following file structure for the project:

```
fastapi-sqlmodel-app/
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── api.py
│   └── main.py
│
├── .env
├── requirements.txt
└── README.md
```

## **Step 3: Database Configuration**

### **`database.py`**

This file manages the database connection, table creation, and session dependency.

```python
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

# Load database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

# Create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency for session
def get_session():
    with Session(engine) as session:
        yield session
```

## **Step 4: Define Models**

### **`models.py`**
Models define the structure of the database tables.

```python
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    price: float
    in_stock: bool = True
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Book(BookBase, table=True):  # Represents a table
    id: Optional[int] = Field(default=None, primary_key=True)

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
```

---

## **Step 5: Define Schemas**

### **`schemas.py`**
Schemas specify the request and response formats for API operations.

```python
from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class BookCreate(SQLModel):
    title: str
    author: str
    year: int
    price: float
    in_stock: bool = True
    description: Optional[str] = None

class BookRead(SQLModel):
    id: int
    title: str
    author: str
    year: int
    price: float
    in_stock: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    description: Optional[str] = None

class BookSearchResults(SQLModel):
    results: List[BookRead]
    total: int
    page: int
    size: int
```

---

## **Step 6: CRUD Operations**

### **`crud.py`**
Handles all database operations (Create, Read, Update, Delete).

```python
from sqlmodel import Session, select
from typing import List, Optional
from .models import Book
from .schemas import BookCreate, BookUpdate, BookSearchResults

def create_book(session: Session, book: BookCreate) -> Book:
    db_book = Book.from_orm(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

def get_book(session: Session, book_id: int) -> Optional[Book]:
    return session.get(Book, book_id)

def get_books(session: Session, offset: int = 0, limit: int = 10) -> List[Book]:
    return session.exec(select(Book).offset(offset).limit(limit)).all()

def update_book(session: Session, book_id: int, book_data: BookUpdate) -> Optional[Book]:
    db_book = session.get(Book, book_id)
    if not db_book:
        return None
    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    db_book.update_timestamp()
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

def delete_book(session: Session, book_id: int) -> bool:
    db_book = session.get(Book, book_id)
    if not db_book:
        return False
    session.delete(db_book)
    session.commit()
    return True
```

---

## **Step 7: API Router**

### **`api.py`**
Defines the API routes and binds them to the CRUD operations.

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from .crud import create_book, get_books, get_book, update_book, delete_book
from .schemas import BookCreate, BookRead, BookUpdate, BookSearchResults
from .database import get_session

router = APIRouter()

@router.post("/books/", response_model=BookRead)
def create(book: BookCreate, session: Session = Depends(get_session)):
    return create_book(session, book)

@router.get("/books/", response_model=List[BookRead])
def read_all(offset: int = 0, limit: int = Query(default=10, le=100), session: Session = Depends(get_session)):
    return get_books(session, offset, limit)

@router.get("/books/{book_id}", response_model=BookRead)
def read(book_id: int, session: Session = Depends(get_session)):
    book = get_book(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/books/{book_id}", response_model=BookRead)
def update(book_id: int, book_data: BookUpdate, session: Session = Depends(get_session)):
    book = update_book(session, book_id, book_data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.delete("/books/{book_id}")
def delete(book_id: int, session: Session = Depends(get_session)):
    if not delete_book(session, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
```

---

## **Step 8: Main Application**

### **`main.py`**
Starts the FastAPI application.

```python
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api import router

app = FastAPI(root_path="ROOT_PATH", title="BookStore API", version="1.0.0")

# Define a route for "/"
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(router, prefix="/api/v1")
```

## **Step 9: Environment Variables**

Create a `.env` file and add the following variables:

```
DATABASE_URL=<DATABASE_URL>
ROOT_PATH=<ROOT_PATH>
```
>NOTE: Replace `<DATABASE_URL>` and `<ROOT_PATH>` with your own values.

## Database Setup

For database integration, running MySQL as a Docker container can simplify your development process and keep your database environment consistent.

**Start a MySQL container using the command below:**

```bash
docker run --name fastapi-mysql \
-e MYSQL_ROOT_PASSWORD=<your_root_password> \
-e MYSQL_DATABASE=fastapi_db \
-p 3306:3306 \
-v mysql_data:/var/lib/mysql \
-d mysql:latest
```

>NOTE: Replace `your_root_password` with your own password.

**Check the container status using the command below:**

```bash
docker ps
```

## Running the Application**

Run the application using `uvicorn`:
```bash
uvicorn app.main:app --reload
```


