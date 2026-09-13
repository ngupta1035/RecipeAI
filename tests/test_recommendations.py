from recommendation import (
    build_recipe_dataframe,
    compute_similarity_matrix,
    get_similar_recipes,
    explain_similarity,
    tokenize_ingredients,
    match_recipes_by_ingredients,
)
from app.models import Recipe
from tests.conftest import create_recipe


SAMPLE_RECIPES = [
    {"id": 1, "name": "Paneer Butter Masala", "ingredients": "paneer, tomato, butter, cream",
     "cuisine": "Indian", "meal_category": "Dinner", "is_vegetarian": True},
    {"id": 2, "name": "Paneer Tikka", "ingredients": "paneer, yogurt, spices",
     "cuisine": "Indian", "meal_category": "Dinner", "is_vegetarian": True},
    {"id": 3, "name": "Chicken Manchurian", "ingredients": "chicken, soy sauce, garlic",
     "cuisine": "Chinese", "meal_category": "Dinner", "is_vegetarian": False},
]


# ---- Pure engine tests (no Flask/DB needed) ----

def test_similarity_ranks_related_recipe_higher():
    df = build_recipe_dataframe(SAMPLE_RECIPES)
    sim = compute_similarity_matrix(df)
    results = get_similar_recipes(1, df, sim, top_n=2)
    result_ids = [r["id"] for r in results]
    assert result_ids[0] == 2  # Paneer Tikka should outrank Chicken Manchurian
    assert 3 in result_ids or len(result_ids) == 1


def test_similarity_handles_empty_and_single_recipe():
    assert compute_similarity_matrix(build_recipe_dataframe([])) is None
    assert compute_similarity_matrix(build_recipe_dataframe([SAMPLE_RECIPES[0]])) is None
    assert get_similar_recipes(1, build_recipe_dataframe([]), None) == []


def test_similarity_unknown_id_returns_empty():
    df = build_recipe_dataframe(SAMPLE_RECIPES)
    sim = compute_similarity_matrix(df)
    assert get_similar_recipes(999, df, sim) == []


def test_explain_similarity_finds_shared_traits():
    reasons = explain_similarity(SAMPLE_RECIPES[0], SAMPLE_RECIPES[1])
    joined = " ".join(reasons)
    assert "cuisine" in joined.lower()
    assert "paneer" in joined.lower()


def test_tokenize_ingredients_normalizes():
    tokens = tokenize_ingredients("Potato, Onion\nTomato,  paneer ")
    assert tokens == {"potato", "onion", "tomato", "paneer"}


def test_match_recipes_by_ingredients_ranks_by_percentage():
    available = tokenize_ingredients("potato, onion, tomato, paneer")
    recipes = [
        {"id": 1, "ingredients": "potato, onion, tomato, paneer, spices"},
        {"id": 2, "ingredients": "chicken, garlic"},
        {"id": 3, "ingredients": "potato, onion, cumin"},
    ]
    results = match_recipes_by_ingredients(available, recipes)
    assert [r["id"] for r in results] == [1, 3]
    assert results[0]["match_percentage"] == 80.0


# ---- Flask integration tests ----

def test_recommendations_page_shows_similar_recipes(app, client, alice):
    create_recipe(client, "Paneer Butter Masala", "paneer, tomato, butter, cream",
                  cuisine="Indian", meal_category="Dinner")
    create_recipe(client, "Paneer Tikka", "paneer, yogurt, spices",
                  cuisine="Indian", meal_category="Dinner")
    create_recipe(client, "Chicken Manchurian", "chicken, soy sauce, garlic",
                  cuisine="Chinese", meal_category="Dinner", is_vegetarian="nonveg")

    with app.app_context():
        target_id = Recipe.query.filter_by(name="Paneer Butter Masala").first().id

    r = client.get(f"/recommendations/?recipe_id={target_id}")
    assert b"Paneer Tikka" in r.data
    assert b"% match" in r.data


def test_recommendations_page_empty_catalog_does_not_crash(client):
    r = client.get("/recommendations/")
    assert r.status_code == 200


def test_similar_recipes_shown_on_detail_page(app, client, alice):
    create_recipe(client, "Paneer Butter Masala", "paneer, tomato, butter, cream", cuisine="Indian")
    create_recipe(client, "Paneer Tikka", "paneer, yogurt, spices", cuisine="Indian")

    with app.app_context():
        target_id = Recipe.query.filter_by(name="Paneer Butter Masala").first().id

    r = client.get(f"/recipes/{target_id}")
    assert b"Paneer Tikka" in r.data


def test_ingredient_finder_page(client, alice):
    create_recipe(client, "Aloo Tikki", "potato, onion, tomato, spices")
    create_recipe(client, "Chicken Curry", "chicken, garlic, soy sauce")

    r = client.get("/recommendations/ingredient-finder?ingredients=potato,+onion,+tomato")
    assert b"Aloo Tikki" in r.data
    assert b"Chicken Curry" not in r.data
    assert b"% match" in r.data


def test_ingredient_finder_no_matches_shows_message(client, alice):
    create_recipe(client, "Aloo Tikki", "potato, onion, tomato")
    r = client.get("/recommendations/ingredient-finder?ingredients=kryptonite")
    assert b"No recipes share" in r.data
