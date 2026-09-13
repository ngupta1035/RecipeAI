from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recipes = db.relationship(
        "Recipe", backref="author", lazy="dynamic", cascade="all, delete-orphan"
    )
    favorites = db.relationship(
        "Favorite", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    ratings = db.relationship(
        "Rating", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    recently_viewed = db.relationship(
        "RecentlyViewed", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    cuisine = db.Column(db.String(50), index=True)
    meal_category = db.Column(db.String(50), index=True)
    is_vegetarian = db.Column(db.Boolean, default=True)

    prep_time = db.Column(db.Integer)  # minutes
    cook_time = db.Column(db.Integer)  # minutes
    difficulty = db.Column(db.String(20))  # Easy / Medium / Hard

    image_filename = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship(
        "Favorite", backref="recipe", lazy="dynamic", cascade="all, delete-orphan"
    )
    ratings = db.relationship(
        "Rating", backref="recipe", lazy="dynamic", cascade="all, delete-orphan"
    )
    recently_viewed = db.relationship(
        "RecentlyViewed", backref="recipe", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def average_rating(self):
        ratings = [r.value for r in self.ratings]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def rating_count(self):
        return self.ratings.count()

    @property
    def total_time(self):
        return (self.prep_time or 0) + (self.cook_time or 0)

    def __repr__(self):
        return f"<Recipe {self.name}>"


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_favorite"),
    )


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_rating"),
        db.CheckConstraint("value >= 1 AND value <= 5", name="ck_rating_value_range"),
    )


class RecentlyViewed(db.Model):
    __tablename__ = "recently_viewed"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_view"),
    )
