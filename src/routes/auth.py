"""
Authentication Routes Module
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail, TokenRefreshRequest
from src.services.auth import (
    create_access_token,
    get_email_from_token,
    create_email_token,
    verify_refresh_token,
    create_refresh_token,
)
from src.services.email_service import send_email
from src.services.users import UserService
from src.database.db import get_db
from src.services.utils.hash_helper import HashHelper
from src.services.utils.email_template_utils import EmailTemplatesUtils
from src.services.utils.str_to_email_str import str_to_email_str

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): The user data for registration.
        background_tasks (BackgroundTasks): Background tasks to send confirmation email.
        request (Request): The incoming request.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        User: The newly created user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User name already exists",
        )
    user_data.password = HashHelper().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    token_verification = create_email_token({"sub": new_user.email})
    email_template_utils = EmailTemplatesUtils()
    email_content = email_template_utils.get_verivy_email_content(
        username=new_user.username, host=request.base_url, token=token_verification
    )

    background_tasks.add_task(
        send_email, email=new_user.email, email_content=email_content
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data containing username and password.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not HashHelper().verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    await db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email address using a verification token.

    Args:
        token (str): The email verification token.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        dict: A message indicating email confirmation status.
    """
    email = await get_email_from_token(token)
    valid_email = str_to_email_str(email)

    user_service = UserService(db)
    user = await user_service.get_user_by_email(valid_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(valid_email)
    return {"message": "Email confirmed successfully"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a new email confirmation link.

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

    if user.confirmed:
        return {"message": "Email already confirmed"}
    if user:
        token_verification = create_email_token({"sub": user.email})
        email_template_utils = EmailTemplatesUtils()
        email_content = email_template_utils.get_verivy_email_content(
            username=user.username, host=request.base_url, token=token_verification
        )

        background_tasks.add_task(
            send_email, email=user.email, email_content=email_content
        )
    return {"message": "Check your email for confirm registration"}