# Jure Sanguinis API

A backend-oriented eligibility engine for Italian citizenship by descent (jure sanguinis). It focuses on maintainable, declarative rules, explicit handling of edge cases (1948 maternal, minor issue, Tajani-style reforms), and rich outputs for attorney review.

**This engine models current law to the best of its ability but is not legal advice. Borderline and contested cases must be reviewed by an Italian citizenship attorney.**

## Components
- JSON Schemas for inputs/outputs (`src/schemas.py`).
- Domain models and enums (`src/models.py`).
- Rule engine core (`src/rule_engine/*`).
- Declarative rule sets (`rules/*.yaml`).
- Scenario tests (`tests/`).

## Running tests
```bash
pytest
```

## Running the Django API

The project includes a lightweight Django REST API that exposes an `/api/evaluate/` endpoint for lineage evaluations.

```bash
pip install -r requirements.txt
python manage.py migrate  # first run only; uses SQLite
python manage.py runserver
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {"id": "app", "name": "Applicant", "birth_country": "USA"},
    "ancestors": [
      {"id": "a1", "name": "Giorgio", "birth_country": "Italy"},
      {"id": "a2", "name": "Maria", "birth_country": "Argentina"}
    ],
    "lineage_links": [
      {"parent_id": "a1", "child_id": "a2", "relationship": "father"},
      {"parent_id": "a2", "child_id": "app", "relationship": "father"}
    ]
  }'
```

## Calling the hosted API

The API is also deployed at `https://jure-sanguinis-api-git-codex-6ae004-simplyjackfosters-projects.vercel.app`. Use the same payload as above with the hosted base URL:

```bash
curl -X POST https://jure-sanguinis-api-git-codex-6ae004-simplyjackfosters-projects.vercel.app/api/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {"id": "app", "name": "Applicant", "birth_country": "USA"},
    "ancestors": [
      {"id": "a1", "name": "Giorgio", "birth_country": "Italy"},
      {"id": "a2", "name": "Maria", "birth_country": "Argentina"}
    ],
    "lineage_links": [
      {"parent_id": "a1", "child_id": "a2", "relationship": "father"},
      {"parent_id": "a2", "child_id": "app", "relationship": "father"}
    ]
  }'
```
