from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField, RadioField, SubmitField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

CUISINE_CHOICES = [
    ("Indian", "Indian"), ("Chinese", "Chinese"), ("Italian", "Italian"),
    ("Mexican", "Mexican"), ("Continental", "Continental"), ("Thai", "Thai"),
    ("Other", "Other"),
]

MEAL_CHOICES = [
    ("Breakfast", "Breakfast"), ("Lunch", "Lunch"), ("Dinner", "Dinner"),
    ("Snack", "Snack"), ("Dessert", "Dessert"),
]

DIFFICULTY_CHOICES = [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")]

VEG_CHOICES = [("veg", "Vegetarian"), ("nonveg", "Non-Vegetarian")]


class RecipeForm(FlaskForm):
    name = StringField(
        "Recipe Name", validators=[DataRequired(), Length(min=2, max=150)]
    )
    description = TextAreaField(
        "Description", validators=[Optional(), Length(max=500)]
    )
    ingredients = TextAreaField(
        "Ingredients",
        validators=[DataRequired(message="List at least one ingredient.")],
    )
    instructions = TextAreaField(
        "Instructions",
        validators=[DataRequired(message="Cooking instructions are required.")],
    )
    cuisine = SelectField("Cuisine", choices=CUISINE_CHOICES, validators=[Optional()])
    meal_category = SelectField(
        "Meal Category", choices=MEAL_CHOICES, validators=[Optional()]
    )
    is_vegetarian = RadioField(
        "Type", choices=VEG_CHOICES, default="veg", validators=[DataRequired()]
    )
    prep_time = IntegerField(
        "Prep Time (minutes)",
        validators=[Optional(), NumberRange(min=0, max=1440, message="Enter a realistic time in minutes.")],
    )
    cook_time = IntegerField(
        "Cook Time (minutes)",
        validators=[Optional(), NumberRange(min=0, max=1440, message="Enter a realistic time in minutes.")],
    )
    difficulty = SelectField(
        "Difficulty", choices=DIFFICULTY_CHOICES, validators=[Optional()]
    )
    image = FileField(
        "Recipe Image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp"],
                "Only image files (jpg, jpeg, png, gif, webp) are allowed.",
            )
        ],
    )
    submit = SubmitField("Save Recipe")


class DeleteForm(FlaskForm):
    """Empty form used purely to attach a CSRF token to delete buttons."""
    submit = SubmitField("Delete")


class FavoriteForm(FlaskForm):
    """Empty form used purely to attach a CSRF token to the favorite toggle."""
    submit = SubmitField("Toggle Favorite")


class RatingForm(FlaskForm):
    value = IntegerField(
        "Rating", validators=[DataRequired(), NumberRange(min=1, max=5, message="Choose a rating from 1 to 5.")]
    )
    submit = SubmitField("Rate")
