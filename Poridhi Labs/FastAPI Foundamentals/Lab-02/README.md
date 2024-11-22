# **Database Integration with FastAPI using SQLModel**

This document provides a comprehensive guide on integrating SQLModel with FastAPI to build a fully functional Bookstore API. It explains all steps, from environment setup to implementing database interactions and deploying the application.


## **1. Setting Up the Environment**

### **Step 1: Create a Virtual Environment**
A virtual environment isolates your project dependencies. Use the following commands to create and activate it:

```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### **Step 2: Install Required Libraries**
Install the necessary libraries using `pip`:

```bash
# Install dependencies individually
pip install fastapi sqlmodel uvicorn python-dotenv
```

Alternatively, create a `requirements.txt` file (explained in Step 3) and install all dependencies at once:

```bash
# Install from requirements.txt
pip install -r requirements.txt
```


### **Step 3: Create a `requirements.txt` File**
List the required libraries with version specifications to ensure compatibility:

```txt
fastapi>=0.68.0
sqlmodel>=0.0.8
uvicorn>=0.15.0
python-dotenv>=0.19.0
```

## **2. Database Configuration**

### **Step 4: Create `database.py`**
This file handles database configuration, connections, and session management.

```python
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection string from .env
Database_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(Database_URL, echo=True)

# Create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to provide database sessions
def get_session():
    with Session(engine) as session:
        yield session
```

### Key Points:
- **Environment Variables:** Use `.env` for secure database connection strings.
- **`engine`:** Manages communication with the database.
- **`create_db_and_tables`:** Initializes database tables.
- **`get_session`:** Provides a session for database operations.


## **3. Define Models**

### **Step 5: Create `models.py`**
Define database models representing tables and their fields.

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

class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
```

### Key Points:
- **Base Model (`BookBase`):** Defines common fields across schemas.
- **Database Table (`Book`):** Inherits from `BookBase` and sets `table=True`.


## **4. Define Schemas**

### **Step 6: Create `schemas.py`**
Schemas define the shape of data for API requests and responses.

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

### Key Points:
- **`BookCreate`:** Used for creating books.
- **`BookRead`:** Used for fetching book details.
- **`BookUpdate`:** Handles partial updates.
- **`BookSearchResults`:** Encapsulates search results with pagination.


## **5. CRUD Operations**

### **Step 7: Create `crud.py`**
This file contains reusable functions for database interactions.

```python
from sqlmodel import Session, select
from typing import List, Optional
from . import models, schemas

def create_book(session: Session, book: schemas.BookCreate) -> models.Book:
    db_book = models.Book.from_orm(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

def get_book(session: Session, book_id: int) -> Optional[models.Book]:
    return session.get(models.Book, book_id)

def get_books(session: Session, offset: int = 0, limit: int = 10) -> List[models.Book]:
    return session.exec(select(models.Book).offset(offset).limit(limit)).all()

def update_book(session: Session, book_id: int, book_data: schemas.BookUpdate) -> Optional[models.Book]:
    db_book = session.get(models.Book, book_id)
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
    db_book = session.get(models.Book, book_id)
    if not db_book:
        return False
    session.delete(db_book)
    session.commit()
    return True
```

## **6. API Routes**

### **Step 8: Create `api.py`**
Defines API endpoints and integrates CRUD functions.

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from . import crud, schemas, database

router = APIRouter()

@router.post("/books/", response_model=schemas.BookRead)
def create_book(book: schemas.BookCreate, session: Session = Depends(database.get_session)):
    return crud.create_book(session, book)

@router.get("/books/", response_model=List[schemas.BookRead])
def list_books(offset: int = 0, limit: int = Query(default=10, le=100), session: Session = Depends(database.get_session)):
    return crud.get_books(session, offset, limit)

@router.get("/books/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, session: Session = Depends(database.get_session)):
    book = crud.get_book(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/books/{book_id}", response_model=schemas.BookRead)
def update_book(book_id: int, book_data: schemas.BookUpdate, session: Session = Depends(database.get_session)):
    book = crud.update_book(session, book_id, book_data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.delete("/books/{book_id}")
def delete_book(book_id: int, session: Session = Depends(database.get_session)):
    if not crud.delete_book(session, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
```

## **7. Application Entry Point**

### **Step 9: Create `main.py`**
Initializes the FastAPI application.

```python
from fastapi import FastAPI
from database import create_db_and_tables
from api import router

app = FastAPI(
    title="Bookstore API",
    description="An API for managing books using FastAPI and SQLModel",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

## **8. Run the Application**

### **Step 10: Start the Server**
Run the application using `uvicorn`:

```bash
uvicorn main:app --reload
```

## **Conclusion**
This guide illustrates how to build and integrate a database with FastAPI using SQLModel. The example creates a fully functional Bookstore API with features like CRUD operations, validation, and search functionality.