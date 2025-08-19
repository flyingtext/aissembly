# Errors, Tracing and Limits

Errors are ordinary values `Error(kind, msg, data)` defined in `errors.py`.
Parsing errors include line and column information.  Runtime errors may be
caught using the `ctrl.try` primitive.

`tracing.Trace` is a light‑weight hook object with optional callbacks
`on_enter`, `on_exit` and `on_branch`.  Core primitives call these hooks when
provided.

Loop primitives honour optional `max_iter` and `timeout_ms` arguments.  If a
limit is exceeded the evaluator raises an `Error("LimitExceeded", ...)` value.
