import io
from unittest.mock import Mock, patch, AsyncMock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.services.utils.str_to_email_str import str_to_email_str
from tests.conftest import TestingSessionLocal, test_admin_user

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/v1/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).filter_by(email=user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/v1/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    return data


@pytest.mark.asyncio
async def test_get_me(client):
    response = await test_login(client)
    token = response.get("access_token")
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200 or response.status_code == 405


@pytest.mark.asyncio
async def test_update_avatar(client):
    token_object = await test_login(client)
    token = token_object.get("access_token")

    with patch(
        "src.api.users.UserService.update_avatar_url", new_callable=AsyncMock
    ) as mock_update_avatar:
        mock_update_avatar.return_value = test_admin_user
        with patch(
            "src.api.users.UploadFileService.upload_file", new_callable=Mock
        ) as mock_upload:
            mock_upload.return_value = "https://fake-avatar-url.com/avatar.png"

            fake_file = io.BytesIO(b"avatar image data")
            fake_file.name = "avatar.png"

            response = client.patch(
                "/api/v1/users/avatar",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("avatar.png", fake_file, "image/png")},
            )
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_user_by_id(client):
    token_object = await test_login(client)
    token = token_object.get("access_token")

    with patch(
        "src.api.users.UserService.delete_user_by_id", new_callable=AsyncMock
    ) as mock_delete_user:
        mock_delete_user.return_value = test_admin_user
        response = client.delete(
            "api/v1/users/7", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_reset_password(client):
    with patch(
        "src.api.users.UserService.get_user_by_email", new_callable=AsyncMock
    ) as mock_get_user_by_email:
        mock_get_user_by_email.return_value = test_admin_user
        with patch(
            "src.api.users.EmailTemplatesUtils.get_reset_password_email_content",
            new_callable=Mock,
        ) as mock_get_email_content:
            mock_get_email_content.return_value = "Email content"

            response = client.post(
                "api/v1/users/request_reset_password",
                json={"email": str_to_email_str("deadpool@example.com")},
            )
            data = response.json()
            assert response.status_code == 200
            assert data["message"] == "Check your email for confirm registration."


@pytest.mark.asyncio
async def test_request_reset_password_wrong_email(client):
    with patch(
        "src.api.users.UserService.get_user_by_email", new_callable=AsyncMock
    ) as mock_get_user_by_email:
        mock_get_user_by_email.return_value = None

        response = client.post(
            "api/v1/users/request_reset_password",
            json={"email": str_to_email_str("deadpool@example.com")},
        )
        data = response.json()
        assert response.status_code == 401
        assert data["detail"] == "User not found or email is not confirmed"


def test_get_reset_password_form(client):
    token = "valid_token_for_agent007"

    with patch(
        "src.api.users.get_email_from_token", new_callable=AsyncMock
    ) as mock_get_email_from_token:
        mock_get_email_from_token.return_value = test_admin_user.email

        with patch(
            "src.services.auth.UserService.get_user_by_email", new_callable=AsyncMock
        ) as mock_get_user_by_email:
            mock_get_user_by_email.return_value = test_admin_user

            response = client.get("api/v1/users/reset_password/" + token)
            assert response.status_code == 200
            assert response.json() == {"message": "Show form for reset a password"}


@pytest.mark.asyncio
def test_reset_password(client):
    token = "valid_token_for_agent007"

    with patch(
        "src.api.users.get_email_from_token", new_callable=AsyncMock
    ) as mock_get_email_from_token:
        with patch(
            "src.api.users.UserService.get_user_by_email", new_callable=AsyncMock
        ) as mock_get_user_by_email:
            mock_get_user_by_email.return_value = test_admin_user

            with patch(
                "src.api.users.UserService.change_password", new_callable=AsyncMock
            ) as mock_change_password:
                mock_change_password.return_value = test_admin_user

                mock_get_email_from_token.return_value = test_admin_user.email
                response = client.patch(
                    "api/v1/users/reset_password/",
                    json={"token": token, "new_password": "new_password"},
                )

                assert response.status_code == 200
                assert response.json() == {
                    "message": test_admin_user.username
                    + ", your password was changed successfully!"
                }