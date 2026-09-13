from tests.conftest import create_recipe


def seed_recipes(client):
    create_recipe(client, "Paneer Tikka", "paneer, yogurt, spices",
                  cuisine="Indian", meal_category="Dinner", cook_time="20", difficulty="Easy")
    create_recipe(client, "Veg Biryani", "rice, veggies, spices",
                  cuisine="Indian", meal_category="Lunch", cook_time="40", difficulty="Medium")
    create_recipe(client, "Chicken Manchurian", "chicken, soy sauce, garlic",
                  cuisine="Chinese", meal_category="Dinner", is_vegetarian="nonveg", cook_time="25", difficulty="Medium")
    create_recipe(client, "Fried Rice", "rice, carrot, peas",
                  cuisine="Chinese", meal_category="Lunch", cook_time="15", difficulty="Easy")


def test_search_by_name(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?q=biryani")
    assert b"Veg Biryani" in r.data
    assert b"Paneer Tikka" not in r.data


def test_search_by_ingredient(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?q=chicken")
    assert b"Chicken Manchurian" in r.data
    assert b"Fried Rice" not in r.data


def test_filter_by_cuisine(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?cuisine=Chinese")
    assert b"Chicken Manchurian" in r.data
    assert b"Fried Rice" in r.data
    assert b"Paneer Tikka" not in r.data


def test_filter_by_veg_type(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?veg=nonveg")
    assert b"Chicken Manchurian" in r.data
    assert b"Fried Rice" not in r.data


def test_filter_by_max_cook_time(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?max_time=20")
    assert b"Fried Rice" in r.data
    assert b"Paneer Tikka" in r.data
    assert b"Veg Biryani" not in r.data


def test_sort_by_time_ascending(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?sort=time")
    html = r.get_data(as_text=True)
    assert html.index("Fried Rice") < html.index("Veg Biryani")


def test_pagination_splits_results(app, client, alice):
    app.config["RECIPES_PER_PAGE"] = 2
    seed_recipes(client)
    r = client.get("/recipes/?page=1")
    assert r.status_code == 200
    assert b"4 recipes found" in r.data
    r2 = client.get("/recipes/?page=2")
    assert r2.status_code == 200


def test_no_results_shows_friendly_message(client, alice):
    seed_recipes(client)
    r = client.get("/recipes/?q=nonexistentfood")
    assert b"No recipes match" in r.data
