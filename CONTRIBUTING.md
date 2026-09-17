# Contributing

## Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Validation

Run both checks before submitting changes:

```bash
ruff check .
pytest
```

## Change scope

Keep search, evaluation, training, persistence, and command-line responsibilities separated.

Changes that modify evaluator semantics must include tests covering sign symmetry or sanity behavior.

Changes that modify checkpoint fields must preserve backward compatibility or include an explicit migration path.

Changes that modify arena acceptance must document the statistical or engineering reason for the new threshold.

## Commits

Use concise imperative commit messages.

Examples:

```text
Harden checkpoint migration
Improve tactical move ordering
Add paired arena regression tests
```
