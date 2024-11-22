# Database Integration with FastAPI

This guide walks you through the process of integrating FastAPI with SQLModel to create a simple RESTful API. FastAPI is a modern Python web framework for building APIs quickly and efficiently, while SQLModel simplifies working with SQL databases using Python classes.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/banner.svg)


## Overview of the Project
We will create a Bookstore API that allows users to perform CRUD operations (Create, Read, Update, Delete) on a database of books. The project includes features like:

- Defining a database schema using SQLModel.
- Exposing RESTful API endpoints using FastAPI.
- Managing a SQLite database (default) with flexibility for other databases via environment variables.

## **Step 1: Set Up the Environment**

**Create a folder for the project**:

Create a folder for the project:

```bash
mkdir fastapi-sqlmodel-app
cd fastapi-sqlmodel-app
```

**Install required libraries**:

```bash
pip install fastapi uvicorn sqlmodel mysql-connector-python sqlalchemy
```

**Create a `requirements.txt` file**:

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

## **Step 9: Database Setup**

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

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-19.png)

## **Step 10: Environment Variables**

Create a `.env` file and add the following variables:

```
DATABASE_URL="mysql+pymysql://<user>:<password>@<host>:<port>/<database>"
ROOT_PATH="<ROOT_PATH>"
API_TITLE=My Custom API
API_VERSION=2.0.0
```

>NOTE: Replace `<ROOT_PATH>`, `<user>`, `<password>`, `<host>`, `<port>`, and `<database>` with your own values. The `<ROOT_PATH>` should be the URL of the load balancer.

## **Step 11: Running the Application**

**Run the application using `uvicorn`:**

```bash
uvicorn app.main:app --reload
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-18.png)

**Access the Application:**

This lab is intended to be run on **Poridhi Labs**. After running the application, the API server will be forwarded to a load balancer.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image.png)

**Update the `<ROOT_PATH>` in the `.env` file:**

Copy the URL of the load balancer and update the `<ROOT_PATH>` in the `.env` file.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-20.png)

Access the API using the provided URL.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-1.png)

## **Step 12: Testing the API**

To test your FastAPI application and its API endpoints, you can use **`curl` commands**, a tool like **Postman**, or the **Swagger UI (accessible via `<ROOT_PATH>/docs`)** . Here's how you can test the endpoints with `curl`:

### **1. List All Books**

**GET /api/v1/books/**  

Retrieve a list of all books in the database.

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/" -H "accept: application/json" | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-2.png)

>NOTE: The `jq` command is used to format the JSON response. If you don't have `jq` installed, install it using `sudo apt-get install jq` on Linux.

### **2. Create a New Book**

**POST /api/v1/books/**

Create a new book by sending a JSON payload.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/books/" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 1925,
  "price": 10.99,
  "in_stock": true,
  "description": "A novel set in the 1920s."
}' | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-3.png)

### **3. Get a Specific Book by ID**

**GET /api/v1/books/{book_id}**  
Replace `{book_id}` with the ID of the book you want to retrieve.

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/9" -H "accept: application/json" | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-4.png)

### **4. Update a Book**

**PUT /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book to update. Include only the fields you want to change in the payload.

```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/books/9" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{
  "price": 20.99,
  "in_stock": false
}' | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-5.png)

### **5. Delete a Book**

**DELETE /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book you want to delete.

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/books/9" -H "accept: application/json" | jq .
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-6.png)

### **6. Search and Paginate Books**

**GET /api/v1/books/?offset=0&limit=5**

Fetch a paginated list of books starting from the offset and limited to a number of records.

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/?offset=0&limit=5" -H "accept: application/json" | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-7.png)

### **Testing via Swagger UI**

To test the API endpoints using Swagger UI, follow these steps:

#### **Navigate to `<ROOT_PATH>/docs` in your browser.**

Replace `<ROOT_PATH>` with the URL of the load balancer.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-8.png)

Now use the interactive interface to explore and test the API endpoints.

**1. List All Books**

**GET /api/v1/books/**

Get a list of all books in the database. Click on the **Try it out** button and then **Execute** to see the response.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-9.png)

**Output:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-10.png)

### **2. Create a New Book**

**POST /api/v1/books/**

Create a new book by sending a JSON payload. Click on the **Try it out** button and then **Execute** to see the response.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-11.png)

**Output:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-12.png)

### **3. Get a Specific Book by ID**

**GET /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book you want to retrieve.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-13.png)

**Output:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-14.png)

Now, continue testing the other endpoints in a similar manner.

### **4. Update a Book**

**PUT /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book to update. Include only the fields you want to change in the payload.

### **5. Delete a Book**

**DELETE /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book you want to delete. Click on the **Try it out** button and then **Execute** to see the response.


## **Step 13: Verify the Database**

You can verify the database by checking the tables and records.

```bash
docker ps
docker exec -it <container_id> mysql -uroot -p
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-15.png)


After entering the password, you can check the tables and records.

```bash
show databases;
use fastapi_db;
show tables;
select * from book;
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/image-17.png)


## Conclusion

So we have successfully created a FastAPI application that integrates with a MySQL database using SQLModel. This setup allows you to perform CRUD operations on a database of books, and you can extend this foundation to build more complex APIs.
