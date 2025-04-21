"""
Database Sessions Manager Module
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages database sessions using SQLAlchemy's async API.

    This class is responsible for creating and managing database sessions, ensuring
    proper session initialization, committing, and rolling back in case of errors.

    Attributes:
        _engine (AsyncEngine | None): The asynchronous engine used to connect to the database.
        _session_maker (async_sessionmaker): A factory function to create new database sessions.
    """

    def __init__(self, url: str):
        """
        Initializes the DatabaseSessionManager with a database connection URL.

        Args:
            url (str): The database URL used to create the asynchronous engine.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides an asynchronous context manager for creating a database session.

        This method ensures that a database session is created, and handles
        rolling back the session in case of an SQLAlchemyError. The session
        is closed automatically when done.

        Yields:
            AsyncSession: A database session object.

        Raises:

            SQLAlchemyError: If an error occurs during the transaction, it will
                be caught, rolled back, and re-raised.

            Exception: If the session maker is not initialized.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session