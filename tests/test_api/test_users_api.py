from builtins import str
import pytest
import app.routers.user_routes as user_routes
from app.routers.user_routes import upgrade_to_pro, update_my_profile
from uuid import uuid4
from httpx import AsyncClient
from fastapi import HTTPException
import app.routers.user_routes as ur_mod
from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.schemas.user_schemas import UserProfileDTO, UserProfileUpdate
from app.main import app
from datetime import datetime
from app.models.user_model import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.nickname_gen import generate_nickname
from app.utils.security import hash_password
from app.services.jwt_service import decode_token  # Import your FastAPI app

# Example of a test function using the async_client fixture
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client, user_token, email_service):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Define user data for the test
    user_data = {
        "nickname": generate_nickname(),
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }
    # Send a POST request to create a user
    response = await async_client.post("/users/", json=user_data, headers=headers)
    # Asserts
    assert response.status_code == 403

# You can similarly refactor other test functions to use the async_client fixture
@pytest.mark.asyncio
async def test_retrieve_user_access_denied(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_retrieve_user_access_allowed(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(admin_user.id)

@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client, verified_user, user_token):
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client, admin_user, admin_token):
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]


@pytest.mark.asyncio
async def test_delete_user(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{admin_user.id}", headers=headers)
    assert delete_response.status_code == 204
    # Verify the user is deleted
    fetch_response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert fetch_response.status_code == 404

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client, verified_user):
    user_data = {
        "email": verified_user.email,
        "password": "AnotherPassword123!",
        "role": UserRole.ADMIN.name
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "Email already exists" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_create_user_invalid_email(async_client):
    user_data = {
        "email": "notanemail",
        "password": "ValidPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422

import pytest
from app.services.jwt_service import decode_token
from urllib.parse import urlencode

@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    # Attempt to login with the test user
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # Check for successful login response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Use the decode_token method from jwt_service to decode the JWT
    decoded_token = decode_token(data["access_token"])
    assert decoded_token is not None, "Failed to decode token"
    assert decoded_token["role"] == "AUTHENTICATED", "The user role should be AUTHENTICATED"

@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    form_data = {
        "username": "nonexistentuser@here.edu",
        "password": "DoesNotMatter123!"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "IncorrectPassword123!"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_unverified_user(async_client, unverified_user):
    form_data = {
        "username": unverified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_locked_user(async_client, locked_user):
    form_data = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 400
    assert "Account locked due to too many failed login attempts." in response.json().get("detail", "")
@pytest.mark.asyncio
async def test_delete_user_does_not_exist(async_client, admin_token):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID format
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{non_existent_user_id}", headers=headers)
    assert delete_response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_github(async_client, admin_user, admin_token):
    updated_data = {"github_profile_url": "http://www.github.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["github_profile_url"] == updated_data["github_profile_url"]

@pytest.mark.asyncio
async def test_update_user_linkedin(async_client, admin_user, admin_token):
    updated_data = {"linkedin_profile_url": "http://www.linkedin.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["linkedin_profile_url"] == updated_data["linkedin_profile_url"]

@pytest.mark.asyncio
async def test_list_users_as_admin(async_client, admin_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert 'items' in response.json()

@pytest.mark.asyncio
async def test_list_users_as_manager(async_client, manager_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, user_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403  # Forbidden, as expected for regular user


@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient, admin_token: str):
    """
    When fetching a non‐existent user, the endpoint should return 404.
    This covers the `if not user: raise HTTPException(404)` branch.
    """
    random_id = uuid4()
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get(f"/users/{random_id}", headers=headers)

    assert resp.status_code == 404
    assert resp.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_get_user_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_token: str
):
    """
    When fetching an existing user, the endpoint should return 200 and a payload
    matching the UserResponse schema. This covers the return‐path of model_construct.
    """
    # 1) Seed a user into the database
    user = User(
        id=uuid4(),
        nickname=generate_nickname(),
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.AUTHENTICATED,
        email_verified=True,
        is_locked=False
    )
    db_session.add(user)
    await db_session.commit()

    # 2) Perform the GET request as an admin
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get(f"/users/{user.id}", headers=headers)
    assert resp.status_code == 200

    data = resp.json()

    # 3) The response should include exactly the fields defined in UserResponse
    expected_keys = {
        "id",
        "email",
        "nickname",
        "first_name",
        "last_name",
        "bio",
        "profile_picture_url",
        "linkedin_profile_url",
        "github_profile_url",
        "role",
        "is_professional",
    }
    assert expected_keys.issubset(data.keys())

    # 4) Validate field values
    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["nickname"] == user.nickname
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name

    # Optional fields default to None
    assert data["bio"] is None
    assert data["profile_picture_url"] is None
    assert data["linkedin_profile_url"] is None
    assert data["github_profile_url"] is None

    # Enum and boolean fieldss
    assert data["role"] == user.role.name
    assert data["is_professional"] is False


@pytest.mark.asyncio
async def test_update_user_not_found(async_client: AsyncClient, admin_token: str):
    """
    When updating a non‐existent user, the endpoint should return 404.
    Covers the `if not updated_user: raise HTTPException(404)` branch.
    """
    random_id = uuid4()
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"first_name": "Foo"}
    resp = await async_client.put(f"/users/{random_id}", json=payload, headers=headers)

    assert resp.status_code == 404
    assert resp.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_update_user_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_token: str
):
    """
    When updating an existing user, the endpoint should return 200 and reflect
    the changes in both the response payload and the database.
    """
    # 1) Seed a user into the database
    user = User(
        id=uuid4(),
        nickname=generate_nickname(),
        first_name="OldFirst",
        last_name="OldLast",
        email="update_test@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.AUTHENTICATED,
        email_verified=True,
        is_locked=False
    )
    db_session.add(user)
    await db_session.commit()

    # 2) Perform the PUT request as an admin
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "first_name": "NewFirst",
        "last_name": "NewLast"
    }
    resp = await async_client.put(f"/users/{user.id}", json=payload, headers=headers)
    assert resp.status_code == 200

    data = resp.json()

    # 3) The response should include exactly the fields defined in UserResponse
    expected_keys = {
        "id",
        "email",
        "nickname",
        "first_name",
        "last_name",
        "bio",
        "profile_picture_url",
        "linkedin_profile_url",
        "github_profile_url",
        "role",
        "is_professional",
    }
    assert expected_keys.issubset(data.keys())

    # 4) Validate that the updated fields match the payload
    assert data["first_name"] == "NewFirst"
    assert data["last_name"] == "NewLast"

    # 5) Validate that unchanged fields are preserved
    assert data["email"] == user.email
    assert data["nickname"] == user.nickname
    assert data["role"] == user.role.name

    # Optional fields default to None
    assert data["bio"] is None
    assert data["profile_picture_url"] is None
    assert data["linkedin_profile_url"] is None
    assert data["github_profile_url"] is None

    # 6) Confirm the changes persisted to the database
    refreshed = await db_session.get(User, user.id)
    assert refreshed.first_name == "NewFirst"
    assert refreshed.last_name == "NewLast"

@pytest.mark.asyncio
async def test_login_locked_account(
    async_client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch
):
    """
    If the account is locked, login should return 400 with the appropriate detail.
    Covers the `if await UserService.is_account_locked(...)` branch.
    """
    # 1) Patch is_account_locked → Truee
    async def fake_is_locked(session, username):
        return True

    monkeypatch.setattr(UserService, "is_account_locked", fake_is_locked)

    # 2) Attempt login
    resp = await async_client.post(
        "/login/",
        data={"username": "locked@example.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": "Account locked due to too many failed login attempts."}


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, db_session: AsyncSession, monkeypatch):
    """
    If credentials are valid, login should return a bearer token.
    Covers the path where is_account_locked → False and login_user returns a user.
    """
    # 1) Patch is_account_locked → False
    async def fake_is_locked(session, username):
        return False
    monkeypatch.setattr(UserService, "is_account_locked", fake_is_locked)

    # 2) Patch login_user → return dummy user with id and role
    class DummyUser:
        id = uuid4()
        role = UserRole.AUTHENTICATED
    async def fake_login_user(session, username, password):
        return DummyUser()
    monkeypatch.setattr(UserService, "login_user", fake_login_user)

    # 3) Patch create_access_token in the router module so we get a predictable token
    import app.routers.user_routes as ur_mod
    monkeypatch.setattr(
        ur_mod,
        "create_access_token",
        lambda data, expires_delta: "fake-jwt-token"
    )

    # 4) Perform login requestt
    resp = await async_client.post(
        "/login/",
        data={"username": "user@example.com", "password": "ValidPass!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"access_token": "fake-jwt-token", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient, db_session: AsyncSession, monkeypatch):
    """
    If credentials are invalid (login_user returns None), login should return 401.
    Covers the final `raise HTTPException(status_code=401)` branch.
    """
    # 1) Patch is_account_locked → False
    async def fake_is_locked(session, username):
        return False
    monkeypatch.setattr(UserService, "is_account_locked", fake_is_locked)

    # 2) Patch login_user → None
    async def fake_login_user(session, username, password):
        return None
    monkeypatch.setattr(UserService, "login_user", fake_login_user)

    # 3) Attempt login with bad creds
    resp = await async_client.post(
        "/login/",
        data={"username": "doesnotexist@example.com", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Incorrect email or password."}

@pytest.mark.asyncio
async def test_get_my_profile_returns_current_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
    user_token: str
):
    """
    The /me endpoint should return whatever `get_current_user` yields.
    Covers the single `return current_user` line.
    """
    # Seed a user in the DB so it has attributes
    test_user = User(
        id=uuid4(),
        nickname="profile_test",
        first_name="Profile",
        last_name="User",
        email="profile@example.com",
        hashed_password="irrelevant",
        role=UserRole.AUTHENTICATED,
        email_verified=True,
        is_locked=False,
        is_professional=False,
    )
    db_session.add(test_user)
    await db_session.commit()

    # Override the dependency to return our test_user
    app.dependency_overrides[get_current_user] = lambda: test_user

    # Call the endpoint (header doesn’t matter because we’ve overridden the dependency)
    resp = await async_client.get("/me")
    assert resp.status_code == 200

    data = resp.json()
    # Verify all UserProfileDTO fields
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email
    assert data["nickname"] == test_user.nickname
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name

    # Optional fields default to None
    assert data["bio"] is None
    assert data["profile_picture_url"] is None
    assert data["linkedin_profile_url"] is None
    assert data["github_profile_url"] is None

    # Role and professional status
    assert data["role"] == test_user.role.name
    assert data["is_professional"] is False
    assert data["professional_status_updated_at"] is None

    # Cleanupp
    app.dependency_overrides.pop(get_current_user)

@pytest.mark.asyncio
async def test_upgrade_to_pro_insufficient_privileges(db_session: AsyncSession, user):
    """
    Non-Admin/Manager user should hit the first HTTPException(403).
    """
    with pytest.raises(HTTPException) as exc_info:
        await upgrade_to_pro(uuid4(), db_session, user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient privileges"

@pytest.mark.asyncio
async def test_upgrade_to_pro_user_not_found(db_session: AsyncSession, admin_user):
    """
    Admin role but no matching user in DB → HTTPException(404).
    """
    missing_id = uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await upgrade_to_pro(missing_id, db_session, admin_user)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_upgrade_to_pro_success(db_session: AsyncSession, manager_user, monkeypatch):
    """
    Manager role + existing user → flips is_professional, sets timestamp, and returns success dict.
    """
    # Freeze datetime.utcnow()
    fixed_time = datetime(2025, 5, 4, 12, 0, 0)
    FakeDatetime = type("FakeDatetime", (), {"utcnow": staticmethod(lambda: fixed_time)})
    monkeypatch.setattr(user_routes, "datetime", FakeDatetime)

#     # Seed a target user with is_professional=False
#     target = User(
#         id=uuid4(),
#         nickname=generate_nickname(),
#         first_name="T",
#         last_name="U",
#         email="target@example.com",
#         hashed_password=hash_password("pass"),
#         role=UserRole.AUTHENTICATED,
#         email_verified=True,
#         is_locked=False,
#         is_professional=False
#     )
#     db_session.add(target)
#     await db_session.commit()

#     # Call the function directly
#     result = await upgrade_to_pro(target.id, db_session, manager_user)
#     assert result == {"message": "Upgraded to professional status"}

#     # Verify DB changes
#     refreshed = await db_session.get(User, target.id)
#     assert refreshed.is_professional is True
#     assert refreshed.professional_status_updated_at == fixed_time

# @pytest.mark.asyncio
# async def test_update_my_profile_direct_no_fields(db_session: AsyncSession, user: User):
#     """
#     If no fields are provided, the root_validator should raise ValueError
#     before entering the function body.
#     """
#     # Persist the user so refresh() inside the function can run if body were entered
#     db_session.add(user)
#     await db_session.commit()

#     with pytest.raises(ValueError) as exc:
#         await update_my_profile(UserProfileUpdate(), db_session, user)
#     assert "At least one field" in str(exc.value)

# @pytest.mark.asyncio
# async def test_userprofileupdate_root_validator():
#     # Constructing with no fields should trigger the root_validator
#     with pytest.raises(ValueError) as exc:
#         UserProfileUpdate()  # no fields provided
#     assert "At least one field" in str(exc.value)

# @pytest.mark.asyncio
# async def test_update_my_profile_direct_success(
#     db_session: AsyncSession,
#     manager_user: User,
#     monkeypatch
# ):
#     """
#     Manager role + valid updates should hit every line:
#     - loop over fields + setattr
#     - db.add, commit, refresh
#     - return current_user
#     """
#     # 1) Freeze datetime.utcnow() to a fixed value
#     fixed_time = datetime(2025, 5, 4, 12, 0, 0)
#     FakeDT = type("FakeDT", (), {"utcnow": staticmethod(lambda: fixed_time)})
#     monkeypatch.setattr(user_routes, "datetime", FakeDT)

#     # 2) Persist the current_user so db.refresh() can operate
#     db_session.add(manager_user)
#     await db_session.commit()

#     # 3) Provide all required fields to the DTO
#     updates = UserProfileUpdate(
#         first_name="UpdatedFirst",
#         last_name=None,
#         bio="New bio",
#         profile_picture_url=None,
#         linkedin_profile_url=None,
#         github_profile_url=None,
#     )

#     # 4) Call the function directly
#     result = await update_my_profile(updates, db_session, manager_user)

#     # 5) It should return the same User instance with updated attrs
#     assert isinstance(result, User)
#     assert result.first_name == "UpdatedFirst"
#     assert result.bio == "New bio"

#     # 6) Confirm DB was updated and refresh() happened
#     refreshed = await db_session.get(User, manager_user.id)
#     assert refreshed.first_name == "UpdatedFirst"
#     assert refreshed.bio == "New bio"