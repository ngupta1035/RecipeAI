from flask import render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from datetime import datetime

from app.recipes import bp
from app.extensions import db
from app.models import Recipe, Rating, Favorite, RecentlyViewed
from app.recipes.forms import (
    RecipeForm, DeleteForm, FavoriteForm, RatingForm,
    CUISINE_CHOICES, MEAL_CHOICES, DIFFICULTY_CHOICES,
)
from app.recipes.utils import save_recipe_image, delete_recipe_image


from app.recommendations.service import recommend_similar


def _owns_recipe(recipe):
    return current_user.is_authenticated and (
        recipe.user_id == current_user.id or current_user.is_admin
    )


def _resolve_category_shortcut(args):
    """Homepage category pills link here with a single ?category= value.
    Map it onto the right filter (cuisine, meal, or veg type)."""
    category = args.get("category")
    if not category:
        return None, None, None

    cuisine_values = {c[0] for c in CUISINE_CHOICES}
    meal_values = {c[0] for c in MEAL_CHOICES}

    if category in cuisine_values:
        return category, None, None
    if category in meal_values:
        return None, category, None
    if category == "Vegetarian":
        return None, None, "veg"
    if category == "Non-Vegetarian":
        return None, None, "nonveg"
    return None, None, None


@bp.route("/")
def explore():
    q = request.args.get("q", "").strip()
    cuisine = request.args.get("cuisine", "").strip()
    meal_category = request.args.get("meal_category", "").strip()
    veg = request.args.get("veg", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    max_time = request.args.get("max_time", "").strip()
    sort = request.args.get("sort", "newest").strip()
    page = request.args.get("page", 1, type=int)

    # Homepage category pills provide a single ?category= shortcut
    shortcut_cuisine, shortcut_meal, shortcut_veg = _resolve_category_shortcut(request.args)
    cuisine = cuisine or shortcut_cuisine or ""
    meal_category = meal_category or shortcut_meal or ""
    veg = veg or shortcut_veg or ""

    # Average-rating subquery, joined so we can sort by it
    rating_subq = (
        db.session.query(
            Rating.recipe_id.label("recipe_id"),
            func.avg(Rating.value).label("avg_rating"),
        )
        .group_by(Rating.recipe_id)
        .subquery()
    )

    query = Recipe.query.outerjoin(
        rating_subq, Recipe.id == rating_subq.c.recipe_id
    )

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Recipe.name.ilike(like),
                Recipe.ingredients.ilike(like),
                Recipe.cuisine.ilike(like),
            )
        )

    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)

    if meal_category:
        query = query.filter(Recipe.meal_category == meal_category)

    if veg == "veg":
        query = query.filter(Recipe.is_vegetarian.is_(True))
    elif veg == "nonveg":
        query = query.filter(Recipe.is_vegetarian.is_(False))

    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)

    if max_time.isdigit():
        query = query.filter(
            Recipe.cook_time.isnot(None), Recipe.cook_time <= int(max_time)
        )

    if sort == "rating":
        query = query.order_by(rating_subq.c.avg_rating.desc().nullslast())
    elif sort == "time":
        query = query.order_by(Recipe.cook_time.asc().nullslast())
    else:
        sort = "newest"
        query = query.order_by(Recipe.created_at.desc())

    per_page = current_app.config.get("RECIPES_PER_PAGE", 12)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    filters = {
        "q": q, "cuisine": cuisine, "meal_category": meal_category,
        "veg": veg, "difficulty": difficulty, "max_time": max_time, "sort": sort,
    }

    return render_template(
        "recipes/explore.html",
        recipes=pagination.items,
        pagination=pagination,
        filters=filters,
        cuisine_choices=CUISINE_CHOICES,
        meal_choices=MEAL_CHOICES,
        difficulty_choices=DIFFICULTY_CHOICES,
    )


@bp.route("/favorites")
@login_required
def favorites():
    favorite_recipes = (
        Recipe.query.join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return render_template("recipes/favorites.html", recipes=favorite_recipes)


@bp.route("/<int:recipe_id>")
def detail(recipe_id):
    """Recipe detail view. Similar-recipe recommendations arrive in Phase 6."""
    recipe = Recipe.query.get_or_404(recipe_id)
    delete_form = DeleteForm()
    favorite_form = FavoriteForm()
    rating_form = RatingForm()
    can_manage = _owns_recipe(recipe)

    is_favorited = False
    user_rating = None
    if current_user.is_authenticated:
        is_favorited = (
            Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
            is not None
        )
        existing_rating = Rating.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        user_rating = existing_rating.value if existing_rating else None

        existing_view = RecentlyViewed.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if existing_view:
            existing_view.viewed_at = datetime.utcnow()
        else:
            db.session.add(RecentlyViewed(user_id=current_user.id, recipe_id=recipe.id))
        db.session.commit()

    similar_recipes = recommend_similar(recipe.id, top_n=5)

    return render_template(
        "recipes/detail.html",
        recipe=recipe,
        delete_form=delete_form,
        favorite_form=favorite_form,
        rating_form=rating_form,
        can_manage=can_manage,
        is_favorited=is_favorited,
        user_rating=user_rating,
        similar_recipes=similar_recipes,
    )


@bp.route("/<int:recipe_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = FavoriteForm()
    if not form.validate_on_submit():
        flash("Could not verify that request. Please try again.", "danger")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))

    existing = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from favorites.", "info")
    else:
        db.session.add(Favorite(user_id=current_user.id, recipe_id=recipe.id))
        db.session.commit()
        flash("Added to favorites!", "success")

    return redirect(url_for("recipes.detail", recipe_id=recipe.id))


@bp.route("/<int:recipe_id>/rate", methods=["POST"])
@login_required
def rate(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = RatingForm()

    if not form.validate_on_submit():
        flash("Please choose a rating from 1 to 5.", "danger")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))

    existing = Rating.query.filter_by(
        user_id=current_user.id, recipe_id=recipe.id
    ).first()

    if existing:
        existing.value = form.value.data
        flash("Rating updated!", "success")
    else:
        db.session.add(
            Rating(user_id=current_user.id, recipe_id=recipe.id, value=form.value.data)
        )
        flash("Thanks for rating!", "success")

    db.session.commit()
    return redirect(url_for("recipes.detail", recipe_id=recipe.id))


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = RecipeForm()

    if form.validate_on_submit():
        try:
            image_filename = save_recipe_image(form.image.data)
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("recipes/recipe_form.html", form=form, mode="add")

        recipe = Recipe(
            name=form.name.data.strip(),
            description=(form.description.data or "").strip() or None,
            ingredients=form.ingredients.data.strip(),
            instructions=form.instructions.data.strip(),
            cuisine=form.cuisine.data or None,
            meal_category=form.meal_category.data or None,
            is_vegetarian=(form.is_vegetarian.data == "veg"),
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            difficulty=form.difficulty.data or None,
            image_filename=image_filename,
            author=current_user,
        )
        db.session.add(recipe)
        db.session.commit()

        flash("Recipe added!", "success")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))

    return render_template("recipes/recipe_form.html", form=form, mode="add")


@bp.route("/<int:recipe_id>/edit", methods=["GET", "POST"])
@login_required
def edit(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if not _owns_recipe(recipe):
        abort(403)

    form = RecipeForm()

    if request.method == "GET":
        form.name.data = recipe.name
        form.description.data = recipe.description
        form.ingredients.data = recipe.ingredients
        form.instructions.data = recipe.instructions
        form.cuisine.data = recipe.cuisine
        form.meal_category.data = recipe.meal_category
        form.is_vegetarian.data = "veg" if recipe.is_vegetarian else "nonveg"
        form.prep_time.data = recipe.prep_time
        form.cook_time.data = recipe.cook_time
        form.difficulty.data = recipe.difficulty

    if form.validate_on_submit():
        if form.image.data:
            try:
                new_filename = save_recipe_image(form.image.data)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template(
                    "recipes/recipe_form.html", form=form, mode="edit", recipe=recipe
                )
            delete_recipe_image(recipe.image_filename)
            recipe.image_filename = new_filename

        recipe.name = form.name.data.strip()
        recipe.description = (form.description.data or "").strip() or None
        recipe.ingredients = form.ingredients.data.strip()
        recipe.instructions = form.instructions.data.strip()
        recipe.cuisine = form.cuisine.data or None
        recipe.meal_category = form.meal_category.data or None
        recipe.is_vegetarian = (form.is_vegetarian.data == "veg")
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.difficulty = form.difficulty.data or None

        db.session.commit()
        flash("Recipe updated!", "success")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))

    return render_template(
        "recipes/recipe_form.html", form=form, mode="edit", recipe=recipe
    )


@bp.route("/<int:recipe_id>/delete", methods=["POST"])
@login_required
def delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if not _owns_recipe(recipe):
        abort(403)

    form = DeleteForm()
    if not form.validate_on_submit():
        flash("Could not verify that request. Please try again.", "danger")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))

    delete_recipe_image(recipe.image_filename)
    db.session.delete(recipe)
    db.session.commit()

    flash("Recipe deleted.", "info")
    return redirect(url_for("recipes.explore"))
