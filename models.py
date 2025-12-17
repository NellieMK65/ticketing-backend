from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)

# 2. create an instance of flask sqlalchemy and connect it to sqlalchemy
db = SQLAlchemy(metadata=metadata)

# model the tables
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False, unique=True)
    email = db.Column(db.Text(), nullable=False, unique=True)
    role = db.Column(db.Enum("admin", "user"), default="user", nullable=False)
    # password_hash = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Integer(), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    venue = db.Column(db.Text(), nullable=False)
    poster = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Enum("cancelled", "postponed", "cancelled", "active", "completed"), default="active")
    category_id = db.Column(db.Integer(), db.ForeignKey("categories.id"), nullable=False)
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    tickets_available = db.Column(db.Integer(), nullable=False)
    event_id = db.Column(db.Integer(), db.ForeignKey("events.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer(), primary_key=True)
    mpesa_code = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    ticket_id = db.Column(db.Integer(), db.ForeignKey("tickets.id"), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())
