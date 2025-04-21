from passlib.context import CryptContext


class HashHelper:
    """
    Hashing utilities for password encryption and verification.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The raw password input by the user.
            hashed_password (str): The stored hashed password.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a plain password.

        Args:
            password (str): The raw password input by the user.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)