# Library Management System

Overview
- Small Django-based library management web app for adding, issuing, returning, and tracking books.

Features
- Admin and user login (admin can add/delete/issue books)
- Book listing, issue/return workflow with overdue fines
- Simple session-based authentication for demo purposes

Technologies
- Python 3.x
- Django 3.2
- SQLite (development)
- HTML/CSS/vanilla JS for frontend (no SPA framework)

System Architecture
- Monolithic Django app
- App `LibManager` contains models, views, templates

Database
- Default: SQLite (`db.sqlite3`) for local development
- For production, switch to PostgreSQL/MySQL via `DATABASES` in settings

Local database & initial setup
- This project uses Django migrations to create the database schema. You do not need to commit `db.sqlite3` — create it locally by running migrations.
- Migrations exist in `LibManager/migrations/` and include optional demo seeding that is disabled by default. Enable seeding only via environment variables as described below.

Recommended local steps (PowerShell):

```powershell
# 1. Create and activate virtualenv
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy example env and edit values
copy .env.example .env
# Edit .env and set DJANGO_SECRET_KEY (and any optional seeds)

# 4. Create database locally via migrations
python manage.py migrate

# 5 (optional). Create a local superuser for admin access
python manage.py createsuperuser

# Notes: Do NOT add or commit db.sqlite3 to the repository. Ensure .gitignore contains db.sqlite3.
```

If you accidentally add `db.sqlite3` to git before the initial commit, remove it from tracking (do not delete the local file):

```powershell
# If repository has already been initialized and file is tracked
git rm --cached db.sqlite3
git commit -m "Remove db.sqlite3 from tracking"
```

Seeding demo data
- The project previously included seed migrations; the seeding step is now opt-in. To enable seeding during migration, set `SEED_DEFAULT_USER=true` and `DEFAULT_USER_PASSWORD` in your `.env` before running `python manage.py migrate`.

Installation
1. Clone repository
2. Create and activate a Python virtualenv

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Setup
- Copy `.env.example` to `.env` and fill values (especially `DJANGO_SECRET_KEY`).
- Recommended: do NOT commit real secrets.
- By default the project will NOT seed any demo users or admin passwords. To enable seeding during `migrate`, set `SEED_DEFAULT_USER=true` and `DEFAULT_USER_PASSWORD` in `.env`.

Run
```powershell
python manage.py migrate
python manage.py runserver
```

Folder structure
- `LibraryManagementSystem/` — Django project settings
- `LibManager/` — main application (models, views, templates)
- `Templates/` — HTML templates
- `static/` — CSS and JS assets
- `db.sqlite3` — development database (should be removed from public repo)

Screenshots
- Add screenshots to `/screenshots` and reference them here (login, books list, issue flow, admin pages).

Future enhancements
- Use Django's built-in `User` model and admin for authentication
- Replace session-based admin with Django admin or OAuth
- Use PostgreSQL in production
- Add automated tests and CI

Contributors
- Project owner: (replace with your name)

Security notes
- Secrets must be placed in environment variables. This repository was prepared for public release by moving secrets to envs and adding `.env.example`.

If you want me to also create a CONTRIBUTING.md or add GitHub Actions for CI, tell me and I'll add them.
