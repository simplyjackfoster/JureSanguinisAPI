# Jure Sanguinis Eligibility Engine Architecture

This engine models current Italian citizenship-by-descent rules in a maintainable, testable manner. **This engine models current law to the best of its ability but is not legal advice. Borderline and contested cases must be reviewed by an Italian citizenship attorney.**

## Goals
- Keep legal rules declarative and versionable.
- Preserve auditability through rule metadata (sources, effective dates, contested flag).
- Make it easy to add new reforms without rewriting the core pipeline.

## Modules
- `src/models.py`: Domain dataclasses and enums for persons, lineage links, statuses, and rule metadata.
- `src/schemas.py`: JSON Schemas for API input and evaluation output.
- `src/rule_engine/json_logic.py`: Minimal JSON-logic evaluator used by rule definitions.
- `src/rule_engine/features.py`: Lineage feature extraction (1948 maternal detection, minor issue flags, Tajani reform exemptions, etc.).
- `src/rule_engine/loader.py`: Loads YAML rule sets into `Rule` instances.
- `src/rule_engine/pipeline.py`: Runs the rule engine over a normalized lineage and aggregates outcomes.
- `rules/*.yaml`: Declarative rule sets (classical, 1948, minor issue, reforms).
- `tests/`: Scenario-driven pytest coverage of edge cases.

## Data flow
1. **Normalization**: Build a parent→child chain of `LineageLink` objects ending with the applicant.
2. **Feature extraction**: `build_feature_flags` inspects each link for pre-1948 maternal links, minor-issue indicators, Tajani exemptions, and reform-driven alternative paths.
3. **Rule loading**: YAML rule sets are loaded by `RuleLoader` to produce `Rule` objects with metadata.
4. **Evaluation**: `RuleEngine.evaluate` runs JSON-logic conditions against a flattened context (`EvaluationContext.to_dict`) enriched with extracted flags.
5. **Aggregation**: The engine merges rule outcomes into an `EvaluationResult`, deriving `overall_status`, `acquisition_mode`, `court_viability`, confidence, and whether a lawyer is recommended.

## Extensibility and versioning
- Add new rules by appending YAML entries with `id`, `condition`, `effects`, `sources`, and `effective_date`.
- Mark contested jurisprudence with `contested: true`; the pipeline automatically elevates `needs_lawyer` and lowers confidence.
- Version rule sets externally (e.g., Git tags) and stamp evaluations with the rule-set version used when invoking `RuleLoader`.

## Handling uncertainty
- `TransmissionStatus.CONTESTED_EDGE_CASE` and `OverallStatus.INDETERMINATE_COMPLEX_CASE` surface unclear facts or disputed rules.
- `court_viability` is increased automatically for court-only or contested outcomes to highlight judicial paths.
- Explanations list triggered rules to support attorney review.

## Update process
1. Update or add YAML rule entries with new legal sources and effective dates.
2. Expand `features.py` to compute any new context facts referenced by rules.
3. Add scenario tests covering the new or changed behavior.
4. Commit changes with citations to sources in rule metadata.

