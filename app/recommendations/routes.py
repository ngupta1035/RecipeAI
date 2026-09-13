from flask import render_template, request

from app.recommendations import bp
from app.recommendations.service import recommend_similar, find_recipes_by_ingredients
from app.models import Recipe


@bp.route("/")
def index():
    recipes = Recipe.query.order_by(Recipe.name.asc()).all()
    selected_id = request.args.get("recipe_id", type=int)

    selected_recipe = None
    recommendations = []

    if selected_id:
        selected_recipe = Recipe.query.get(selected_id)
        if selected_recipe:
            recommendations = recommend_similar(selected_id, top_n=5)

    return render_template(
        "recommendations/index.html",
        recipes=recipes,
        selected_recipe=selected_recipe,
        recommendations=recommendations,
    )


@bp.route("/ingredient-finder")
def ingredient_finder():
    ingredients_text = request.args.get("ingredients", "").strip()

    results = []
    available = set()
    if ingredients_text:
        results, available = find_recipes_by_ingredients(ingredients_text)

    return render_template(
        "recommendations/finder.html",
        ingredients_text=ingredients_text,
        results=results,
        available=sorted(available),
    )
