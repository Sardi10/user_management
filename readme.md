# Reflection on the User Management System Final Project

## 1. Overview and Personal Learning

Throughout this project I deepened my skills in:

FastAPI & SQLAlchemy (async sessions, dependency overrides, Alembic migrations)

pytest‐asyncio & pytest-cov (fixtures, monkeypatching, terminal coverage reports)

Clean architecture (separating services, routers, schemas)

Secure API design (OAuth2, role checks, HTTPException handling)

Email templating (Markdown → HTML → inline CSS for broad compatibility)

## 2. Quality Assurance (5 Issues, 30%)
I opened and closed Six detailed bug issues, each with repro steps, fixes on feature branches, tests, and PRs:

Issue #1: Verification Email Sending Service Not Working

Fixed unique‐constraint check in create_user → HTTP 400

PR 🔗 https://github.com/Sardi10/user_management/issues/1

Issue #2: Verification Link Contains None Instead of User ID

Moved the session.flush() call to occur immediately after session.add(new_user).

PR 🔗 https://github.com/Sardi10/user_management/issues/3

Issue #3: GET /users/me Has No Example Response in Swagger UI

Added schema_extra with a realistic example to the UserProfileDTO Pydantic model.

PR 🔗 https://github.com/Sardi10/user_management/issues/5

Issue #4: NameError: UUID is not defined

Imported UUID at the top of dependencies.py.

Simplified get_current_user to a single clear code path.

PR 🔗 https://github.com/Sardi10/user_management/issues/7

Issue #5: Calling POST /{user_id}/upgrade-pro triggers an internal server error

Issue resolved by adding from datetime import datetime

PR 🔗 https://github.com/Sardi10/user_management/issues/9

Issue #6: Fix missing imports causing NameError in user routes

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi import Query # ← added this

PR 🔗 https://github.com/Sardi10/user_management/issues/12

## 3. Test Coverage Improvement (26 New Tests, 40%)
I identified coverage gaps and wrote 26 new async tests across unit and API levels. Highlights include:

User endpoints

test_get_user_not_found https://github.com/Sardi10/user_management/issues/15 
test_get_user_success https://github.com/Sardi10/user_management/issues/17

test_update_user_not_found https://github.com/Sardi10/user_management/issues/19 
test_update_user_success https://github.com/Sardi10/user_management/issues/21

test_register_user_* 

Authentication

test_login_locked_account https://github.com/Sardi10/user_management/issues/23
test_login_invalid_credentials https://github.com/Sardi10/user_management/issues/27
test_login_success https://github.com/Sardi10/user_management/issues/25

Upgrade‐to‐Pro

test_upgrade_to_pro_insufficient_privileges https://github.com/Sardi10/user_management/issues/31
test_upgrade_to_pro_user_not_found https://github.com/Sardi10/user_management/issues/33
test_upgrade_to_pro_success https://github.com/Sardi10/user_management/issues/35

“Me” endpoints

test_get_my_profile https://github.com/Sardi10/user_management/issues/29
test_update_my_profile_validation
test_update_my_profile_success 

TemplateManager helpers

test_read_template_success 
test_read_template_not_found 

test_apply_email_styles_* 

test_render_template_success 
test_render_template_keyerror

After these additions, overall coverage rose 95 %.

## 4. New Feature Implementation (2 Features, 40%)
I chose two real enhancements from our backlog and implemented them fully, each with its own branch, tests, and documentation:

Feature A: User Profile Management & Pro-Status
Issue #27: Support .md templates with header/footer and context

Reads header.md, footer.md, and <name>.md, formats with context

Uses markdown2 → HTML → _apply_email_styles for inline CSS

Tests: unit tests for _read_template, _apply_email_styles, and render_template

PR 🔗 https://github.com/Sardi10/user_management/commit/16426478220a9ea055f0705bcd834bf3b4611595

Feature B: Advanced User Search Filters
Issue #28: Extend /users/ with q, role, and is_professional filters

Updated UserService.search_users and router to apply combined filters

Returns paginated results under items with total/page/size metadata

Tests: test_no_filters_returns_all, test_filter_by_q_and_role_and_pro_status

PR 🔗 https://github.com/Sardi10/user_management/commit/900fb00aab8dd26370805618eaa0612d453203d8

## 5. Deployment & Repository Links
DockerHub: https://hub.docker.com/repository/docker/sardi10/user_management/general

GitHub: https://github.com/Sardi10/user_management

## 6. Commit History & Process
I followed GitFlow and a professional commit cadence:

Initial setup: CI, Docker, Alembic, basic endpoints 

QA fixes: one branch/issue per bug 

Test suite: commits for each new test case 

Feature A & B: two feature branches and PRs 

Final docs & cleanup: 
