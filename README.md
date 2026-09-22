# RecipeAI — Smart Recipe Recommendation System

A full-stack Flask web application for discovering, managing, and getting personalized recipe recommendations using a content-based machine learning engine built with TF-IDF and cosine similarity.

RecipeAI combines recipe discovery, ingredient-based search, user accounts, ratings, favorites, dashboards, and machine-learning recommendations into a single web application.

Built incrementally as an academic project across 10 development phases, with automated testing, security hardening, database migrations, and deployment support.

---

## Features

### 👤 User Accounts

- User registration and login
- Secure password hashing using Werkzeug
- Session management with Flask-Login
- Case-insensitive username uniqueness
- Password validation
- User profile/dashboard

### 🍳 Recipe Management

- Create, view, edit, and delete recipes
- Owner-only recipe modification
- Recipe image uploads
- Image content verification using Pillow
- Randomized image filenames
- Maximum upload size protection
- Recipe categories and cuisines
- Vegetarian/non-vegetarian classification
- Preparation and cooking time
- Difficulty levels

### 🔎 Recipe Discovery

Search and explore recipes using:

- Recipe name
- Ingredients
- Cuisine
- Meal category
- Vegetarian/non-vegetarian
- Maximum cooking time
- Difficulty

Additional functionality:

- Sorting
- Pagination
- Shareable and bookmarkable filtered URLs

### ⭐ Favorites & Ratings

- Add/remove recipes from favorites
- Rate recipes from 1–5 stars
- Average rating calculation
- Rating count
- Prevents duplicate ratings for the same user and recipe

### 🤖 Machine Learning Recommendations

RecipeAI includes a content-based recommendation system built using:

- TF-IDF vectorization
- Cosine similarity
- Recipe name
- Ingredients
- Cuisine
- Meal category
- Vegetarian/non-vegetarian information

The recommendation engine provides:

- Similar recipes
- Top matching recipes
- Match percentage
- Plain-language explanations

Example explanations:

- Same cuisine
- Shares ingredients: paneer, spices

The recommendation engine is implemented independently in `recommendation.py` and can be tested separately from Flask.

### 🥔 Ingredient-Based Recipe Finder

Enter ingredients available in your kitchen, for example:

```text
potato, onion, tomato, paneer
```

RecipeAI then:

- Finds recipes containing matching ingredients
- Calculates a match percentage
- Ranks recipes
- Shows matching ingredients
- Shows missing ingredients

### 📊 User Dashboard

The personal dashboard provides:

- User information
- User-created recipes
- Favorite recipes
- Recently viewed recipes
- Personalized recommendations
- Basic statistics

### 🛠️ Admin Dashboard

Role-based admin functionality includes:

- Total users
- Total recipes
- Total favorites
- Total ratings
- Most-favorited recipes
- Newest users
- Newest recipes
- User management
- Recipe management
- Recipe deletion
- Access control using an admin-only decorator

### 🔐 Security

Security features include:

- CSRF protection
- Password hashing
- Secure session cookies
- `HttpOnly` cookies
- `SameSite=Lax`
- `Secure` cookies in production
- Security response headers
- Image content verification
- File upload validation
- Random image filenames
- Upload size restrictions
- Production protection against default `SECRET_KEY`
- Case-insensitive username uniqueness
- Minimum password length validation

---

# Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Architecture | Flask Application Factory + Blueprints |
| Database | SQLAlchemy ORM |
| Development Database | SQLite |
| Production Database | PostgreSQL / MySQL |
| Migrations | Flask-Migrate / Alembic |
| Authentication | Flask-Login |
| Password Security | Werkzeug |
| Forms | Flask-WTF / WTForms |
| Machine Learning | Pandas, scikit-learn |
| ML Techniques | TF-IDF, Cosine Similarity |
| Frontend | Jinja2, Bootstrap 5, Bootstrap Icons, JavaScript |
| Image Processing | Pillow |
| Testing | pytest |
| Production Server | Gunicorn |
| Deployment | Docker / Render / Heroku-style WSGI hosts |

---

# Project Structure

```text
RecipeAI/
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   │
│   ├── auth/
│   │   ├── routes.py
│   │   └── ...
│   │
│   ├── main/
│   │   └── ...
│   │
│   ├── recipes/
│   │   └── ...
│   │
│   ├── recommendations/
│   │   └── ...
│   │
│   ├── users/
│   │   └── ...
│   │
│   ├── admin/
│   │   └── ...
│   │
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/
│
├── migrations/
│   └── versions/
│
├── seed/
│   ├── recipes.json
│   ├── seed_database.py
│   └── images/
│
├── tests/
│
├── instance/
│   └── database.db
│
├── recommendation.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
├── Procfile
├── render.yaml
├── LICENSE
├── run.py
└── README.md
```

> `instance/database.db` is a local development database and is intentionally excluded from version control.

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/ngupta1035/RecipeAI.git
cd RecipeAI
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example environment file.

### Windows

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Open `.env` and configure your secret key.

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Example:

```env
SECRET_KEY=your-generated-secret-key
FLASK_CONFIG=development
```

Do **not** commit `.env` to GitHub.

---

# Database Setup

RecipeAI uses Flask-Migrate and Alembic for database migrations.

Run:

```bash
flask db upgrade
```

This creates the required database tables.

The migrations include tables for:

- Users
- Recipes
- Favorites
- Ratings
- Recently viewed recipes

If you modify a model, generate a migration:

```bash
flask db migrate -m "Describe your change"
```

Then apply it:

```bash
flask db upgrade
```

Do not delete migrations or manually modify the production database schema.

---

# Loading the Sample Recipe Data

The repository contains a reproducible seed package with:

- 74 sample recipes
- 74 recipe images
- A seed/import script

The seed files are located in:

```text
seed/
├── recipes.json
├── seed_database.py
└── images/
```

After creating the database with:

```bash
flask db upgrade
```

run:

```bash
python seed/seed_database.py
```

The script:

1. Loads the recipe data from `seed/recipes.json`
2. Validates the recipe count
3. Validates referenced images
4. Creates a dedicated `RecipeAI` seed user
5. Copies recipe images
6. Imports the recipes
7. Verifies the final recipe count

The seed script intentionally refuses to run if recipes already exist in the database. This prevents accidental duplicate imports.

The seed data does **not** contain the original application's users, passwords, favorites, ratings, or recently viewed records.

---

# Run the Application

Start the Flask application:

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes in production | Development placeholder | Flask session/security key |
| `FLASK_CONFIG` | No | `development` | Application configuration |
| `DATABASE_URL` | No | SQLite | SQLAlchemy database URL |

Supported configuration values include:

```text
development
production
testing
```

For production, always use a strong randomly generated `SECRET_KEY`.

---

# Authentication and Authorization

RecipeAI uses Flask-Login for session management.

Passwords are never stored as plaintext.

Passwords are hashed using Werkzeug's password hashing functionality.

Users can:

- Register
- Log in
- Log out
- Manage recipes
- Favorite recipes
- Rate recipes
- View their dashboard

Administrative functionality is protected by an admin-only authorization decorator.

There is no self-service admin registration.

To promote a user to admin in a local development environment:

```bash
flask --app run.py shell
```

Then:

```python
from app.extensions import db
from app.models import User

u = User.query.filter_by(username="yourusername").first()
u.is_admin = True
db.session.commit()
```

---

# Running Tests

Run the complete test suite:

```bash
pytest
```

The project contains 51 automated tests covering:

- Authentication
- Recipe CRUD
- Recipe ownership
- Image upload validation
- Search
- Filtering
- Sorting
- Pagination
- Favorites
- Ratings
- Duplicate-rating prevention
- Recommendation engine
- Recommendation routes
- Ingredient finder
- User dashboard
- Admin access control

The test configuration uses in-memory SQLite and disables CSRF for testing.

---

# Screenshots

Screenshots can be added under:

```text
docs/screenshots/
```

Recommended screenshots:

1. Homepage
2. Explore page with filters
3. Recipe detail page
4. Similar recipe recommendations
5. Recommendations page
6. Ingredient Finder
7. User dashboard
8. Admin dashboard

Example:

```markdown
![RecipeAI Homepage](docs/screenshots/homepage.png)

![Recipe Detail](docs/screenshots/recipe-detail.png)

![Recommendations](docs/screenshots/recommendations.png)

![Ingredient Finder](docs/screenshots/ingredient-finder.png)
```

---

# Machine Learning Recommendation Engine

RecipeAI uses a content-based recommendation system.

The recommendation engine combines multiple recipe attributes:

```text
Recipe Name
Ingredients
Cuisine
Meal Category
Vegetarian / Non-Vegetarian
```

These attributes are converted into TF-IDF vectors.

Cosine similarity is then used to determine how similar recipes are.

Conceptually:

```text
Recipe Data
     │
     ▼
Text Feature Combination
     │
     ▼
TF-IDF Vectorization
     │
     ▼
Cosine Similarity
     │
     ▼
Similarity Ranking
     │
     ▼
Top Recommended Recipes
```

The recommendation system powers:

- Similar Recipes on recipe detail pages
- Dedicated Recommendations page
- Match percentages
- Plain-language recommendation explanations

The engine is implemented in:

```text
recommendation.py
```

and is designed to remain Flask-independent for easier testing.

---
# Ingredient-Based Recipe Finder

The Ingredient Finder uses set-based ingredient matching.

Example input:

```text
potato, onion, tomato, paneer
```

The system compares the entered ingredients with recipe ingredients and calculates a match percentage.

Results include:

```text
Recipe
Match %
Matching Ingredients
Missing Ingredients
```

Recipes are ranked according to ingredient overlap.

---

# Deployment

RecipeAI includes deployment configuration for:

- Render
- Docker
- Heroku-style WSGI platforms
- Other Python WSGI hosts

For production, configure:

```env
SECRET_KEY=<strong-random-secret>
FLASK_CONFIG=production
DATABASE_URL=<production-database-url>
```

Never commit production secrets to GitHub.

---

# Render Deployment

A `render.yaml` Blueprint configuration is included.

General deployment flow:

```text
GitHub Repository
       │
       ▼
Render Blueprint
       │
       ├── Web Service
       │
       └── PostgreSQL Database
```

### Deployment Steps

1. Push the repository to GitHub.
2. Open Render.
3. Select **New + → Blueprint**.
4. Connect the GitHub repository.
5. Render reads the included `render.yaml`.
6. Configure the required environment variables.
7. Deploy the application.

Before deploying with PostgreSQL, ensure the required PostgreSQL driver is included in `requirements.txt`.

For production deployments, use:

```env
SECRET_KEY=<strong-random-secret>
FLASK_CONFIG=production
DATABASE_URL=<postgresql-database-url>
```

The application runs database migrations during deployment according to the included deployment configuration.

---

# Docker

Build the Docker image:

```bash
docker build -t recipeai .
```

Run the application:

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  -e FLASK_CONFIG=production \
  -v recipeai_data:/app/instance \
  recipeai
```

The container uses Gunicorn to serve the Flask application.

For persistent data, mount volumes for:

```text
/app/instance
/app/app/static/uploads
```

Alternatively, configure the application to use PostgreSQL or MySQL through `DATABASE_URL`.

---

# Production Configuration

For a production environment:

```env
SECRET_KEY=<strong-random-secret>
FLASK_CONFIG=production
DATABASE_URL=<production-database-url>
```

The application protects against using the default development secret in production.

Production deployments should also use:

- HTTPS
- A production database
- Secure environment variables
- A production WSGI server such as Gunicorn
- Persistent storage for uploaded images
- Regular database backups

---

# Known Limitations

Current limitations include:

- No login-attempt rate limiting
- No password-reset workflow
- Recommendation TF-IDF vectors are recomputed for requests instead of being cached
- Screenshots/demo video are not bundled by default
- SQLite is intended primarily for development

For production deployment, additional infrastructure and security controls may be required.

---

# Future Improvements

Possible future improvements include:

- Login attempt rate limiting
- Password reset and email verification
- Cached recommendation vectors
- Larger recipe datasets
- More advanced recommendation models
- Collaborative filtering
- Hybrid recommendation system
- Nutrition information
- Recipe difficulty personalization
- User preference learning
- Recipe API integration
- Automated CI/CD
- Production monitoring
- Improved image optimization
- Advanced admin moderation tools

---

# Development History

RecipeAI was developed incrementally through multiple phases.

## Phase 1 — Application Foundation

- Flask application factory
- SQLite
- SQLAlchemy
- Shared base template
- Homepage
- Recipe categories

## Phase 2 — Authentication

- Registration
- Login/logout
- Flask-Login
- Password hashing
- Form validation
- Flash messages

## Phase 3 — Recipe CRUD

- Add recipes
- View recipes
- Edit recipes
- Delete recipes
- Owner-only modification
- Image uploads
- Image validation
- Upload size restrictions

## Phase 4 — Search & Discovery

- Search
- Cuisine filtering
- Meal-category filtering
- Vegetarian filtering
- Cooking-time filtering
- Difficulty filtering
- Sorting
- Pagination

## Phase 5 — Favorites & Ratings

- Favorites
- 1–5 star ratings
- Average ratings
- Rating counts
- Duplicate-rating prevention

## Phase 6 — ML Recommendations

- TF-IDF
- Cosine similarity
- Similar recipes
- Match percentages
- Recommendation explanations

## Phase 7 — Ingredient Finder

- Ingredient matching
- Match percentage
- Matching ingredients
- Missing ingredients
- Ranked results

## Phase 8 — Dashboards

- User dashboard
- Favorites
- Recently viewed recipes
- Personalized recommendations
- User statistics
- Admin dashboard
- Role-based authorization

## Phase 9 — Security & Testing

- Image content verification
- CSRF protection
- Security headers
- Hardened cookies
- Production secret-key protection
- Username uniqueness
- Password validation
- Automated tests

## Phase 10 — Deployment Readiness

- Docker support
- Gunicorn
- Render configuration
- Procfile
- Alembic migrations
- PostgreSQL/MySQL readiness
- Deployment documentation
- Project README

---

# Security Notes

This repository intentionally does **not** include:

- `.env`
- Production secrets
- Local SQLite database
- Original user accounts
- User passwords
- User emails
- Favorites from the original database
- Ratings from the original database
- Recently viewed records

The `.gitignore` configuration excludes local databases, environment files, virtual environments, Python cache files, and runtime-uploaded data.

The repository does include sanitized seed data containing the sample recipes and their associated recipe images.

---

# Data & Privacy

The sample recipe dataset included in this repository is separated from the original application's private database.

The seed package contains:

- Recipe information
- Recipe descriptions
- Ingredients
- Instructions
- Cuisine
- Meal category
- Dietary classification
- Preparation/cooking information
- Difficulty
- Recipe image filenames
- Recipe images

The seed package does not include:

- Original application users
- User email addresses
- Password hashes
- Favorites
- Ratings
- Recently viewed records
- Original user IDs

This allows the application to be recreated from a clean database without exposing the original application's user data.

---

# Repository Safety

The repository is configured to keep local and sensitive development files out of version control.

Examples of excluded files include:

```text
.env
instance/*.db
instance/*.sqlite3
venv/
.venv/
__pycache__/
*.pyc
```

The actual SQLite database is created locally after running:

```bash
flask db upgrade
```

The database itself is not required to be committed to GitHub because the schema can be recreated through Flask-Migrate and the sample recipe data can be restored through the seed package.

---

# Reproducible Setup

A fresh installation can recreate the application using the following workflow:

```text
Clone Repository
       │
       ▼
Create Virtual Environment
       │
       ▼
Install Dependencies
       │
       ▼
Configure .env
       │
       ▼
Run Database Migrations
       │
       ▼
Seed Sample Recipes
       │
       ▼
Run Application
       │
       ▼
Open Browser
```

Commands:

```bash
git clone https://github.com/ngupta1035/RecipeAI.git
cd RecipeAI
python -m venv venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment:

```bash
cp .env.example .env
```

Run migrations:

```bash
flask db upgrade
```

Load the sample recipe data:

```bash
python seed/seed_database.py
```

Start the application:

```bash
python run.py
```

Then visit:

```text
http://127.0.0.1:5000
```

---

# Testing Workflow

Before submitting changes to the repository, run:

```bash
pytest
```

Then verify the application locally:

```bash
python run.py
```

Recommended manual checks include:

- Registration
- Login
- Recipe creation
- Recipe editing
- Recipe deletion
- Recipe search
- Filters
- Favorites
- Ratings
- Recommendations
- Ingredient Finder
- User dashboard
- Admin dashboard
- Image uploads

---

# Screenshots & Demo

Screenshots can be stored in:

```text
docs/screenshots/
```

Recommended screenshots include:

- Homepage
- Explore/search page
- Recipe detail page
- Recommendations page
- Ingredient Finder
- User dashboard
- Admin dashboard

A short 2–3 minute demonstration video can also be created showing:

```text
Register
   ↓
Add Recipe
   ↓
Favorite / Rate Recipe
   ↓
View Recommendations
   ↓
Use Ingredient Finder
   ↓
View Dashboard
   ↓
View Admin Features
```

---

# License

MIT License.

See [LICENSE](LICENSE) for details.

---

# Acknowledgments

RecipeAI was developed as an academic project demonstrating:

- Python development
- Flask web development
- Application factory architecture
- Blueprint-based application structure
- Relational database design
- SQLAlchemy ORM
- Authentication and authorization
- CRUD operations
- Data processing
- Machine learning recommendations
- TF-IDF
- Cosine similarity
- Automated testing
- Web security practices
- Docker
- Database migrations
- Deployment practices

---

# Author

**Narayani Gupta**

B.E. — Artificial Intelligence and Data Science

GitHub: [https://github.com/ngupta1035](https://github.com/ngupta1035)

---

# Project Summary

RecipeAI is a full-stack recipe discovery and recommendation platform that combines traditional web application functionality with a content-based machine learning recommendation engine.

The project demonstrates the complete development lifecycle:

```text
Planning
   ↓
Flask Application
   ↓
Database Design
   ↓
Authentication
   ↓
Recipe CRUD
   ↓
Search & Discovery
   ↓
Favorites & Ratings
   ↓
Machine Learning Recommendations
   ↓
Ingredient Finder
   ↓
Dashboards
   ↓
Security Hardening
   ↓
Automated Testing
   ↓
Docker / Deployment
```

The project is designed to be reproducible from a clean installation using database migrations and the included recipe seed data.

## Acknowledgments

Built as an academic project demonstrating Python/Flask web development,
relational database design, authentication, CRUD operations, data
processing, machine learning recommendations, and deployment practices.
