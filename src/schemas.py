"""
Module for Pydantic models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactBase(BaseModel):
    """
    Base model for creating and validating contact data.

    This class is used for creating or validating the basic information for a contact,
    such as first name, last name, email, phone number, birth date, and any additional information.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        birth_date (datetime): The birth date of the contact.
        additional (str): Additional information about the contact.
    """

    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=50)
    birth_date: Optional[datetime] = None
    additional: Optional[str] = Field(default=None, max_length=250)


class ContactResponse(ContactBase):
    """
    Model for representing a contact response.

    This class extends `ContactBase` and adds fields such as ID, created_at, and updated_at,
    which are typically returned in the response after the contact is created or fetched.

    Attributes:
        id (int): The unique identifier of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        birth_date (datetime): The birth date of the contact.
        additional (str): Additional information about the contact.
        created_at (datetime | None): The timestamp when the contact was created.
        updated_at (datetime | None): The timestamp when the contact was last updated.
    """

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: datetime
    additional: str
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class User(BaseModel):
    """
    Model for representing a user.

    This class defines the structure for user data such as the user ID, username, email, and avatar.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        avatar (str): The URL or path to the user's avatar.
        role (UserRole): The user role.
    """

    id: int
    username: str
    email: EmailStr
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserCreate(BaseModel):
    """
    Model for creating a new user.

    This class is used to validate data for creating a new user, including username, email, and password.

    Attributes:
        username (str): The username for the new user.
        email (EmailStr): The email address for the new user.
        password (str): The password for the new user.
        role (UserRole): The user role.
    """

    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Model for representing an authentication tokens.

    Attributes:
        access_token (str): The actual access token.
        refresh_token (str): The actual refresh token.
        token_type (str): The type of the token (e.g., "bearer").
    """

    access_token: str
    refresh_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Model for representing a request to send an email.

    This class is used to validate the email address when making a request for actions like password reset
    or verification.

    Attributes:
        email (EmailStr): The email address of the user.
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Model for representing a request to reset password.

    Attributes:
        token (Str): The token.
        new_password (Str): The new user password.
    """

    token: str
    new_password: str


class TokenRefreshRequest(BaseModel):
    """
    Model for representing a refresh token.

    Attributes:
        refresh_token (Str): The actual refresh token.
    """

    refresh_token: str