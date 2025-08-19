# Aissembly DSL

A small Python‑like language that desugars to a functional core.  This repository
contains a reference implementation consisting of a tokenizer, parser, desugarer
and evaluator together with documentation and tests.

## Quickstart

```bash
pip install -e .
pytest -q
```

Example program:

```ais
for i in range(1,6):
    -> acc + i*i
init 0
```
