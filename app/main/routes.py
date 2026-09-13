from flask import render_template

from app.main import bp
from app.models import Recipe

CATEGORIES = [
    "Indian", "Chinese", "Italian", "Breakfast",
    "Lunch", "Dinner", "Dessert", "Vegetarian", "Non-Vegetarian",
]


@bp.route("/")
def home():
    featured_recipes = (
        Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    )
    return render_template(
        "index.html", featured_recipes=featured_recipes, categories=CATEGORIES
    )
