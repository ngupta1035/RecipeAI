"""Bridges Flask/SQLAlchemy Recipe rows to the Flask-independent
recommendation engine in recommendation.py at the project root."""

from recommendation import (
    build_recipe_dataframe,
    compute_similarity_matrix,
    get_similar_recipes,
    explain_similarity,
    tokenize_ingredients,
    match_recipes_by_ingredients,
)
from app.models import Recipe


def _recipe_to_record(recipe):
    return {
        "id": recipe.id,
        "name": recipe.name,
        "ingredients": recipe.ingredients,
        "cuisine": recipe.cuisine,
        "meal_category": recipe.meal_category,
        "is_vegetarian": recipe.is_vegetarian,
    }


def recommend_similar(recipe_id, top_n=5):
    """Return up to top_n recipes similar to recipe_id, each as
    {"recipe": Recipe, "score": float, "reasons": [str, ...]}."""
    recipes = Recipe.query.all()
    records = [_recipe_to_record(r) for r in recipes]

    df = build_recipe_dataframe(records)
    similarity_matrix = compute_similarity_matrix(df)
    similar = get_similar_recipes(recipe_id, df, similarity_matrix, top_n=top_n)

    recipe_map = {r.id: r for r in recipes}
    record_map = {rec["id"]: rec for rec in records}
    base_record = record_map.get(recipe_id)

    results = []
    for item in similar:
        candidate_recipe = recipe_map.get(item["id"])
        candidate_record = record_map.get(item["id"])
        if not candidate_recipe or not candidate_record or not base_record:
            continue
        results.append(
            {
                "recipe": candidate_recipe,
                "score": item["score"],
                "reasons": explain_similarity(base_record, candidate_record),
            }
        )
    return results


def find_recipes_by_ingredients(ingredients_text, min_match=1):
    """Ingredient-based recipe finder (Phase 7). Returns
    (results, available_ingredients) where results is a list of
    {"recipe", "matching", "missing", "match_percentage"} sorted by best
    match first, and available_ingredients is the parsed set of what the
    user said they have (handy for showing "you entered: ...")."""
    available = tokenize_ingredients(ingredients_text)
    if not available:
        return [], available

    recipes = Recipe.query.all()
    records = [{"id": r.id, "ingredients": r.ingredients} for r in recipes]
    matches = match_recipes_by_ingredients(available, records, min_match=min_match)

    recipe_map = {r.id: r for r in recipes}
    results = []
    for m in matches:
        recipe_obj = recipe_map.get(m["id"])
        if not recipe_obj:
            continue
        results.append(
            {
                "recipe": recipe_obj,
                "matching": m["matching"],
                "missing": m["missing"],
                "match_percentage": m["match_percentage"],
            }
        )
    return results, available
