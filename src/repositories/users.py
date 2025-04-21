"""
User Repository Module

This module provides a repository for managing user-related database operations.
"""

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate
from src.services.utils.hash_helper import HashHelper


class UserRepository:
    """
    Repository for handling user-related database operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the UserRepository with a database session.

        Args:
            session (AsyncSession): The async database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user if found, else None.
        """
        query = select(User).filter_by(id=user_id)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user if found, else None.
        """
        query = select(User).filter_by(username=username)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """
        Retrieves a user by their email.

        Args:
            email (EmailStr): The email of the user.

        Returns:
            User | None: The user if found, else None.
        """
        query = select(User).filter_by(email=email)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Creates a new user in the database.

        Args:
            body (UserCreate): The user data.
            avatar (str, optional): The user's avatar URL. Defaults to None.

        Returns:
            User: The created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: EmailStr) -> None:
        """
        Marks a user's email as confirmed.

        Args:
            email (EmailStr): The email of the user.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: EmailStr, url: str) -> User:
        """
        Updates a user's avatar URL.

        Args:
            email (EmailStr): The email of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user_by_id(self, user_id: int) -> User | None:
        """
        Delete a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user if deleted, else None.
        """
        user = await self.get_user_by_id(user_id=user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()

        return user

    async def change_password(self, email: EmailStr, new_password: str) -> User | None:
        user = await self.get_user_by_email(email)

        if user:
            user.hashed_password = HashHelper().get_password_hash(new_password)
            await self.db.commit()
            await self.db.refresh(user)
        return user