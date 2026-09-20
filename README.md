# POS Application

## Description

This API manages products, inventory, sales, customers, users, suppliers, payments, and receipts for a retail business. It supports full CRUD operations across nine entities with proper foreign key relationships and data validation.

Built with FastAPI, SQLAlchemy and PostgreSQL.

## Setup

```bash
python -m venv env
source env/bin/activate      
pip install -r requirements.txt
```

Create a `.env` file in the project root (it is git-ignored):

```env
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/pos_db
JWT_SECRET_KEY=<a long random string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Run the API from the `app/` folder:

```bash
cd app
uvicorn main:app --reload
```

Interactive docs are then available at <http://127.0.0.1:8000/docs>.

## Running the tests

```bash
pytest
```

Run this from the project root with your virtual environment active. That is all
that is needed: no `.env` file, no PostgreSQL server and no other setup.

Useful variations:

```bash
pytest -v                          # one line per test
pytest app/tests/test_products.py  # a single file
pytest -k "duplicate"              # tests whose name contains "duplicate"
pytest -x                          # stop at the first failure
```

### How the tests are set up

- **Isolated database.** `app/tests/conftest.py` forces `DATABASE_URL=sqlite://`
  before the app is imported and overrides the `get_db` dependency with an
  in-memory SQLite database. Tables are created and dropped around every test, so
  tests cannot affect each other or your PostgreSQL development database, even if
  your shell or `.env` points at it. SQLite foreign-key enforcement is switched on
  to match PostgreSQL.
- **Authentication.** The default `client` fixture is logged in as an Admin. Use
  `anon_client` for unauthenticated requests and `auth_headers("Manager")` (or
  `"Cashier"`) to act as another role.
- **Layout.** One file per resource in `app/tests/` (`test_products.py`,
  `test_sales.py`, ...), plus `test_permissions.py` (role rules),
  `test_security.py` (JWT handling), `test_relationships.py` (cascades),
  `test_product_service.py` (service layer) and `test_isolation.py` (checks that
  the suite never touches PostgreSQL). Each resource is covered for create, read,
  update and delete, validation errors (422), missing records (404), invalid
  references (400) and duplicate or in-use records (409).

## Continuous integration

`.github/workflows/tests.yml` runs the full suite on Python 3.10 on every push and
on every pull request that is opened, updated or reopened. The job fails if any
test fails.