from pathlib import Path
import json
import secrets
import shutil
import sys

# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

SEED_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SEED_ROOT.parent

RECIPES_JSON = SEED_ROOT / "recipes.json"
SEED_IMAGES = SEED_ROOT / "images"

# Make sure Python can import the Flask app
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import User, Recipe


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED_USERNAME = "RecipeAI"
SEED_EMAIL = "recipeai_seed@example.com"

EXPECTED_RECIPE_COUNT = 74


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

def load_recipes():
    if not RECIPES_JSON.exists():
        raise FileNotFoundError(
            f"Missing seed file: {RECIPES_JSON}"
        )

    with RECIPES_JSON.open("r", encoding="utf-8") as f:
        recipes = json.load(f)

    if not isinstance(recipes, list):
        raise ValueError("recipes.json must contain a JSON list.")

    if len(recipes) != EXPECTED_RECIPE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_RECIPE_COUNT} recipes, "
            f"found {len(recipes)}."
        )

    return recipes


def validate_images(recipes):
    missing = []

    for recipe in recipes:
        filename = recipe.get("image_filename")

        if filename:
            image_path = SEED_IMAGES / filename

            if not image_path.is_file():
                missing.append(filename)

    if missing:
        raise FileNotFoundError(
            "Missing recipe images:\n"
            + "\n".join(missing)
        )


# ---------------------------------------------------------
# Main seed process
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("RecipeAI database seeding")
    print("=" * 60)

    recipes = load_recipes()

    print(f"Recipes found in seed file: {len(recipes)}")

    # Validate everything BEFORE modifying the database.
    validate_images(recipes)

    print("All referenced recipe images found.")

    app = create_app()

    with app.app_context():

        existing_recipe_count = Recipe.query.count()

        if existing_recipe_count != 0:
            raise RuntimeError(
                f"Database already contains {existing_recipe_count} "
                "recipes. Seeding stopped to prevent duplicates."
            )

        # -------------------------------------------------
        # Create dedicated seed user
        # -------------------------------------------------

        seed_user = User.query.filter_by(
            username=SEED_USERNAME
        ).first()

        if seed_user is None:

            random_password = secrets.token_urlsafe(32)

            seed_user = User(
                username=SEED_USERNAME,
                email=SEED_EMAIL,
                is_admin=False
            )

            seed_user.set_password(random_password)

            db.session.add(seed_user)
            db.session.flush()

            print(f"Created seed user: {SEED_USERNAME}")

        # -------------------------------------------------
        # Copy images
        # -------------------------------------------------

        upload_dir = PROJECT_ROOT / "app" / "static" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        copied_images = 0

        for recipe in recipes:

            filename = recipe.get("image_filename")

            if not filename:
                continue

            source = SEED_IMAGES / filename
            destination = upload_dir / filename

            if not destination.exists():
                shutil.copy2(source, destination)
                copied_images += 1

        print(f"Images copied: {copied_images}")

        # -------------------------------------------------
        # Import recipes
        # -------------------------------------------------

        imported = 0

        for data in recipes:

            recipe = Recipe(
                name=data.get("name"),
                description=data.get("description"),
                ingredients=data.get("ingredients"),
                instructions=data.get("instructions"),
                cuisine=data.get("cuisine"),
                meal_category=data.get("meal_category"),
                is_vegetarian=data.get("is_vegetarian"),
                prep_time=data.get("prep_time"),
                cook_time=data.get("cook_time"),
                difficulty=data.get("difficulty"),
                image_filename=data.get("image_filename"),
                user_id=seed_user.id,
                created_at=data.get("created_at")
            )

            db.session.add(recipe)
            imported += 1

        db.session.commit()

        # -------------------------------------------------
        # Verification
        # -------------------------------------------------

        final_recipe_count = Recipe.query.count()

        if final_recipe_count != EXPECTED_RECIPE_COUNT:
            raise RuntimeError(
                f"Verification failed. Expected "
                f"{EXPECTED_RECIPE_COUNT} recipes, "
                f"found {final_recipe_count}."
            )

        print()
        print("=" * 60)
        print("SEED SUCCESSFUL")
        print("=" * 60)
        print(f"Recipes imported : {final_recipe_count}")
        print(f"Seed user        : {SEED_USERNAME}")
        print(f"Images copied    : {copied_images}")
        print("=" * 60)


if __name__ == "__main__":
    main()