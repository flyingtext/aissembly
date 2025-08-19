# Runtime Semantics

Evaluation proceeds in two stages:

1. The surface AST is desugared into Core IR nodes.
2. The evaluator walks the IR and executes primitives.

Bindings live in immutable environments.  A `mut` declaration stores its value
inside a small `Box` object that can be updated with `set`.

Loops and conditionals operate via higher‑order functions and are therefore lazy
in their branches.
