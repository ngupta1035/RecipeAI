import pytest

from app import create_app
from app.extensions import db as _db
from app.models import User, Recipe


@pytest.fixture
def app():
    """A fresh app + in-memory database for every test. CSRF is disabled
    under the testing config so tests can POST forms directly."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


def register(client, username="alice", email="alice@example.com", password="testpass123"):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="alice@example.com", password="testpass123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def register_and_login(client, username="alice", email="alice@example.com", password="testpass123"):
    register(client, username, email, password)
    return login(client, email, password)


def create_recipe(client, name="Test Recipe", ingredients="a, b, c", **extra):
    data = {
        "name": name,
        "ingredients": ingredients,
        "instructions": "Cook it well.",
        "is_vegetarian": "veg",
    }
    data.update(extra)
    return client.post("/recipes/add", data=data, follow_redirects=True)


@pytest.fixture
def alice(app, client):
    """A logged-in user, ready to use in a test."""
    register_and_login(client, "alice", "alice@example.com")
    with app.app_context():
        user = User.query.filter_by(username="alice").first()
        yield user


@pytest.fixture
def admin_user(app, client):
    """A logged-in user promoted to admin."""
    register_and_login(client, "admin", "admin@example.com")
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        user.is_admin = True
        _db.session.commit()
        yield user
