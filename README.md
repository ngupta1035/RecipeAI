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
