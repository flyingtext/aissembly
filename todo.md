# TODO

Summary of implemented vs pending features relative to [docs/language_spec.md](docs/language_spec.md).

## Implemented
- Variable declarations using `let` with expression assignment.
- Numbers, strings, lists, and dict literals with indexing and slicing.
- Arithmetic, comparison, and logical operators (`+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `and`, `or`, `not`).
- Function calls with positional and named arguments and dotted names.
- Built-in operations such as `op.len`, `op.get`, `op.set`, `op.append`, `op.slice`, and `op.has`.
- Loop constructs `for(range(start, end[, step]), init=acc) -> expr` and `while(test=..., init=...) -> expr`.
- Conditional expressions via `if (cond) ? a : b` and `cond(test=...) -> ... ::else-> ...`.
- LLM adapter integration for calling external functions.

## Not Implemented
- `const` bindings.
- Boolean (`true`, `false`) and `null` literals.
- Block syntax using braces `{}` and statement terminators `;` as described in the spec.
- Standard `if`/`else` statements with block bodies.
- `for`/`while` statements over general iterables; current loops require `range` and accumulator parameters.
- `break`, `continue`, and `return` statements.
- Try/catch/finally and `throw`.
- List/dict comprehensions.
- Comment syntax (`//`, `/* */`).
- Function declarations (`fn`), parameters, and return semantics.
- Module imports (`import`, `as`, `from`).
- Additional standard library helpers (`push`, `pop`, `merge`, `floor_div`, `print`, `type`, `assert`, etc.).
