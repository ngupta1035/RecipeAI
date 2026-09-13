# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Pillow/psycopg2-style native deps come pre-built as wheels for this image
# in almost all cases, so no extra system packages are needed for this
# project's dependency set.

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance app/static/uploads

ENV FLASK_CONFIG=production \
    FLASK_APP=run.py \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Run migrations, then start the app. SECRET_KEY and DATABASE_URL must be
# supplied at runtime (see .env.example) - the app refuses to boot in
# production with the placeholder SECRET_KEY.
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:8000 run:app"]
