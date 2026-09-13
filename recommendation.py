"""Content-based recipe recommendation engine.

This module is intentionally Flask- and database-agnostic: it works on
plain lists of dicts in and returns plain lists of dicts out. That keeps
the ML logic easy to test, profile, or swap out (e.g. for a different
vectorizer) without touching any Flask route code. The Flask-facing glue
that pulls Recipe rows from the database and calls into this module lives
in app/recommendations/service.py.

Pipeline:
1. Combine each recipe's name, ingredients, cuisine, meal category, and
   veg/non-veg classification into one text blob.
2. Vectorize all blobs with TF-IDF.
3. Compare recipes pairwise with cosine similarity.
4. For a given recipe, return the top-N most similar others.
"""

import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQUIRED_FIELDS = ("id", "name", "ingredients", "cuisine", "meal_category", "is_vegetarian")


def _combined_features(row):
    """Combine a recipe's text-bearing fields into one string for TF-IDF."""
    veg_label = "vegetarian" if row.get("is_vegetarian") else "non-vegetarian"
    parts = [
        row.get("name") or "",
        row.get("ingredients") or "",
        row.get("cuisine") or "",
        row.get("meal_category") or "",
        veg_label,
    ]
    return " ".join(str(p) for p in parts if p)


def build_recipe_dataframe(recipes):
    """Turn a list of recipe dicts into a DataFrame with a combined_features
    column ready for vectorization. Each dict should have at least the keys
    in REQUIRED_FIELDS."""
    df = pd.DataFrame(list(recipes))
    if df.empty:
        return df
    df["combined_features"] = df.apply(_combined_features, axis=1)
    return df


def compute_similarity_matrix(df):
    """Fit TF-IDF over the combined_features column and return the full
    cosine-similarity matrix (n_recipes x n_recipes), or None if there's
    nothing to compare."""
    if df is None or df.empty or len(df) < 2:
        return None
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["combined_features"])
    return cosine_similarity(tfidf_matrix)


def get_similar_recipes(recipe_id, df, similarity_matrix, top_n=5):
    """Return up to top_n most similar recipes to recipe_id, as a list of
    {"id": ..., "score": ...} dicts sorted by descending similarity.
    Recipes with zero similarity (no overlapping terms at all) are excluded."""
    if df is None or df.empty or similarity_matrix is None:
        return []

    id_list = df["id"].tolist()
    if recipe_id not in id_list:
        return []

    idx = id_list.index(recipe_id)
    scored = list(enumerate(similarity_matrix[idx]))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    results = []
    for i, score in scored:
        if i == idx or score <= 0:
            continue
        results.append({"id": id_list[i], "score": float(score)})
        if len(results) >= top_n:
            break
    return results


def tokenize_ingredients(text):
    """Split a free-text ingredient list (comma or newline separated) into
    a normalized set of lowercase tokens. Used both to compare two recipes'
    ingredient lists and to parse what a user says they have on hand."""
    if not text:
        return set()
    tokens = re.split(r"[,\n]+", text.lower())
    return {t.strip() for t in tokens if t.strip()}


def explain_similarity(base, candidate):
    """Return a short list of human-readable reasons two recipe records
    (dicts) were considered similar - used to make recommendations
    explainable rather than a black box."""
    reasons = []

    if base.get("cuisine") and base.get("cuisine") == candidate.get("cuisine"):
        reasons.append(f"Same cuisine ({base['cuisine']})")

    if base.get("meal_category") and base.get("meal_category") == candidate.get("meal_category"):
        reasons.append(f"Same meal category ({base['meal_category']})")

    if base.get("is_vegetarian") == candidate.get("is_vegetarian"):
        reasons.append("Both vegetarian" if base.get("is_vegetarian") else "Both non-vegetarian")

    shared_ingredients = tokenize_ingredients(base.get("ingredients")) & tokenize_ingredients(
        candidate.get("ingredients")
    )
    if shared_ingredients:
        sample = ", ".join(sorted(shared_ingredients)[:3])
        reasons.append(f"Shares ingredients: {sample}")

    return reasons


def match_recipes_by_ingredients(available_ingredients, recipes, min_match=1):
    """Ingredient-based recipe finder (Phase 7).

    available_ingredients: a set of normalized ingredient tokens the user
        currently has on hand (see tokenize_ingredients).
    recipes: iterable of dicts with at least "id" and "ingredients".
    min_match: a recipe must share at least this many ingredients with the
        user's list to be included at all.

    Returns a list of {"id", "matching", "missing", "match_percentage"}
    dicts, sorted by highest match percentage first, then by fewest
    missing ingredients.
    """
    results = []
    for recipe in recipes:
        recipe_ingredients = tokenize_ingredients(recipe.get("ingredients"))
        if not recipe_ingredients:
            continue

        matching = available_ingredients & recipe_ingredients
        if len(matching) < min_match:
            continue

        missing = recipe_ingredients - available_ingredients
        match_percentage = round(len(matching) / len(recipe_ingredients) * 100, 1)

        results.append(
            {
                "id": recipe["id"],
                "matching": sorted(matching),
                "missing": sorted(missing),
                "match_percentage": match_percentage,
            }
        )

    results.sort(key=lambda r: (-r["match_percentage"], len(r["missing"])))
    return results
