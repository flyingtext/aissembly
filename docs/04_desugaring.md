# Desugaring Rules

The table below summarises the mapping from surface syntax to Core IR calls.

| Surface | Core IR |
| --- | --- |
| `if E: A else: B` | `cond(fn()->E, fn()->A, fn()->B)` |
| `for i in R: -> BODY init X` | `loop.for(R, fn(i, acc)->BODY, init=X)` |
| `while T: -> BODY init X` | `loop.while(fn()->T, fn(acc)->BODY, init=X)` |
| `break` | `ctrl.break()` |
| `continue` | `ctrl.continue()` |

The desugaring step rewrites the parsed AST into an equivalent tree composed of
`Call` and `Lambda` nodes that reference the primitives above.  No evaluation
happens during desugaring.
