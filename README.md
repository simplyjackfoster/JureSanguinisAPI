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

If you would like ChatGPT to collect the necessary details, assemble the JSON payload, and return a ready-to-run `curl` request for the hosted API, copy the prompt below into a new ChatGPT conversation. The prompt gives ChatGPT all the structure it needs so you only have to answer questions about your lineage.

```
You are helping me call the Jure Sanguinis API `/api/evaluate/` endpoint at:
https://jure-sanguinis-api-git-main-simplyjackfosters-projects.vercel.app/api/evaluate/

Ask me only the questions needed to build this JSON body (explain the fields briefly as you go):
{
  "applicant": {"id": string, "name": string, "birth_country": string, "birth_date": yyyy-mm-dd?, "other_citizenships_at_birth": [string]?, "events": [ {"kind": string, "date": yyyy-mm-dd?, "country": string?, "metadata": object?} ]?, "notes": object?},
  "ancestors": [ {"id": string, "name": string, "birth_country": string?, "birth_date": yyyy-mm-dd?, "other_citizenships_at_birth": [string]?, "events": [ ...same as above... ]?, "notes": object?} ],
  "lineage_links": [ {"parent_id": string, "child_id": string, "relationship": string (e.g., father/mother), "notes": object?} ],
  "context": {"process_type": "ADMIN"|"COURT"?, "appointment_filed_date": yyyy-mm-dd?, "country_of_filing": string?}?
}

Instructions for the conversation:
- Validate basics before building JSON: confirm the applicant id/name, at least one ancestor, and lineage_links that connect everyone to the applicant.
- For each person, remind me that birth_date and events are optional; keep placeholders out of the final JSON if I do not provide them.
- Ensure every lineage link uses existing ids and has a relationship label.
- After collecting answers, construct a minimal JSON payload that only includes fields I provided (omit null/unknowns).
- Output **one** `curl` command that POSTs this JSON to the hosted endpoint with `Content-Type: application/json`.
- Show the final JSON and `curl` command in fenced code blocks and nothing else.
```
