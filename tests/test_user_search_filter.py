import pytest
import markdown2
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from httpx import AsyncClient
from app.services.email_service import EmailService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from app.main import app
from app.models.user_model import UserRole, User
from app.dependencies import get_db
from app.database import Database
from app.utils.nickname_gen import generate_nickname
from app.utils.security import hash_password
from pathlib import Path
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager

TEMPLATE_MODULE_PATH = "app.utils.template_manager"

@pytest.fixture
def client(async_client):
    return async_client

async def test_no_filters_returns_all(client, db_session, admin_token):
    # Arrange: insert 3 users directly into the test DB
    created_emails = []
    for i in range(3):
        u = User(
            nickname=generate_nickname(),
            first_name="Test",
            last_name="User",
            email=f"user{i}@example.com",
            hashed_password=hash_password("Secure*1234"),
            role=UserRole.AUTHENTICATED,
            email_verified=True,
            is_locked=False
        )
        db_session.add(u)
        created_emails.append(u.email)
    await db_session.commit()

    # Act: call the list‐users endpoint with admin auth
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await client.get("/users/", headers=headers)
    assert resp.status_code == 200

    data = resp.json()

    # Normalize the response payload into a users_list
    if isinstance(data, dict):
        if "items" in data:
            users_list = data["items"]
        elif "users" in data:
            users_list = data["users"]
        else:
            pytest.fail(f"Unexpected response format: {data!r}")
    elif isinstance(data, list):
        users_list = data
    else:
        pytest.fail(f"Unexpected response format: {data!r}")

    # Extract emails and assert we see all three
    emails = [u["email"] for u in users_list]
    for email in created_emails:
        assert email in emails

    assert len(users_list) >= 3

@pytest.mark.asyncio
async def test_filter_by_q_and_role_and_pro_status(client, db_session, admin_token):
    # Arrange: insert 2 ANONYMOUS users (only one pro) and 1 ADMIN
    anon_not_pro = User(
        nickname=generate_nickname(),
        first_name="Test",
        last_name="Anon",
        email="anon_not_pro@example.com",    # unique email
        hashed_password=hash_password("Secure*1234"),
        role=UserRole.ANONYMOUS,
        email_verified=True,
        is_locked=False,
        is_professional=False
    )
    anon_pro = User(
        nickname=generate_nickname(),
        first_name="Test",
        last_name="Anon",
        email="anon_pro@example.com",        # unique email
        hashed_password=hash_password("Secure*1234"),
        role=UserRole.ANONYMOUS,
        email_verified=True,
        is_locked=False,
        is_professional=True
    )
    admin = User(
        nickname=generate_nickname(),
        first_name="Admin",
        last_name="User",
        email="admin_search@example.com",    # unique email
        hashed_password=hash_password("Secure*1234"),
        role=UserRole.ADMIN,
        email_verified=True,
        is_locked=False,
        is_professional=True
    )

    db_session.add_all([anon_not_pro, anon_pro, admin])
    await db_session.commit()

    # Act: call the list‐users endpoint as admin with all three filters
    headers = {"Authorization": f"Bearer {admin_token}"}
    params = {
        "q": "anon",                         # matches both anon_not_pro & anon_pro
        "role": UserRole.ANONYMOUS.name,
        "is_professional": "true"
    }
    resp = await client.get("/users/", headers=headers, params=params)
    assert resp.status_code == 200

    data = resp.json()
    # normalize paginated vs bare list
    if isinstance(data, dict) and "items" in data:
        users_list = data["items"]
    elif isinstance(data, list):
        users_list = data
    else:
        pytest.fail(f"Unexpected response format: {data!r}")

    # Only the professional anonymous user should be returned
    assert len(users_list) == 1
    returned = users_list[0]
    assert returned["email"] == anon_pro.email
    assert returned["role"] == UserRole.ANONYMOUS.name
    assert returned["is_professional"] is True




# @pytest.mark.asyncio
# async def test_create_user(async_client):
#     # 1) create a brand-new user
#     new_user = {"email": "alice@example.com", "password": "TestPass123!"}
#     resp = await async_client.post("/users/", json=new_user)
#     assert resp.status_code == 201
#     data = resp.json()
#     assert data["email"] == new_user["email"]
#     assert "id" in data

# @pytest.mark.asyncio
# async def test_create_user_duplicate(async_client):
#     # 2) creating the same email again returns 400
#     duplicate = {"email": "alice@example.com", "password": "TestPass123!"}
#     resp = await async_client.post("/users/", json=duplicate)
#     assert resp.status_code == 400

# @pytest.mark.asyncio
# async def test_read_user_list(async_client, admin_token):
#     # 3) list all users (admin only)
#     headers = {"Authorization": f"Bearer {admin_token}"}
#     resp = await async_client.get("/users/", headers=headers)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert isinstance(data, list)
#     # at least the admin and “alice” should appear
#     emails = [u["email"] for u in data]
#     assert "alice@example.com" in emails

@pytest.mark.asyncio
async def test_read_user_by_id(async_client, admin_user, admin_token):
    # 4) get a single user by ID
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == admin_user.email

# @pytest.mark.asyncio
# async def test_read_nonexistent_user(async_client, admin_token):
#     # 5) 404 on missing user
#     headers = {"Authorization": f"Bearer {admin_token}"}
#     resp = await async_client.get("/users/999999", headers=headers)
#     assert resp.status_code == 404

# @pytest.mark.asyncio
# async def test_read_user_unauthorized(async_client, admin_user):
#     # 6) no token → 401
#     resp = await async_client.get(f"/users/{admin_user.id}")
#     assert resp.status_code == 401

# @pytest.mark.asyncio
# async def test_update_user(async_client, admin_user, admin_token):
#     # 7) update profile fields
#     headers = {"Authorization": f"Bearer {admin_token}"}
#     update = {"full_name": "Alice Wonderland"}
#     resp = await async_client.put(f"/users/{admin_user.id}", json=update, headers=headers)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert data["full_name"] == "Alice Wonderland"

# @pytest.mark.asyncio
# async def test_update_user_unauthorized(async_client, admin_user):
#     # 8) cannot update without token
#     resp = await async_client.put(f"/users/{admin_user.id}", json={"full_name": "X"})
#     assert resp.status_code == 401


@pytest.fixture
def tmp_templates_dir(tmp_path):
    """
    Create an empty temporary directory to act as the templates_dir.
    """
    return tmp_path

@pytest.fixture
def tm(tmp_templates_dir, monkeypatch):
    """
    Patch a TemplateManager instance so its templates_dir points at our tmp directory.
    """
    manager = TemplateManager()
    monkeypatch.setattr(manager, "templates_dir", tmp_templates_dir)
    return manager

def test_read_template_success(tm, tmp_templates_dir):
    # Arrange: create a dummy template file
    filename = "hello.txt"
    expected = "Hello, Template!"
    file_path = tmp_templates_dir / filename
    file_path.write_text(expected, encoding="utf-8")

    # Act
    result = tm._read_template(filename)

    # Assert
    assert result == expected

def test_read_template_file_not_found(tm):
    # When the file does not exist, we expect a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        tm._read_template("does_not_exist.txt")

# @pytest.fixture
# def tm():
#     return TemplateManager()

def test_apply_email_styles_multiple_tags(tm):
    # Expected inline styles from the method
    body_style = (
        "font-family: Arial, sans-serif; font-size: 16px; color: #333333; "
        "background-color: #ffffff; line-height: 1.5;"
    )
    h1_style = (
        "font-size: 24px; color: #333333; font-weight: bold; "
        "margin-top: 20px; margin-bottom: 10px;"
    )
    p_style = (
        "font-size: 16px; color: #666666; margin: 10px 0; line-height: 1.6;"
    )
    a_style = "color: #0056b3; text-decoration: none; font-weight: bold;"
    ul_style = "list-style-type: none; padding: 0;"
    li_style = "margin-bottom: 10px;"

    html = "<h1>Header</h1><p>Paragraph</p><a>Link</a><ul><li>Item</li></ul>"
    styled = tm._apply_email_styles(html)

    # Check wrapper div with body style
    assert styled.startswith(f'<div style="{body_style}">')
    # Check each tag got its style attribute
    assert f'<h1 style="{h1_style}">Header</h1>' in styled
    assert f'<p style="{p_style}">Paragraph</p>' in styled
    assert f'<a style="{a_style}">Link</a>' in styled
    assert f'<ul style="{ul_style}">' in styled
    assert f'<li style="{li_style}">Item</li>' in styled
    # Closing tags and wrapper
    assert styled.endswith('</ul></div>')

def test_apply_email_styles_empty_html(tm):
    body_style = (
        "font-family: Arial, sans-serif; font-size: 16px; color: #333333; "
        "background-color: #ffffff; line-height: 1.5;"
    )
    # An empty HTML string should still be wrapped
    styled = tm._apply_email_styles("")
    assert styled == f'<div style="{body_style}"></div>'

def test_render_template_success(monkeypatch, tm):
    # 1) Stub out _read_template
    def fake_read_template(self, filename):
        mapping = {
            "header.md": "HEADER_CONTENT",
            "footer.md": "FOOTER_CONTENT",
            "welcome.md": "Hello, {user}!"
        }
        return mapping[filename]
    monkeypatch.setattr(TemplateManager, "_read_template", fake_read_template)

    # 2) Stub out markdown2.markdown
    def fake_markdown(text):
        return f"<html>{text}</html>"
    monkeypatch.setattr(markdown2, "markdown", fake_markdown)

    # 3) Stub out _apply_email_styles (accepting self and html)
    def fake_apply(self, html):
        return f"STYLED[{html}]"
    monkeypatch.setattr(TemplateManager, "_apply_email_styles", fake_apply)

    # 4) Call render_template
    result = tm.render_template("welcome", user="Alice")

    # 5) Verify the sequence
    expected_md = "HEADER_CONTENT\nHello, Alice!\nFOOTER_CONTENT"
    assert result == f"STYLED[<html>{expected_md}</html>]"


@pytest.mark.asyncio
def test_render_template_missing_context_raises(monkeypatch):
    """
    If the main template contains a placeholder not in context,
    render_template should raise a KeyError from .format(...)
    """
    tm = TemplateManager()

    # Stub read_template for header/footer and a bad main template
    def fake_read_template(self, filename):
        if filename == "header.md":
            return "H"
        if filename == "footer.md":
            return "F"
        # main template missing 'name' key
        return "Hi {name} and {missing}"
    monkeypatch.setattr(TemplateManager, "_read_template", fake_read_template)

    # Stub markdown2 and _apply_email_styles to ensure they would not run
    monkeypatch.setattr(f"{TEMPLATE_MODULE_PATH}.markdown2", 
                        __import__("types").SimpleNamespace(markdown=lambda x: x))
    monkeypatch.setattr(TemplateManager, "_apply_email_styles", lambda html: html)

    # Calling without 'missing' in context should KeyError
    with pytest.raises(KeyError) as exc:
        tm.render_template("any", name="Bob")
    assert "missing" in str(exc.value)

class DummySMTP:
    """
    A dummy SMTP context manager that records calls.
    """
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def starttls(self):
        self.calls.append("starttls")

    def login(self, username, password):
        self.calls.append(("login", username, password))

    def sendmail(self, from_addr, to_addr, msg):
        self.calls.append(("sendmail", from_addr, to_addr, msg))

def test_smtpclient_send_email_success(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # Arrange: create an SMTPClient with dummy credentials
    client = SMTPClient(server="smtp.test", port=25, username="user@test", password="secret")

    # Patch smtplib.SMTP to return our DummySMTP
    dummy = DummySMTP(client.server, client.port)
    monkeypatch.setattr(smtplib, "SMTP", lambda server, port: dummy)

    # Act
    client.send_email("Test Subject", "<p>Hello!</p>", "recipient@test")

    # Assert: SMTP methods were called in proper order
    assert dummy.calls[0] == "starttls"
    assert dummy.calls[1] == ("login", client.username, client.password)
    assert dummy.calls[2][0] == "sendmail"
    _, from_addr, to_addr, raw = dummy.calls[2]
    # Check the raw message contains the subject and HTML body
    assert f"Subject: Test Subject" in raw
    assert "<p>Hello!</p>" in raw
    assert f"Email sent to recipient@test" in caplog.text

def test_smtpclient_send_email_failure(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)
    client = SMTPClient(server="smtp.bad", port=2525, username="user@bad", password="wrong")

    # Define an SMTP that errors on enter
    class BadSMTP:
        def __init__(self, server, port):
            pass
        def __enter__(self):
            raise RuntimeError("connection failed")
        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(smtplib, "SMTP", BadSMTP)

    with pytest.raises(RuntimeError):
        client.send_email("Subj", "<p>Fail</p>", "fail@test")

    assert "Failed to send email: connection failed" in caplog.text