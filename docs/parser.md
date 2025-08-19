# Aissembly Minimal Parser and Executor

This document describes the prototype parser and execution engine for the
Aissembly minimal language.

## Running Programs

```bash
python -m aissembly_core.runtime path/to/program.asl --llm llm_functions.json
```

The optional `--llm` flag loads LLM function specifications in JSON format.

## Example

```
let x = add(7, 6)
let tag = cond(test=ge(x, 10)):
    then:
        -> "ok"
    else:
        -> "ng"
```

Executing this program produces the environment:

```
{
  "x": 13,
  "tag": "ok"
}
```
