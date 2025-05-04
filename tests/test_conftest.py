# test_users.py

from builtins import len
import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from app.utils.template_manager import TemplateManager
from app.models.user_model import User, UserRole
from app.utils.security import verify_password
from app.utils.smtp_connection import SMTPClient
from app.services.email_service import EmailService

@pytest.mark.asyncio
async def test_user_creation(db_session, verified_user):
    """Test that a user is correctly created and stored in the database."""
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    stored_user = result.scalars().first()
    assert stored_user is not None
    assert stored_user.email == verified_user.email
    assert verify_password("MySuperPassword$1234", stored_user.hashed_password)

# Apply similar corrections to other test functions
@pytest.mark.asyncio
async def test_locked_user(db_session, locked_user):
    result = await db_session.execute(select(User).filter_by(email=locked_user.email))
    stored_user = result.scalars().first()
    assert stored_user.is_locked

@pytest.mark.asyncio
async def test_verified_user(db_session, verified_user):
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    stored_user = result.scalars().first()
    assert stored_user.email_verified

@pytest.mark.asyncio
async def test_user_role(db_session, admin_user):
    result = await db_session.execute(select(User).filter_by(email=admin_user.email))
    stored_user = result.scalars().first()
    assert stored_user.role == UserRole.ADMIN

@pytest.mark.asyncio
async def test_bulk_user_creation_performance(db_session, users_with_same_role_50_users):
    result = await db_session.execute(select(User).filter_by(role=UserRole.AUTHENTICATED))
    users = result.scalars().all()
    assert len(users) == 50

@pytest.mark.asyncio
async def test_password_hashing(user):
    assert verify_password("MySuperPassword$1234", user.hashed_password)

@pytest.mark.asyncio
async def test_user_unlock(db_session, locked_user):
    locked_user.unlock_account()
    await db_session.commit()
    result = await db_session.execute(select(User).filter_by(email=locked_user.email))
    updated_user = result.scalars().first()
    assert not updated_user.is_locked

@pytest.mark.asyncio
async def test_update_professional_status(db_session, verified_user):
    verified_user.update_professional_status(True)
    await db_session.commit()
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    updated_user = result.scalars().first()
    assert updated_user.is_professional
    assert updated_user.professional_status_updated_at is not None

@pytest.mark.asyncio
async def test_send_user_email_success(email_service, monkeypatch):
    calls = {}

    # stub out TemplateManager.render_template
    def fake_render(self, template_name, **context):
        calls['render'] = (template_name, context)
        return "<html>OK</html>"

    # stub out SMTPClient.send_email at the class level
    def fake_send_email(self, subject, content, recipient):
        calls['send'] = (subject, content, recipient)

    # patch the two collaborators
    monkeypatch.setattr(TemplateManager, 'render_template', fake_render)
    monkeypatch.setattr(SMTPClient, 'send_email', fake_send_email)

    user_data = {'email': 'bob@example.com', 'name': 'Bob'}
    await email_service.send_user_email(user_data, 'email_verification')

    # assertions
    assert calls['render'][0] == 'email_verification'
    assert calls['render'][1] == user_data
    assert calls['send'] == (
        "Verify Your Account",
        "<html>OK</html>",
        'bob@example.com'
    )

@pytest.mark.asyncio
async def test_send_user_email_invalid_type(email_service):
    with pytest.raises(ValueError) as exc:
        await email_service.send_user_email({'email': 'x@x.com'}, 'no_such_type')
    assert "Invalid email type" in str(exc.value)