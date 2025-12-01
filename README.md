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
