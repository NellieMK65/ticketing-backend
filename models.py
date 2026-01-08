from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import phonenumbers
import re
from datetime import datetime

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)

# 2. create an instance of flask sqlalchemy and connect it to sqlalchemy
db = SQLAlchemy(metadata=metadata)

"""
Validations
-> Data Integrity - correctness of the data

-> We have frontend validation using tools like zod, yup
-> In the backend we will also add validations at the model level and controller(routes) level
-> In the database layer, we leverage db constraints (not null, unique, and other custom ones)

"""

# model the tables
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False, unique=True)
    email = db.Column(db.Text(), nullable=False, unique=True)
    role = db.Column(db.Enum("admin", "user"), default="user", nullable=False)
    password = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

    # serializer rules (these are used to negate specific properties)
    # serialize_rules = ("-updated_at",)

    @validates("email")
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Please provide a valid email")
        return email

    @validates("phone")
    def validate_phone(self, key, phone):
        # this supports only kenyan numbers
        # if len(phone) < 10 or len(phone) > 10: #07 or 01
        #     raise ValueError("Invalid phone number, can only contain 10 digits")
        # return phone

        # for kenyan numbers with the phone extension
        # if not re.match("^\+2547\d{8}$") or not re.match("^\+2541\d{8}$"):
        #     raise ValueError("Invalid kenyan phone number, must start with +254")

        # this supports global phone numbers
        parsed = phonenumbers.parse(phone, None) # +
        is_valid = phonenumbers.is_valid_number(parsed)

        if not is_valid:
            raise ValueError("Enter a valid phone number")
        elif "+" not in phone:
            raise ValueError("Must contain plus")

        return phone

    # manual serialization
    def to_json(self):
        return {"id": self.id, "name": self.name, "phone": self.phone}


class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Integer(), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

    # define relationships
    events = db.relationship("Event", back_populates="category")  # 1:*


class Event(db.Model, SerializerMixin):
    __tablename__ = "events"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    venue = db.Column(db.Text(), nullable=False)
    poster = db.Column(db.Text(), nullable=False)
    status = db.Column(
        db.Enum("cancelled", "postponed", "cancelled", "active", "completed"),
        default="active",
    )
    category_id = db.Column(
        db.Integer(), db.ForeignKey("categories.id"), nullable=False
    )
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

    # define the relationships
    category = db.relationship(
        "Category", back_populates="events", uselist=False
    )  # *:1

    tickets = db.relationship("Ticket", back_populates="event")

    @validates("start_date")
    def validate_start_date(self, key, date):
        d1 = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.date()

        if d1 < now:
            raise ValueError("Start date has to be of a future date")
        return date



class Ticket(db.Model, SerializerMixin):
    __tablename__ = "tickets"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    tickets_available = db.Column(db.Integer(), nullable=False)
    event_id = db.Column(db.Integer(), db.ForeignKey("events.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

    # relationships
    event = db.relationship("Event", back_populates="tickets", uselist=False)
    payments = db.relationship("Payment", back_populates="ticket")


class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer(), primary_key=True)
    mpesa_code = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    ticket_id = db.Column(db.Integer(), db.ForeignKey("tickets.id"), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now())

    # relationships
    ticket = db.relationship("Ticket", back_populates="payments", uselist=False)
