# Aissembly Minimal Parser and Executor

This document describes the prototype parser and execution engine for the
Aissembly minimal language.

## Running Programs

```bash
python -m aissembly_core.runtime path/to/program.asl --llm llm_functions.json --reparse-iterations 2
```

The optional `--llm` flag loads LLM function specifications in JSON format.
`--reparse-iterations` forwards to ``ParserOptions.reparse_iterations`` and
controls how many times the source is reparsed line by line before execution
(default is `1`).

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

## Line-by-Line Re-parsing

`parse_program` incrementally reparses each line of the source. This enables
interactive sessions to handle single-line edits or streamed input.

## Parser Options

The :class:`aissembly_core.parser.ParserOptions` dataclass configures parser
behaviour:

- ``reparse_iterations`` – how many times to parse the entire source before
  optimisation.
- ``accuracy_opt_passes`` – count of accuracy optimisation passes.
- ``decomposition_opt_passes`` – number of decomposition optimisation passes.
- ``integration_opt_passes`` – number of integration optimisation passes.
- ``loop_to_operation_opt_passes`` – convert loops into operations.
- ``operation_to_loop_opt_passes`` – convert operations into loops.
- ``condition_to_operation_opt_passes`` – convert conditions into operations.

These optimisation passes are placeholders for future LLM-driven transforms.

### Python API Example

```python
from aissembly_core.parser import parse_program

SOURCE = """
let x = add(7, 6)
let tag = cond(test=ge(x, 10)):
    then:
        -> "ok"
    else:
        -> "ng"
"""

program = parse_program(SOURCE)
```

### Running the Example

```bash
python -m aissembly_core.runtime examples/cond_block.asl --llm llm_functions.json
```

The command prints:

```
{
  "x": 13,
  "tag": "ok"
}
```
