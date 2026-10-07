# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project

**PhishGuard** — a Flask-based phishing awareness training platform (Python 3, no Node/npm).  
Actual source lives in `c:\Users\aryan\Downloads\PROJECT\` (the workspace root folder is currently empty).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize DB + seed all data (run once)
python app.py

# Run dev server (after DB is initialized)
flask run --host=0.0.0.0 --port=5000
# OR
python app.py   # also starts server after seeding
```

There is **no test suite, no linter config, no Makefile, and no `package.json`**. No CI configuration exists.

## Architecture

```
app.py          — entry point: creates app, registers 5 blueprints, defines seed_data(), starts server
config.py       — Config class; SQLite DB at project root (database.db); hardcoded dev SECRET_KEY
models/models.py — all SQLAlchemy models in one file (db = SQLAlchemy())
routes/auth.py  — login_required and admin_required decorators defined here; imported by all other routes
routes/admin.py — url_prefix='/admin'; uses @admin_required
services/scoring.py — update_awareness_score() must be called after every quiz submit, simulation submit, and module complete
templates/      — Jinja2; base.html extended by all pages; admin templates in templates/admin/
```

## Critical Patterns

- **Auth decorators** live in `routes/auth.py` — import `login_required`/`admin_required` from there, not from a separate middleware file.
- **Score update is manual** — `update_awareness_score(user_id)` from `services/scoring.py` must be explicitly called whenever a user completes a module, quiz, or simulation. It is NOT triggered automatically by model saves.
- **DB initialization**: `db.create_all()` + `seed_data()` are called only when running `python app.py` directly (inside `if __name__ == '__main__'`). Running via `flask run` skips seeding.
- **Session stores** `user_id`, `username`, and `role` as plain strings — role check is `session.get('role') == 'admin'` or via `User.role`.
- **`red_flags` field** on `Simulation` is a pipe-delimited string (`|`), not JSON. Split on `|` in templates/code.
- **`answers_json`** on `QuizAttempt` is stored as a JSON string (`json.dumps`/`json.loads`) — not a native JSON column.
- **Overall awareness score formula**: `training*0.30 + quiz*0.30 + simulation*0.40`.
- **Quiz score** uses only the *latest* attempt, not the best or average.
- Default admin credentials seeded: `admin / Admin@1234`. Default user: `alice / User@1234`.

## Code Style

- No formatter or linter enforced. Follow existing style: 4-space indent, single quotes for strings, no type annotations.
- Blueprint names match module names: `auth_bp`, `user_bp`, `quiz_bp`, `simulation_bp`, `admin_bp`.
- `db.session.commit()` is called at the end of each route handler — no unit-of-work pattern.
- Flash categories used: `'success'`, `'danger'`, `'warning'`, `'info'` (Bootstrap alert classes).
- `User.query.get(id)` used directly (SQLAlchemy 1.x style) — not `db.session.get(User, id)`.
