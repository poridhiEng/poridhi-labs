# Database Integration with FastAPI in Kubernetes

This guide walks you through the process of integrating FastAPI with SQLModel to create a simple RESTful API. FastAPI is a modern Python web framework for building APIs quickly and efficiently, while SQLModel simplifies working with SQL databases using Python classes. This lab will also cover how to deploy the application in Kubernetes.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2002/images/banner.svg)


## Overview of the Project

We will create a Bookstore API that allows users to perform CRUD operations (Create, Read, Update, Delete) on a database of books. The project includes features like:

- Defining a database schema using SQLModel.
- Exposing RESTful API endpoints using FastAPI.
- Managing a SQLite database (default) with flexibility for other databases via environment variables.
- Deploying the application in Kubernetes.


### Kubernetes Deployment Architecture

![](./images/k8s.drawio.svg)


## Requirements

**Install pip**

To install pip for Python3, run:

```sh
sudo apt update
sudo apt install python3-pip
```

**Verify the installation**

Once installed, you can verify that pip is working by checking its version:

```sh
pip3 --version
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image.png)

## **Step 1: Set Up the Environment**

**Create a folder for the project**:

Create a folder for the project:

```bash
mkdir fastapi-sqlmodel-app
cd fastapi-sqlmodel-app
```

**Step 2: Directory Structure**
    
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
|-- manifests/
├── requirements.txt
```


**Commands to create the directories:**

```sh
# Create the root project directory
mkdir -p fastapi-sqlmodel-app/app

mkdir -p fastapi-sqlmodel-app/manifests

# Create the necessary Python files inside the 'app' directory
touch fastapi-sqlmodel-app/app/__init__.py
touch fastapi-sqlmodel-app/app/database.py
touch fastapi-sqlmodel-app/app/models.py
touch fastapi-sqlmodel-app/app/schemas.py
touch fastapi-sqlmodel-app/app/crud.py
touch fastapi-sqlmodel-app/app/api.py
touch fastapi-sqlmodel-app/app/main.py

# Create the requirements.txt file
touch fastapi-sqlmodel-app/requirements.txt
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

**Install dependencies using:**

```bash
pip install -r requirements.txt
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

API_TITLE = os.getenv("API_TITLE", "BookStore API")  # Default title
API_VERSION = os.getenv("API_VERSION", "1.0.0")  # Default version

# Create the FastAPI app instance using environment variables
app = FastAPI(title=API_TITLE, version=API_VERSION)

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
docker build -t <your-dockerhub-username>/<imageName>:<version> .
docker push <your-dockerhub-username>/<imageName>:<version>
```

## **Step 11: Deploy the Application in Kubernetes**

First create a `manifests` folder in the root directory of the project.

**1. mysql-secret.yaml**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
data:
  MYSQL_ROOT_PASSWORD: cm9vdA==  # base64 encoded 'root'
  MYSQL_DATABASE: ZmFzdGFwaV9kYg==       # base64 encoded 'fastapi_db'
```

> Use base64 encoded value of Password and Database Name

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
  DATABASE_URL: "mysql+pymysql://root:root@mysql:3306/fastapi_db"
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
        image: <your-docker-username>/<image_name>:<version>
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
kubectl apply -f manifests/*
```

**Verify the Application**

```bash
kubectl get all
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-1.png)

## **Step 12: Access the Application**

To access the FastAPI Application with `Poridhi's Loadbalancer`, use the following steps:

**1. Find the `eth0` IP address for the Poridhi's VM currently you are running by using the command:**

```sh
ifconfig
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-6.png)

**2. Go to Poridhi's LoadBalancer and Create a LoadBalancer with the `eht0` IP and port `Nodeport` of the FastAPI service Nodeport.**


You can get the FlaskAPI service Nodeport by running this command:

```sh
kubectl get svc
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-7.png)


**3. By using the Provided `URL` by LoadBalancer, you can access the FastAPI Application from any browser.**


## **Step 13: Testing the API**

To test your FastAPI application and its API endpoints, you can use **`curl` commands**, a tool like **Postman**, or the **Swagger UI**. Here's how you can test the endpoints with `curl`:

### **1. List All Books**

**GET /api/v1/books/**  

Retrieve a list of all books in the database.

```bash
curl -X GET "https://66dbf2e46722fdb9097e9eb5-lb-716.bm-east.lab.poridhi.io/api/v1/books/" -H "accept: application/json" | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-2.png)

>NOTE: The `jq` command is used to format the JSON response. If you don't have `jq` installed, install it using `sudo apt-get install jq` on Linux.

### **2. Create a New Book**

**POST /api/v1/books/**

Create a new book by sending a JSON payload.

```bash
curl -X POST "https://66dbf2e46722fdb9097e9eb5-lb-716.bm-east.lab.poridhi.io/api/v1/books/" \
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

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-3.png)



### **3. Get a Specific Book by ID**

**GET /api/v1/books/{book_id}**  
Replace `{book_id}` with the ID of the book you want to retrieve.

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/9" -H "accept: application/json" | jq .
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-4.png)

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

### **5. Delete a Book**

**DELETE /api/v1/books/{book_id}**

Replace `{book_id}` with the ID of the book you want to delete.

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/books/9" -H "accept: application/json" | jq .
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-5.png)


### **Testing via Swagger UI**

To test the API endpoints using Swagger UI, follow these steps:

#### **Navigate to Loadbalancer UI in your browser.**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/FastAPI%20Labs/Lab%2003/images/image-9.png)

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

Now, continue testing the other endpoints in a similar manner.

## Conclusion

So we have successfully created a FastAPI application and created a Docker Image. Then we have deployed the setup in Kubernetes. This setup allows you to perform CRUD operations on a database of books, and you can extend this foundation to build more complex APIs.
