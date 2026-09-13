from app.models import Recipe
from tests.conftest import create_recipe


def test_admin_routes_block_anonymous(client):
    for path in ["/admin/", "/admin/users", "/admin/recipes"]:
        r = client.get(path)
        assert r.status_code == 403


def test_admin_routes_block_regular_user(client, alice):
    for path in ["/admin/", "/admin/users", "/admin/recipes"]:
        r = client.get(path)
        assert r.status_code == 403


def test_admin_can_access_dashboard(client, admin_user):
    r = client.get("/admin/")
    assert r.status_code == 200
    assert b"Total Users" in r.data


def test_admin_users_page_lists_users(client, admin_user):
    r = client.get("/admin/users")
    assert b"admin" in r.data.lower()


def test_admin_can_delete_any_recipe(app, client, admin_user):
    create_recipe(client, "Admin Owned Recipe")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Admin Owned Recipe").first().id

    r = client.post(f"/admin/recipes/{recipe_id}/delete", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Recipe.query.get(recipe_id) is None


def test_non_admin_cannot_hit_admin_delete_directly(app, client, alice):
    create_recipe(client, "Alice Recipe")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Alice Recipe").first().id

    r = client.post(f"/admin/recipes/{recipe_id}/delete")
    assert r.status_code == 403
    with app.app_context():
        assert Recipe.query.get(recipe_id) is not None
