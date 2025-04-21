"""
Database Models Module
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Integer,
    String,
    func,
    ForeignKey,
    Column,
    Boolean,
)
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models.

    This class serves as the base class for all models in the application, providing
    the foundational functionality needed for ORM mappings.
    """

    pass


class Contact(Base):
    """
    Contact model for storing contact information.

    Represents a contact record that contains personal information about an individual.
    It includes fields like first name, last name, email, phone number, and birthdate.

    Attributes:
        id (int): The unique identifier for each contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        birth_date (datetime): The birthdate of the contact (optional).
        additional (str): Any additional information about the contact (optional).
        created_at (datetime): The timestamp when the contact was created.
        updated_at (datetime): The timestamp when the contact was last updated.
        user_id (int): The foreign key to the user associated with the contact.
        user (User): The relationship to the User model.
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[DateTime] = mapped_column("birth_date", DateTime, nullable=True)
    additional: Mapped[str] = mapped_column(String(250), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    user_id = Column("user_id", ForeignKey("users.id"), default=None)
    user = relationship("User", backref="contacts")


class UserRole(str, Enum):
    """Enumeration of user roles.

    Attributes:
        USER (str): Regular user role.
        ADMIN (str): Administrator role.
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model for storing user information.

    Represents a user record, including their username, email, hashed password, and account details.

    Attributes:
        id (int): The unique identifier for each user.
        username (str): The unique username for the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password for user authentication.
        created_at (datetime): The timestamp when the user account was created.
        avatar (str): The URL or path to the user's avatar image (optional).
        confirmed (bool): Whether the user’s email is confirmed (default is False).
        role (UserRole): user role.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String(10), default="user")
    refresh_token = Column(String(255), nullable=True)