# Ticketing Application

A Flask-based backend API for a ticketing system with user authentication and authorization.

## Table of Contents

-   [Installation](#installation)
-   [Setup Guide](#setup-guide)
    -   [1. Flask + Flask-RESTful](#1-flask--flask-restful)
    -   [2. Flask-SQLAlchemy + Serializer](#2-flask-sqlalchemy--serializer)
    -   [3. Flask-Bcrypt + Flask-JWT-Extended](#3-flask-bcrypt--flask-jwt-extended)
-   [Running the Application](#running-the-application)
-   [API Endpoints](#api-endpoints)

## Installation

1. Clone the repository and navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies using Pipenv:

```bash
pipenv install
```

3. Activate the virtual environment:

```bash
pipenv shell
```

4. Create a `.env` file in the backend directory (make sure to include it in the .gitignore file):

```bash
touch .env
```

5. Add the following environment variables to `.env`:

```
JWT_SECRET_KEY=your-super-secret-key
```

You can generate random secure strings using `openssl rand -hex 32`

---

## Setup Guide

### 1. Flask + Flask-RESTful

Flask-RESTful is an extension for Flask that adds support for quickly building REST APIs.

#### Installation

```bash
pipenv install flask flask-restful
```

#### Configuration (app.py)

```python
from flask import Flask
from flask_restful import Api

app = Flask(__name__)

# Link Flask with Flask-RESTful
api = Api(app)
```

#### Creating Resources

Resources are the building blocks of Flask-RESTful. Each resource represents an endpoint.

```python
# routes/users.py
from flask_restful import Resource, reqparse

class UserResource(Resource):
    def get(self):
        # Handle GET requests
        return {"message": "Get all users"}

    def post(self):
        # Handle POST requests
        return {"message": "Create user"}
```

#### Using Request Parsers

Request parsers validate incoming request data:

```python
signup_parser = reqparse.RequestParser()
signup_parser.add_argument(
    "name", required=True, type=str, help="User name is required"
)
signup_parser.add_argument(
    "email", required=True, type=str, help="Email address is required"
)

class UserSignup(Resource):
    def post(self):
        data = signup_parser.parse_args()
        # data is now validated
        return {"name": data["name"], "email": data["email"]}
```

#### Registering Resources

```python
# app.py
from routes.users import UserResource, UserSignup

api.add_resource(UserResource, "/users")
api.add_resource(UserSignup, "/sign-up")
```

---

### 2. Flask-SQLAlchemy + Serializer

Flask-SQLAlchemy provides SQLAlchemy support for Flask, while SQLAlchemy-Serializer helps convert model instances to dictionaries/JSON.

#### Installation

```bash
pipenv install flask-sqlalchemy sqlalchemy-serializer flask-migrate
```

#### Database Configuration (app.py)

```python
from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_ECHO"] = True  # Enable query logging

# Initialize migrations
migrate = Migrate(app, db)

# Link database to Flask app
db.init_app(app)
```

#### Creating Models with Serializer (models.py)

```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy import MetaData

# Naming convention for constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)

db = SQLAlchemy(metadata=metadata)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())

    # Exclude password from serialization
    serialize_rules = ("-password",)

    # Model-level validation
    @validates("email")
    def validate_email(self, key, email):
        if "@" not in email:
            raise ValueError("Please provide a valid email")
        return email
```

#### Using the Serializer

```python
# Get all users and serialize
users = User.query.all()
result = [user.to_dict() for user in users]

# Serialize with specific rules
result = [user.to_dict(rules=("-updated_at", "-created_at")) for user in users]

# Serialize with only specific fields
result = [user.to_dict(only=("id", "name")) for user in users]
```

#### Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

---

### 3. Flask-Bcrypt + Flask-JWT-Extended

Flask-Bcrypt provides bcrypt hashing for passwords, and Flask-JWT-Extended adds JWT support for authentication.

#### Installation

```bash
pipenv install flask-bcrypt flask-jwt-extended dotenv
```

#### Configuration (app.py)

```python
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Link Flask with Bcrypt
bcrypt = Bcrypt(app)

# Link Flask with JWT
jwt = JWTManager(app)

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
# Optional: Set token expiration
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# timedelta can be imported from datetime package like "from datetime import timedelta"
```

#### Password Hashing

```python
from flask_bcrypt import generate_password_hash, check_password_hash

# Hash a password (during signup)
password = "user_password"
pw_hash = generate_password_hash(password).decode("utf-8")

# Verify a password (during login)
is_valid = check_password_hash(pw_hash, password)  # Returns True/False
```

#### User Signup with Password Hashing

```python
class UserSignup(Resource):
    def post(self):
        data = signup_parser.parse_args()

        # Hash the password
        pw_hash = generate_password_hash(data["password"]).decode("utf-8")

        # Remove plain text password
        del data["password"]

        # Create user with hashed password
        user = User(**data, password=pw_hash)

        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully"}, 201
```

#### Creating JWT Tokens (Login)

```python
from flask_jwt_extended import create_access_token

class LoginResource(Resource):
    def post(self):
        data = login_parser.parse_args()

        # Find user by email
        user = User.query.filter(User.email == data["email"]).first()

        if user is None:
            return {"message": "Invalid email or password"}, 401

        # Verify password
        if not check_password_hash(user.password, data["password"]):
            return {"message": "Invalid email or password"}, 401

        # Create JWT token with additional claims
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role}
        )

        return {
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token
        }
```

#### Protecting Routes with JWT

```python
from flask_jwt_extended import jwt_required, get_jwt

class UserResource(Resource):
    @jwt_required()  # This route requires a valid JWT
    def get(self):
        # Access JWT claims
        claims = get_jwt()
        role = claims["role"]

        # Check authorization
        if role != "admin":
            return {"message": "Unauthorized"}, 401

        users = User.query.all()
        return [user.to_dict() for user in users]
```

#### Making Authenticated Requests

Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

---

## Running the Application

1. Make sure you're in the virtual environment:

```bash
pipenv shell
```

2. Run the Flask development server:

```bash
flask run --debug
```

The API will be available at `http://localhost:5000`

---

## API Endpoints

| Method | Endpoint   | Description         | Auth Required |
| ------ | ---------- | ------------------- | ------------- |
| POST   | `/sign-up` | Register a new user | No            |
| POST   | `/login`   | Login user          | No            |
| GET    | `/users`   | Get all users       | Yes (JWT)     |
