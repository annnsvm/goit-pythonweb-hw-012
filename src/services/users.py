"""
Module for user-related services.

This module provides services for creating, retrieving, and updating user data.
It interacts with the user repository to perform CRUD operations.
"""

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """
    Service for handling user-related operations.

    Responsible for processing requests related to users, such as creating a new user,
    retrieving users by their ID, email, or username, and updating the user's avatar URL.

    Attributes:
        repository (UserRepository): The repository for interacting with the user data.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService.

        Args:
            db (AsyncSession): An asynchronous session object to interact with the database.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user.

        This method attempts to generate a Gravatar avatar for the user based on their email.
        If avatar generation fails, it proceeds without an avatar.

        Args:
            body (UserCreate): The user data for the new user.

        Returns:
            The created user object from the repository.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            The user object corresponding to the given ID.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            The user object corresponding to the given username.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: EmailStr):
        """
        Retrieves a user by their email.

        Args:
            email (EmailStr): The email address of the user to retrieve.

        Returns:
            The user object corresponding to the given email.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: EmailStr):
        """
        Checks if the email is confirmed.

        Args:
            email (EmailStr): The email address to check.

        Returns:
            A boolean indicating whether the email is confirmed or not.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: EmailStr, url: str):
        """
        Updates the avatar URL of a user.

        Args:
            email (EmailStr): The email address of the user.
            url (str): The new avatar URL to set for the user.

        Returns:
            The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def delete_user_by_id(self, user_id: int):
        """
        Delete a user by their ID.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            The user object corresponding to the given ID.
        """
        return await self.repository.delete_user_by_id(user_id)

    async def change_password(self, email: EmailStr, new_password: str) -> User | None:
        return await self.repository.change_password(
            email=email, new_password=new_password
        )