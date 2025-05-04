import pytest
from app.utils.smtp_connection import SMTPClient
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

    
@pytest.mark.asyncio
async def test_send_markdown_email(email_service, monkeypatch):
    calls = {}

    # 1) Fake out TemplateManager.render_template to return markdown
    def fake_render(self, template_name, **context):
        calls['render'] = (template_name, context)
        # pretend your markdown template produces this
        return (
            f"## Hi {context['name']}\n\n"
            f"Please verify your email by clicking [here]({context['verification_url']})."
        )

    # 2) Fake out SMTPClient.send_email so no real email is sent
    def fake_send_email(self, subject, content, recipient):
        calls['send'] = (subject, content, recipient)

    # Patch the collaborators
    monkeypatch.setattr(TemplateManager, 'render_template', fake_render)
    monkeypatch.setattr(SMTPClient, 'send_email', fake_send_email)

    # Prepare test data
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    # Exercise the code
    await email_service.send_user_email(user_data, 'email_verification')

    # Assertions on render
    assert calls['render'][0] == 'email_verification'
    assert calls['render'][1] == user_data

    # Assertions on send_email
    subject, content, recipient = calls['send']
    assert subject == "Verify Your Account"
    assert "## Hi Test User" in content
    assert "(http://example.com/verify?token=abc123)" in content
    assert recipient == "test@example.com"
