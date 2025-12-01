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

The API is also deployed at `https://jure-sanguinis-api-git-main-simplyjackfosters-projects.vercel.app`. Use the same payload as above with the hosted base URL:

```bash
curl -X POST https://jure-sanguinis-api-git-main-simplyjackfosters-projects.vercel.app/api/evaluate/ \
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

## Copy-paste helper prompt for ChatGPT

If you would like ChatGPT to walk you through the questions one-by-one, fill out the JSON, and hand you a ready-to-run `curl` command you can paste directly into your terminal, copy the prompt below into a new ChatGPT conversation. It is written for non-technical users—just answer the questions in plain language.

```
You are helping me send my family tree to this API endpoint (no local server):
https://jure-sanguinis-api-git-main-simplyjackfosters-projects.vercel.app/api/evaluate/

How to interview me (one or two simple questions at a time):
1) Start with me (the applicant): ask for a short id I can remember (e.g., "me"), my full name, and my birth country. Only after that, ask if I know my birth date (yyyy-mm-dd) and any other citizenships I had at birth. If unknown, say we will leave it blank.
2) Add ancestors one at a time. For each person, ask for:
   - a short id (e.g., "mom", "grandpa1"), their full name, and where they were born.
   - then check if I know their birth date (yyyy-mm-dd) and any other citizenships at birth.
   - finally, ask if there are important life events to record (e.g., naturalization, marriage, death) with date and country if known.
3) After each new person, ask how they are connected to the applicant (mother or father) and collect a simple link like: parent_id = that person’s id, child_id = their child’s id, relationship = "mother" or "father".
4) If I have legal context, ask only then: is this for ADMIN or COURT processing, when was it filed (yyyy-mm-dd), and in which country. If I don’t know, skip it.

Rules for building the JSON (keep it beginner-friendly):
- Do not invent information. Only include fields I confirm. If I say "not sure" or leave something blank, omit that field entirely.
- Make sure every lineage link references ids that exist and keeps the relationship label.
- Keep asking until the applicant, at least one ancestor, and the links connecting them are clear.

When finished, show me two fenced code blocks and nothing else:
1) The final JSON you will send.
2) A single `curl` command that POSTs that JSON to the endpoint with header `Content-Type: application/json`. Tell me to copy and paste this command into my terminal to run it.
```
