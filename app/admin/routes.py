from flask import render_template, redirect, url_for, flash
from sqlalchemy import func

from app.admin import bp
from app.admin.decorators import admin_required
from app.extensions import db
from app.models import User, Recipe, Favorite, Rating
from app.recipes.forms import DeleteForm
from app.recipes.utils import delete_recipe_image


@bp.route("/")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_recipes = Recipe.query.count()
    total_favorites = Favorite.query.count()
    total_ratings = Rating.query.count()

    # "Popular" = most favorited, as a simple, gameable-resistant proxy
    # distinct from average star rating (which rewards few high scores).
    popular_recipes = (
        db.session.query(Recipe, func.count(Favorite.id).label("favorite_count"))
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .group_by(Recipe.id)
        .order_by(func.count(Favorite.id).desc())
        .limit(5)
        .all()
    )

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_recipes=total_recipes,
        total_favorites=total_favorites,
        total_ratings=total_ratings,
        popular_recipes=popular_recipes,
        recent_users=recent_users,
        recent_recipes=recent_recipes,
    )


@bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/recipes")
@admin_required
def recipes():
    all_recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    delete_form = DeleteForm()
    return render_template("admin/recipes.html", recipes=all_recipes, delete_form=delete_form)


@bp.route("/recipes/<int:recipe_id>/delete", methods=["POST"])
@admin_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = DeleteForm()
    if not form.validate_on_submit():
        flash("Could not verify that request. Please try again.", "danger")
        return redirect(url_for("admin.recipes"))

    delete_recipe_image(recipe.image_filename)
    db.session.delete(recipe)
    db.session.commit()

    flash(f'Deleted recipe "{recipe.name}".', "info")
    return redirect(url_for("admin.recipes"))
