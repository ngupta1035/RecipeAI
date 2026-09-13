from app.models import Favorite, Rating, Recipe
from tests.conftest import register_and_login, create_recipe


def test_toggle_favorite_add_and_remove(app, client, alice):
    create_recipe(client, "Tomato Soup")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Tomato Soup").first().id

    r = client.post(f"/recipes/{recipe_id}/favorite", follow_redirects=True)
    assert b"Added to favorites" in r.data
    with app.app_context():
        assert Favorite.query.filter_by(user_id=alice.id, recipe_id=recipe_id).count() == 1

    r = client.post(f"/recipes/{recipe_id}/favorite", follow_redirects=True)
    assert b"Removed from favorites" in r.data
    with app.app_context():
        assert Favorite.query.filter_by(user_id=alice.id, recipe_id=recipe_id).count() == 0


def test_favorite_requires_login(app, client):
    register_and_login(client, "alice", "alice@example.com")
    create_recipe(client, "Tomato Soup")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Tomato Soup").first().id
    client.get("/auth/logout")

    r = client.post(f"/recipes/{recipe_id}/favorite", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_favorites_page_lists_saved_recipes(app, client, alice):
    create_recipe(client, "Tomato Soup")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Tomato Soup").first().id
    client.post(f"/recipes/{recipe_id}/favorite")

    r = client.get("/recipes/favorites")
    assert b"Tomato Soup" in r.data


def test_rating_creates_then_updates_not_duplicates(app, client, alice):
    create_recipe(client, "Dal Fry")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Dal Fry").first().id

    client.post(f"/recipes/{recipe_id}/rate", data={"value": "4"}, follow_redirects=True)
    with app.app_context():
        ratings = Rating.query.filter_by(user_id=alice.id, recipe_id=recipe_id).all()
        assert len(ratings) == 1
        assert ratings[0].value == 4

    client.post(f"/recipes/{recipe_id}/rate", data={"value": "2"}, follow_redirects=True)
    with app.app_context():
        ratings = Rating.query.filter_by(user_id=alice.id, recipe_id=recipe_id).all()
        assert len(ratings) == 1  # still just one row
        assert ratings[0].value == 2


def test_rating_out_of_range_rejected(app, client, alice):
    create_recipe(client, "Dal Fry")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Dal Fry").first().id

    client.post(f"/recipes/{recipe_id}/rate", data={"value": "9"}, follow_redirects=True)
    with app.app_context():
        assert Rating.query.filter_by(user_id=alice.id, recipe_id=recipe_id).count() == 0


def test_average_rating_computed_correctly(app, client):
    register_and_login(client, "owner", "owner@example.com")
    create_recipe(client, "Shared Recipe")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Shared Recipe").first().id
    client.get("/auth/logout")

    for username, value in [("rater1", 5), ("rater2", 3), ("rater3", 4)]:
        register_and_login(client, username, f"{username}@example.com")
        client.post(f"/recipes/{recipe_id}/rate", data={"value": str(value)})
        client.get("/auth/logout")

    with app.app_context():
        recipe = Recipe.query.get(recipe_id)
        assert recipe.average_rating == 4.0
        assert recipe.rating_count == 3
