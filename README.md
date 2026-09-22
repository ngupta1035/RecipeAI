# RecipeAI — Smart Recipe Recommendation System

A full-stack Flask web app for discovering, cooking, and getting recipes
recommended for you — with a content-based machine learning engine
(TF-IDF + cosine similarity) built from scratch, not a wrapper around a
third-party API.

Built incrementally as an academic project across 9 completed phases
(see [Development History](#development-history)), with 51 passing
automated tests.

## Features

- **Accounts** — registration, login/logout, hashed passwords, session
  management via Flask-Login.
- **Recipes** — full CRUD, owner-only edit/delete, image uploads with
  real content verification (not just extension checking).
- **Discovery** — search by name/ingredient/cuisine, filters (cuisine,
  meal type, veg/non-veg, max cook time, difficulty), sorting, pagination.
- **Favorites & ratings** — save recipes, rate 1–5 stars, live average
  ratings.
- **ML recommendations** — TF-IDF + cosine similarity over
  name/ingredients/cuisine/category, with plain-language explanations
  ("Same cuisine", "Shares ingredients: paneer, spices").
- **Ingredient-based finder** — "what can I cook with potato, onion,
  tomato, paneer?" — ranked by match %, with matching/missing ingredients
  broken out.
- **Dashboards** — a personal dashboard (your recipes, favorites, recently
  viewed, personalized recommendations, stats) and a role-gated admin
  dashboard (users, recipes, app-wide stats, moderation).
- **Security** — CSRF protection, security headers, hardened session
  cookies, image content verification, no-default-secret-in-production
  guard. See [Phase 9 notes](#development-history) for the full list.

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, Flask (application factory + blueprints) |
| Database | SQLAlchemy ORM, SQLite (dev) / PostgreSQL or MySQL (prod-ready) |
| Migrations | Flask-Migrate / Alembic |
| Auth | Flask-Login, Werkzeug password hashing |
| Forms & CSRF | Flask-WTF / WTForms |
| ML | Pandas, scikit-learn (TF-IDF, cosine similarity) |
| Frontend | Jinja2, Bootstrap 5, Bootstrap Icons, vanilla JS |
| Images | Pillow (upload content verification) |
| Testing | pytest |
| Production server | Gunicorn |

## Screenshots

Screenshots aren't included in this repo yet — add your own once you've
run the app locally (see [Getting Started](#getting-started)) by dropping
PNGs into a `docs/screenshots/` folder and linking them here, e.g.:

```markdown
![Homepage](docs/screenshots/homepage.png)
![Recipe detail with recommendations](docs/screenshots/detail.png)
![Ingredient finder](docs/screenshots/finder.png)
```

Good ones to capture for a submission: the homepage hero, the Explore page
with filters applied, a recipe detail page (favorite + rating + similar
recipes all visible), the Recommendations page, the Ingredient Finder, and
both dashboards.

A short demo video (2–3 minutes, screen-recorded with something like OBS
or Loom) is worth more than screenshots for showing the recommendation
engine and ingredient finder in action — walk through: register → add a
couple of recipes → favorite/rate one → get recommendations for it → try
the ingredient finder → show the admin dashboard.

## Project Structure

```
recipe_app/
├── app/
│   ├── __init__.py         # application factory
│   ├── extensions.py       # db, login_manager, migrate instances
│   ├── models.py           # User, Recipe, Favorite, Rating, RecentlyViewed
│   ├── auth/                # register / login / logout blueprint
│   ├── main/                # homepage blueprint
│   ├── recipes/             # recipe CRUD, search/filter, favorites, ratings
│   ├── recommendations/     # Flask-facing glue around recommendation.py
│   ├── users/                # personal dashboard blueprint
│   ├── admin/                # role-gated admin dashboard blueprint
│   ├── templates/
│   └── static/
│       ├── css/style.css
│       ├── js/
│       └── uploads/
├── migrations/                # Alembic migration scripts (flask db upgrade)
├── instance/                  # local SQLite database lives here
├── tests/                     # pytest suite (51 tests)
├── config.py
├── recommendation.py          # Flask-independent TF-IDF/cosine-similarity engine
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile                   # Heroku/Render process definition
├── Dockerfile
├── .dockerignore
├── render.yaml                # Render.com Blueprint
├── LICENSE
└── run.py
```

## Getting Started

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set a real `SECRET_KEY` (any long random string — e.g.
   `python -c "import secrets; print(secrets.token_hex(32))"`).
   `python-dotenv` loads `.env` automatically when the app starts.

4. **Set up the database**

   ```bash
   export FLASK_APP=run.py     # Windows (cmd): set FLASK_APP=run.py
   flask db upgrade
   ```

   This runs the Alembic migrations in `migrations/versions/` and creates
   `instance/database.db` with all tables. If you ever change a model,
   generate a new migration instead of deleting the database:

   ```bash
   flask db migrate -m "Describe your change"
   flask db upgrade
   ```

5. **Run the app**

   ```bash
   python run.py
   ```

   Visit `http://127.0.0.1:5000`.

### Environment Variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `SECRET_KEY` | Yes (production) | `dev-key-change-me` | App refuses to start in production with the default. |
| `FLASK_CONFIG` | No | `development` | `development`, `production`, or `testing`. |
| `DATABASE_URL` | No | local SQLite | Any SQLAlchemy-compatible URL. `postgres://` is auto-normalized to `postgresql://`. |

### Promoting a User to Admin

There's no self-service way to become an admin (by design). To promote a
user:

```bash
flask --app run.py shell
>>> from app.extensions import db
>>> from app.models import User
>>> u = User.query.filter_by(username="yourusername").first()
>>> u.is_admin = True
>>> db.session.commit()
```

## Running Tests

```bash
pytest
```

51 tests, in-memory SQLite, CSRF disabled under the test config (see
`TestingConfig` in `config.py`) — runs in a few seconds with no setup.
Covers auth, recipe CRUD + ownership, image upload validation,
search/filter/sort/pagination, favorites/ratings, the recommendation
engine (both pure functions and live routes), the dashboard, and admin
access control.

## Deployment

The app is stateless aside from the database and the uploaded-image
folder, so it runs on any platform that can host a Python WSGI app.
Whichever platform you use, set `SECRET_KEY`, `FLASK_CONFIG=production`,
and (for anything beyond SQLite) `DATABASE_URL` as environment variables
— never commit them.

### Option A: Render (render.yaml included)

1. Push this repo to GitHub.
2. In Render, choose **New +** → **Blueprint** and point it at the repo.
   `render.yaml` provisions a free Postgres database and a web service,
   auto-generates `SECRET_KEY`, and runs `flask db upgrade` before each
   deploy.
3. **Note**: `render.yaml`'s `buildCommand` only installs `requirements.txt`.
   Since that file is SQLite-ready by default, add a Postgres driver
   (`psycopg2-binary`) to `requirements.txt` before deploying with the
   Postgres database the blueprint provisions.

### Option B: Docker

```bash
docker build -t recipeai .
docker run -p 8000:8000 \
  -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  -e FLASK_CONFIG=production \
  -v recipeai_data:/app/instance \
  recipeai
```

The container runs migrations automatically on start (see `Dockerfile`'s
`CMD`) and serves via Gunicorn on port 8000. Mount a volume for
`/app/instance` (SQLite) and `/app/app/static/uploads` (recipe images) if
you want data to survive container restarts — or point `DATABASE_URL` at
a managed Postgres/MySQL instance instead, per the spec's "should allow
migration to PostgreSQL or MySQL" requirement.

### Option C: Any other WSGI host (Heroku, PythonAnywhere, a VPS, etc.)

The included `Procfile` (`web: gunicorn run:app`, with a `release: flask
db upgrade` step) works as-is on Heroku and Heroku-style platforms. For a
plain VPS, run behind Nginx/Caddy as a reverse proxy in front of
`gunicorn run:app`, and set the same three environment variables above.

## Known Limitations / Roadmap

- No login-attempt rate limiting (flagged as a deliberate Phase 9 gap —
  add something like Flask-Limiter before any real deployment).
- No password-reset flow (registration/login/logout only).
- The recommendation engine recomputes TF-IDF on every request rather
  than caching it — fine at student-project scale, not at real scale.
- No screenshots/demo video bundled in this repo yet (see
  [Screenshots](#screenshots) for how to add your own).

## Development History

Built phase-by-phase, each phase reviewed and tested before moving to the
next:

- [x] **Phase 1** — Flask app-factory structure, SQLite + SQLAlchemy config,
      shared `base.html` layout, homepage with hero/search/categories/featured
      recipes/how-it-works/CTA.
- [x] **Phase 2** — User registration, login, logout via Flask-Login, hashed
      passwords (Werkzeug), form validation (Flask-WTF/WTForms), flash
      messages.
- [x] **Phase 3** — Full recipe CRUD (add/view/edit/delete), owner-only
      edit/delete (403 for everyone else), secure image uploads (extension
      allow-list, random filenames, 5 MB size cap with a friendly 413 page,
      old image cleaned up on edit/delete), full form validation.
- [x] **Phase 4** — Search by name/ingredients/cuisine, filters (cuisine,
      meal category, veg/non-veg, max cook time, difficulty), sorting
      (newest, highest rated via an average-rating subquery, shortest cook
      time), and pagination. All filters round-trip through the URL so
      results are shareable/bookmarkable, and the homepage category pills
      link straight into the right filter.
- [x] **Phase 5** — Favorites (toggle on the detail page, backed by a
      unique user/recipe constraint, with a "My Favorites" page linked from
      the nav) and a 1–5 star rating widget that creates a rating on first
      submit and updates it (never duplicates) on subsequent submits. The
      average rating and count shown throughout the app come straight from
      the `Rating` table.
- [x] **Phase 6** — Content-based recommendation engine (`recommendation.py`
      at the project root, Flask-independent and separately testable):
      combines name/ingredients/cuisine/meal-category/veg-type into text,
      vectorizes with TF-IDF, ranks by cosine similarity. Powers both the
      "Similar Recipes" section on every recipe's detail page and a
      dedicated Recommendations page where you pick any recipe and see its
      top 5 matches with a match % and plain-language reasons ("Same
      cuisine", "Shares ingredients: paneer, spices", etc). Handles empty
      and single-recipe catalogs without crashing.
- [x] **Phase 7** — Ingredient-Based Recipe Finder: enter what's in your
      kitchen (e.g. "potato, onion, tomato, paneer") and get every recipe
      that shares at least one ingredient, ranked by match percentage, with
      matching and missing ingredients broken out separately. Set-based
      matching logic lives in `recommendation.py` alongside the TF-IDF
      engine, kept equally Flask-independent and testable.
- [x] **Phase 8** — User dashboard (profile info, your own recipes,
      favorites, recently viewed — deduplicated per recipe, not one row per
      view — and personalized recommendations seeded from your latest
      favorite or view, plus basic stats) and a role-gated admin dashboard
      (`is_admin` on `User`) showing total users/recipes/favorites/ratings,
      most-favorited recipes, newest users/recipes, a full user list, and a
      recipe list with delete. Admin routes are protected by an
      `admin_required` decorator that 403s anyone without the flag,
      including logged-in non-admins.
- [x] **Phase 9** — Security hardening, automated tests, and error-handling
      polish:
      - **Real image-content verification.** Uploaded files are opened with
        Pillow and decoded, not just trusted by extension — a script
        renamed to `.png` is rejected, not just files with a disallowed
        extension.
      - **Site-wide CSRF protection** via `Flask-WTF`'s `CSRFProtect`, on
        top of the per-form tokens already in place, with a friendly
        redirect-and-flash instead of a raw error page if a token is
        missing/expired.
      - **Security headers** (`X-Content-Type-Options`, `X-Frame-Options`,
        `Referrer-Policy`) on every response.
      - **Hardened session cookies** (`HttpOnly`, `SameSite=Lax`, and
        `Secure` in production).
      - **Refuses to boot in production** with the default placeholder
        `SECRET_KEY` instead of silently running insecurely.
      - **Case-insensitive username uniqueness** (no more `alice` +
        `Alice` both registering) and a bumped password minimum (8
        characters).
      - **51 automated tests** covering auth, recipe CRUD + ownership,
        image upload validation, search/filter/sort/pagination,
        favorites/ratings (including the no-duplicate-rating guarantee),
        the recommendation engine (both the pure functions and the live
        routes), the dashboard, and admin access control.
- [x] **Phase 10** — Deployment readiness (Procfile, Dockerfile,
      `render.yaml`, `postgres://`→`postgresql://` URL normalization) and
      real Alembic migrations (`flask db upgrade` replaces manual
      `db.create_all()`), plus this README, LICENSE, and deployment docs.
      Screenshots and a demo video are left for you to record locally (see
      [Screenshots](#screenshots)) since they need a running, visual
      instance of the app to capture.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

Built as an academic project demonstrating Python/Flask web development,
relational database design, authentication, CRUD operations, data
processing, machine learning recommendations, and deployment practices.


***************************************************************************

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
