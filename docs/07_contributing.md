# Contributing

* Run `pytest` before sending a pull request.
* Style is enforced by `ruff` and `black` via the provided pre‑commit hooks.
* When adding new surface sugar follow the chain: **grammar → parser tests →
desugar → evaluator tests**.
* New features should include documentation updates under `docs/`.
