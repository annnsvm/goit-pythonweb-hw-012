"""
Users router module
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
    File,
    UploadFile,
    HTTPException,
    status,
    BackgroundTasks,
)
from pydantic import EmailStr, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas import User, RequestEmail, ResetPassword
from src.services.auth import (
    get_current_user,
    get_current_admin_user,
    create_email_token,
    get_email_from_token,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.services.email_service import send_email
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.services.utils.email_template_utils import EmailTemplatesUtils
from src.services.utils.str_to_email import str_to_email_str

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 5 requests per minute"
)
@limiter.limit("50/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.

    Args:
        request (Request): The request object.
        user (User): The currently authenticated user.

    Returns:
        User: The authenticated user's information.
    """

    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the currently authenticated user with admin role.

    Args:
        file (UploadFile): The uploaded avatar file.
        user (User): The currently authenticated user with admin role.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user object with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.delete("/{user_id}", response_model=User)
async def delete_user_by_id(
    user_id: int,
    _: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user by ID.

    Args:
        user_id: The ID of the user to remove.
        db: Database session.
        _: The currently authenticated user.

    Returns:
        The removed user record if found, otherwise raises an HTTPException.
    """
    user_service = UserService(db)
    user = await user_service.delete_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/request_reset_password")
async def request_reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Requesting a password reset email.
    Only registered users can reset password.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): Background tasks to send the email.
        request (Request): The incoming request.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        dict: A message indicating the email confirmation request status.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        token_verification = create_email_token({"sub": user.email})
        email_template_utils = EmailTemplatesUtils()
        email_content = email_template_utils.get_reset_password_email_content(
            username=user.username, host=request.base_url, token=token_verification
        )

        background_tasks.add_task(
            send_email, email=user.email, email_content=email_content
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or email is not confirmed",
        )
    # url = f"{request.base_url}api/v1/users/reset_password/{token_verification}"
    return {"message": "Check your email for confirm registration."}


@router.get("/reset_password/{token}")
async def get_reset_password_form(token: str, db: AsyncSession = Depends(get_db)):
    """
    Show form for reset a user  password if confirmed a user's email address using a verification token.

    Args:
        token: The email verification token.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        dict: A message indicating show password reset form.

    """
    email = await get_email_from_token(token)
    email_adapter = TypeAdapter(EmailStr)
    valid_email = email_adapter.validate_python(email)

    user_service = UserService(db)
    user = await user_service.get_user_by_email(valid_email)

    if user and user.confirmed:
        return {"message": "Show form for reset a password"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found or email is not confirmed",
    )


@router.patch("/reset_password")
async def reset_password(
    body: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Routes for reset form

    Args:
        body: (ResetPassword) The token and a new user password
        db (AsyncSession, optional): The database session dependency.

    Returns:
        dict: A message indicating about a changing password.

    """
    user_service = UserService(db)
    email = await get_email_from_token(body.token)
    valid_email = str_to_email_str(email)
    user = await user_service.get_user_by_email(valid_email)

    if user and user.confirmed:
        changed_user = await user_service.change_password(
            email=user.email, new_password=body.new_password
        )
        if changed_user:
            return {
                "message": changed_user.username
                + ", your password was changed successfully!"
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or email is not confirmed",
        )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Incorrect user data",
    )