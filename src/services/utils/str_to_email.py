from pydantic import TypeAdapter, EmailStr


def str_to_email_str(email: str) -> EmailStr:
    """
    Converting email string to the EmailStr pydantic class
    Args:
        email: (str) email user

    Returns:
        EmailStr: A pydantic class
    """
    email_adapter = TypeAdapter(EmailStr)
    return email_adapter.validate_python(email)