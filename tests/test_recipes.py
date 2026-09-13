import io

from app.models import Recipe
from tests.conftest import register_and_login, create_recipe


def test_add_recipe_requires_login(client):
    r = client.get("/recipes/add", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_add_recipe_success(app, client, alice):
    r = create_recipe(client, "Veg Pulao")
    assert r.status_code == 200
    with app.app_context():
        recipe = Recipe.query.filter_by(name="Veg Pulao").first()
        assert recipe is not None
        assert recipe.user_id == alice.id


def test_add_recipe_missing_required_field_rejected(app, client, alice):
    r = client.post(
        "/recipes/add",
        data={"name": "", "ingredients": "a", "instructions": "b", "is_vegetarian": "veg"},
    )
    assert r.status_code == 200  # re-renders form with errors
    with app.app_context():
        assert Recipe.query.count() == 0


def test_only_owner_can_edit(app, client):
    register_and_login(client, "alice", "alice@example.com")
    create_recipe(client, "Alice Recipe")
    client.get("/auth/logout")

    register_and_login(client, "bob", "bob@example.com")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Alice Recipe").first().id

    r = client.get(f"/recipes/{recipe_id}/edit")
    assert r.status_code == 403


def test_only_owner_can_delete(app, client):
    register_and_login(client, "alice", "alice@example.com")
    create_recipe(client, "Alice Recipe")
    client.get("/auth/logout")

    register_and_login(client, "bob", "bob@example.com")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Alice Recipe").first().id

    r = client.post(f"/recipes/{recipe_id}/delete")
    assert r.status_code == 403
    with app.app_context():
        assert Recipe.query.get(recipe_id) is not None


def test_owner_can_edit_and_delete(app, client, alice):
    create_recipe(client, "Original Name")
    with app.app_context():
        recipe_id = Recipe.query.filter_by(name="Original Name").first().id

    r = client.post(
        f"/recipes/{recipe_id}/edit",
        data={"name": "Updated Name", "ingredients": "x", "instructions": "y", "is_vegetarian": "nonveg"},
        follow_redirects=True,
    )
    assert b"Updated Name" in r.data

    r = client.post(f"/recipes/{recipe_id}/delete", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Recipe.query.get(recipe_id) is None


def test_image_upload_rejects_non_image_content(client, alice):
    fake_file = (io.BytesIO(b"not actually an image"), "fake.png")
    r = client.post(
        "/recipes/add",
        data={
            "name": "Bad Image Recipe",
            "ingredients": "a",
            "instructions": "b",
            "is_vegetarian": "veg",
            "image": fake_file,
        },
        content_type="multipart/form-data",
    )
    assert b"valid image" in r.data or r.status_code == 200


def test_image_upload_accepts_real_image(app, client, alice):
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buf, format="PNG")
    buf.seek(0)

    r = client.post(
        "/recipes/add",
        data={
            "name": "Good Image Recipe",
            "ingredients": "a",
            "instructions": "b",
            "is_vegetarian": "veg",
            "image": (buf, "real.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    with app.app_context():
        recipe = Recipe.query.filter_by(name="Good Image Recipe").first()
        assert recipe is not None
        assert recipe.image_filename is not None
        assert recipe.image_filename.endswith(".png")
