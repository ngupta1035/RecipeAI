from app.models import User
from tests.conftest import register, login, register_and_login


def test_register_creates_user_with_hashed_password(app, client):
    register(client, "bob", "bob@example.com", "testpass123")
    with app.app_context():
        user = User.query.filter_by(username="bob").first()
        assert user is not None
        assert user.password_hash != "testpass123"
        assert user.check_password("testpass123")
        assert not user.check_password("wrongpassword")


def test_duplicate_username_rejected(client):
    register(client, "bob", "bob@example.com")
    r = register(client, "bob", "someoneelse@example.com")
    assert b"already taken" in r.data


def test_duplicate_username_case_insensitive(client):
    register(client, "Bob", "bob@example.com")
    r = register(client, "bob", "someoneelse@example.com")
    assert b"already taken" in r.data


def test_duplicate_email_rejected(client):
    register(client, "bob", "bob@example.com")
    r = register(client, "someoneelse", "bob@example.com")
    assert b"already exists" in r.data


def test_password_too_short_rejected(app, client):
    register(client, "bob", "bob@example.com", "short")
    with app.app_context():
        assert User.query.filter_by(username="bob").first() is None


def test_login_with_correct_credentials(client):
    register(client, "bob", "bob@example.com", "testpass123")
    r = login(client, "bob@example.com", "testpass123")
    assert b"Welcome back" in r.data


def test_login_with_wrong_password_fails(client):
    register(client, "bob", "bob@example.com", "testpass123")
    r = login(client, "bob@example.com", "wrongpassword")
    assert b"Invalid email or password" in r.data


def test_logout_clears_session(client):
    register_and_login(client, "bob", "bob@example.com")
    r = client.get("/auth/logout", follow_redirects=True)
    assert b"logged out" in r.data.lower()

    # Protected page should now redirect to login
    r = client.get("/recipes/add", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]
