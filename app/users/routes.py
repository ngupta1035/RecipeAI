from flask import render_template
from flask_login import login_required, current_user

from app.users import bp
from app.models import Recipe, Favorite, RecentlyViewed, Rating
from app.recommendations.service import recommend_similar


@bp.route("/dashboard")
@login_required
def dashboard():
    my_recipes = (
        Recipe.query.filter_by(user_id=current_user.id)
        .order_by(Recipe.created_at.desc())
        .all()
    )

    favorite_recipes = (
        Recipe.query.join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .limit(6)
        .all()
    )

    recently_viewed = (
        Recipe.query.join(RecentlyViewed, RecentlyViewed.recipe_id == Recipe.id)
        .filter(RecentlyViewed.user_id == current_user.id)
        .order_by(RecentlyViewed.viewed_at.desc())
        .limit(6)
        .all()
    )

    # Personalized recommendations: seed off the most recent favorite, or
    # failing that the most recently viewed recipe.
    seed_recipe = favorite_recipes[0] if favorite_recipes else (
        recently_viewed[0] if recently_viewed else None
    )
    recommendations = recommend_similar(seed_recipe.id, top_n=4) if seed_recipe else []

    stats = {
        "total_recipes": len(my_recipes),
        "total_favorites": Favorite.query.filter_by(user_id=current_user.id).count(),
        "total_ratings_given": Rating.query.filter_by(user_id=current_user.id).count(),
    }

    return render_template(
        "users/dashboard.html",
        my_recipes=my_recipes[:6],
        my_recipes_total=len(my_recipes),
        favorite_recipes=favorite_recipes,
        recently_viewed=recently_viewed,
        recommendations=recommendations,
        seed_recipe=seed_recipe,
        stats=stats,
    )
