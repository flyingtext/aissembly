# Surface Language

The surface syntax resembles a tiny subset of Python.  The grammar is specified
in [EBNF](03_core_ir.md).  Key features:

* `let` and `mut` introduce bindings.  Mutable bindings are updated via `set`.
* `fn` defines anonymous functions.  The body may be a single expression after
  `->` or an indented block.
* Conditionals use the familiar `if` / `else` syntax and may appear either as a
  statement or as an expression.
* Loops come in a reduce‑style flavour.  A `for` loop produces a new accumulator
  value on each iteration using the arrow syntax `->` and an `init` clause.
* `while` loops are similar but compute the next accumulator based on the
  previous value until the test thunk returns `false`.

Comments start with `#` and run to the end of the line.
