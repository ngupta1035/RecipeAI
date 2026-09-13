from app.models import Recipe, RecentlyViewed
from tests.conftest import create_recipe


def test_dashboard_requires_login(client):
    r = client.get("/users/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_dashboard_shows_own_recipes_and_stats(client, alice):
    create_recipe(client, "My Recipe One")
    create_recipe(client, "My Recipe Two")

    r = client.get("/users/dashboard")
    assert b"My Recipe One" in r.data
    assert b"My Recipe Two" in r.data
    assert f"Welcome back, {alice.username}".encode() in r.data


def test_viewing_recipe_twice_does_not_duplicate_recently_viewed(app, client, alice):
    create_recipe(client, "Viewed Recipe")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Viewed Recipe").first().id

    client.get(f"/recipes/{recipe_id}")
    client.get(f"/recipes/{recipe_id}")

    with app.app_context():
        count = RecentlyViewed.query.filter_by(user_id=alice.id, recipe_id=recipe_id).count()
        assert count == 1


def test_dashboard_shows_recently_viewed(app, client, alice):
    create_recipe(client, "Viewed Recipe")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Viewed Recipe").first().id
    client.get(f"/recipes/{recipe_id}")

    r = client.get("/users/dashboard")
    assert b"Viewed Recipe" in r.data
