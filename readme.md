

# The User Management System Final Project: Your Epic Coding Adventure Awaits! 🎉✨🔥

## Introduction: Buckle Up for the Ride of a Lifetime 🚀🎬

Welcome to the User Management System project - an epic open-source adventure crafted by the legendary Professor Keith Williams for his rockstar students at NJIT! 🏫👨‍🏫⭐ This project is your gateway to coding glory, providing a bulletproof foundation for a user management system that will blow your mind! 🤯 You'll bridge the gap between the realms of seasoned software pros and aspiring student developers like yourselves. 

### [Instructor Video - Project Overview and Tips](https://youtu.be/gairLNAp6mA) 🎥

- [Introduction to the system features and overview of the project - please read](system_documentation.md) 📚
- [Project Setup Instructions](setup.md) ⚒️
- [Features to Select From](features.md) 🛠️
- [About the Project](about.md)🔥🌟

## Goals and Objectives: Unlock Your Coding Superpowers 🎯🏆🌟

Get ready to ascend to new heights with this legendary project:

1. **Practical Experience**: Dive headfirst into a real-world codebase, collaborate with your teammates, and contribute to an open-source project like a seasoned pro! 💻👩‍💻🔥
2. **Quality Assurance**: Develop ninja-level skills in identifying and resolving bugs, ensuring your code quality and reliability are out of this world. 🐞🔍⚡
3. **Test Coverage**: Write additional tests to cover edge cases, error scenarios, and important functionalities - leave no stone unturned and no bug left behind! ✅🧪🕵️‍♂️
4. **Feature Implementation**: Implement a brand new, mind-blowing feature and make your epic mark on the project, following best practices for coding, testing, and documentation like a true artisan. ✨🚀🎆
5. **Collaboration**: Foster teamwork and collaboration through code reviews, issue tracking, and adhering to contribution guidelines - teamwork makes the dream work, and together you'll conquer worlds! 🤝💪🌍
6. **Industry Readiness**: Prepare for the software industry by working on a project that simulates real-world development scenarios - level up your skills to super hero status  and become an unstoppable coding force! 🔝🚀🏆⚡

## Submission and Grading: Your Chance to Shine 📝✏️📈

1. **Reflection Document**: Submit a 1-2 page Word document reflecting on your learnings throughout the course and your experience working on this epic project. Include links to the closed issues for the **5 QA issues, 10 NEW tests, and 1 Feature** you'll be graded on. Make sure your project successfully deploys to DockerHub and include a link to your Docker repository in the document - let your work speak for itself! 📄🔗💥

2. **Commit History**: Show off your consistent hard work through your commit history like a true coding warrior. **Projects with less than 10 commits will get an automatic 0 - ouch!** 😬⚠️ A significant part of your project's evaluation will be based on your use of issues, commits, and following a professional development process like a boss - prove your coding prowess! 💻🔄🔥

3. **Deployability**: Broken projects that don't deploy to Dockerhub or pass all the automated tests on GitHub actions will face point deductions - nobody likes a buggy app! 🐞☠️ Show the world your flawless coding skills!

## Managing the Project Workload: Stay Focused, Stay Victorious ⏱️🧠⚡

This project requires effective time management and a well-planned strategy, but fear not - you've got this! Follow these steps to ensure a successful (and sane!) project outcome:

1. **Select a Feature**: [Choose a feature](features.md) from the provided list of additional improvements that sparks your interest and aligns with your goals like a laser beam. ✨⭐🎯 This is your chance to shine!

2. **Quality Assurance (QA)**: Thoroughly test the system's major functionalities related to your chosen feature and identify at least 5 issues or bugs like a true detective. Create GitHub issues for each identified problem, providing detailed descriptions and steps to reproduce - the more detail, the merrier! 🔍🐞🕵️‍♀️ Leave no stone unturned!

3. **Test Coverage Improvement**: Review the existing test suite and identify gaps in test coverage like a pro. Create 10 additional tests to cover edge cases, error scenarios, and important functionalities related to your chosen feature. Focus on areas such as user registration, login, authorization, and database interactions. Simulate the setup of the system as the admin user, then creating users, and updating user accounts - leave no stone unturned, no bug left behind! ✅🧪🔍🔬 Become the master of testing!

4. **New Feature Implementation**: Implement your chosen feature, following the project's coding practices and architecture like a coding ninja. Write appropriate tests to ensure your new feature is functional and reliable like a rock. Document the new feature, including its usage, configuration, and any necessary migrations - future you will thank you profusely! 🚀✨📝👩‍💻⚡ Make your mark on this project!

5. **Maintain a Working Main Branch**: Throughout the project, ensure you always have a working main branch deploying to Docker like a well-oiled machine. This will prevent any last-minute headaches and ensure a smooth submission process - no tears allowed, only triumphs! 😊🚢⚓ Stay focused, stay victorious!

Remember, it's more important to make something work reliably and be reasonably complete than to implement an overly complex feature. Focus on creating a feature that you can build upon or demonstrate in an interview setting - show off your skills like a rockstar! 💪🚀🎓

Don't forget to always have a working main branch deploying to Docker at all times. If you always have a working main branch, you will never be in jeopardy of receiving a very disappointing grade :-). Keep that main branch shining bright!

Let's embark on this epic coding adventure together and conquer the world of software engineering! You've got this, coding rockstars! 🚀🌟✨

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
DockerHub: https://hub.docker.com/repository/managementdocker/YourUser/user-

GitHub: https://github.com/Sardi10/user_management

## 6. Commit History & Process
I followed GitFlow and a professional commit cadence:

Initial setup: CI, Docker, Alembic, basic endpoints 

QA fixes: one branch/issue per bug 

Test suite: commits for each new test case 

Feature A & B: two feature branches and PRs 

Final docs & cleanup: 
