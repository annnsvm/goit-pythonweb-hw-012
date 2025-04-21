"""Utility module for rendering email templates using Jinja2.

This module provides helper methods to render verification and password
reset email content with dynamic values using Jinja2 templates stored
in the 'templates' directory.
"""

from pathlib import Path
from jinja2 import FileSystemLoader, Environment, Template
from sqlalchemy import URL


class EmailTemplatesUtils:
    """Utility class for generating HTML content from email templates."""

    def __init__(self):
        """Initializes the Jinja2 environment with the template's directory."""
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent / "templates")
        )

    def get_verivy_email_content(self, username: str, host: URL, token: str) -> str:
        """Renders the verify email template with the provided parameters.

        Args:
            username (str): The name of the user.
            host (URL): The host address to include in the email.
            token (str): The verification token to include in the email.

        Returns:
            str: Rendered HTML content of the verify email.
        """
        template = self.__get_verivy_email_template()
        return template.render(username=username, host=host, token=token)

    def __get_verivy_email_template(self) -> Template:
        """Retrieves the verify email Jinja2 template.

        Returns:
            Template: The Jinja2 template object for the verify email.
        """
        return self.env.get_template("verify_email.html")

    def get_reset_password_email_content(
        self, username: str, host: URL, token: str
    ) -> str:
        """Renders the reset password email template with the provided parameters.

        Args:
            username (str): The name of the user.
            host (URL): The host address to include in the email.
            token (str): The reset password token to include in the email.

        Returns:
            str: Rendered HTML content of the reset password email.
        """
        template = self.__get_verivy_email_template()
        return template.render(username=username, host=host, token=token)

    def __get_reset_password_email_template(self) -> Template:
        """Retrieves the reset password email Jinja2 template.

        Returns:
            Template: The Jinja2 template object for the reset password email.
        """
        return self.env.get_template("reset_password_email.html")