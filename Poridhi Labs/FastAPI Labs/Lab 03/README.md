# Database Integration with FastAPI in Kubernetes

This guide walks you through the process of integrating FastAPI with SQLModel to create a simple RESTful API. FastAPI is a modern Python web framework for building APIs quickly and efficiently, while SQLModel simplifies working with SQL databases using Python classes. This lab will also cover how to deploy the application in Kubernetes.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/banner.svg)


## Overview of the Project
We will create a Bookstore API that allows users to perform CRUD operations (Create, Read, Update, Delete) on a database of books. The project includes features like:

- Defining a database schema using SQLModel.
- Exposing RESTful API endpoints using FastAPI.
- Managing a SQLite database (default) with flexibility for other databases via environment variables.
- Deploying the application in Kubernetes.


## **Step 1: Set Up the Environment**

**Create a folder for the project**:

Create a folder for the project:

```bash
mkdir fastapi-sqlmodel-app
cd fastapi-sqlmodel-app
```

**Create a `requirements.txt` file**:

Create a `requirements.txt` file and add the following dependencies:

```text
annotated-types==0.7.0
anyio==4.5.2
cffi==1.17.1
click==8.1.7
cryptography==43.0.3
exceptiongroup==1.2.2
fastapi==0.115.5
greenlet==3.1.1
h11==0.14.0
idna==3.10
mysql-connector-python==9.0.0
pycparser==2.22
pydantic==2.10.1
pydantic-core==2.27.1
PyMySQL==1.1.1
python-dotenv==1.0.1
sniffio==1.3.1
SQLAlchemy==2.0.36
sqlmodel==0.0.22
starlette==0.41.3
typing-extensions==4.12.2
uvicorn==0.32.1
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
import os
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api import router
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get environment variables, with defaults if they don't exist
ROOT_PATH = os.getenv("ROOT_PATH", "/")  # Default root_path if not found
API_TITLE = os.getenv("API_TITLE", "BookStore API")  # Default title
API_VERSION = os.getenv("API_VERSION", "1.0.0")  # Default version

# Create the FastAPI app instance using environment variables
app = FastAPI(root_path=ROOT_PATH, title=API_TITLE, version=API_VERSION)

# Define a route for "/"
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.on_event("startup")
def on_startup():
    # Ensure the database and tables are created
    create_db_and_tables()

# Include the router for API versioning
app.include_router(router, prefix="/api/v1")
```

## **Step 9: Dockerize the Application**

First create a `Dockerfile` in the root directory of the project. Add the following code to the `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better cache utilization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app/ ./app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## **Step 10: Build and push the Docker Image**

```bash
docker build -t <your-docker-username>/fastapi-sqlmodel-app:latest .
docker push <your-docker-username>/fastapi-sqlmodel-app:latest
```

## **Step 11: Deploy the Application in Kubernetes**

First create a `manifests` folder in the root directory of the project.

**1. mysql-secret.yaml**

```bash
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
data:
  MYSQL_ROOT_PASSWORD: cm9vdA==  # base64 encoded 'root'
  MYSQL_DATABASE: ZmFzdGFwaV9kYg==       # base64 encoded 'fastapi_db'
```

**2. mysql-pv.yaml**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

**3. mysql-pvc.yaml**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

**4. mysql-deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_DATABASE
        volumeMounts:
        - name: mysql-persistent-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-persistent-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
```

**5. mysql-service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  clusterIP: None  # Headless service for MySQL
```

**6. fastapi-configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
data:
  API_TITLE: "BookStore API"
  API_VERSION: "1.0.0"
  DATABASE_URL: "mysql+pymysql://root:$(MYSQL_ROOT_PASSWORD)@mysql:3306/$(MYSQL_DATABASE)"
```

**7. fastapi-deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: <your-docker-username>/fastapi-sqlmodel-app:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fastapi-config
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

**8. fastapi-service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
  - port: 80
    targetPort: 8000
  type: NodePort
```

**Apply the Kubernetes Manifests**

```bash
kubectl apply -f manifests/
```

**Verify the Application**

```bash
kubectl get pods
kubectl get services
```

## **Step 12: Access the Application**

