"""
This module provides the ContactService class for managing contact-related operations.
"""

from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repositories.contacts import ContactRepository
from src.schemas import ContactBase


class ContactService:
    """
    Service class for handling contact-related operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize ContactService with a database session.

        Args:
            db (AsyncSession): The database session.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Create a new contact for the given user.

        Args:
            body (ContactBase): The contact data.
            user (User): The user associated with the contact.

        Returns:
            Contact: The created contact.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(
        self, skip: int, limit: int, user: User, q: str | None = None
    ) -> Sequence[Contact]:
        """
        Retrieve a list of contacts for the given user with optional search query.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            user (User): The user whose contacts are being retrieved.
            q (str | None, optional): A search query for filtering contacts.

        Returns:
            Sequence[Contact]: A list of contacts.
        """
        return await self.contact_repository.get_contacts(skip, limit, user, q)

    async def get_contact(self, contact_id: int, user: User) -> Contact:
        """
        Retrieve a contact by its ID.

        Args:
            contact_id (int): The ID of the contact.
            user (User): The user who owns the contact.

        Returns:
            Contact: The retrieved contact.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def remove_contact_by_id(self, contact_id: int, user: User) -> Contact:
        """
        Remove a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user who owns the contact.

        Returns:
            Contact: The removed contact.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Update a contact's details.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The updated contact data.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The updated contact or None if not found.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def birthday_reminder(self, user: User) -> Sequence[Contact]:
        """
        Retrieve contacts with upcoming birthdays within the next 7 days.

        Args:
            user (User): The user whose contacts are being checked.

        Returns:
            Sequence[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self.contact_repository.birthday_reminder(user)