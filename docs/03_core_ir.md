# Core IR

All control flow desugars to a small functional core composed of first‑class
primitives.  Each primitive accepts thunks (zero‑argument callables) so that
branches remain lazy.

* `cond(test, then, else)` – evaluate `test()` and call either `then` or `else`.
* `loop.for(iter, body, init, max_iter=None, timeout_ms=None)` – iterate over
  `iter` producing a new accumulator by calling `body(item, acc)`.
* `loop.while(test, body, init, max_iter=None, timeout_ms=None)` – repeatedly
  call `body(acc)` while `test()` returns `True`.
* `ctrl.break(value=None)` and `ctrl.continue()` are implemented via exceptions
  that unwind to the nearest enclosing loop primitive.

Primitive operations such as arithmetic live under the `op` namespace and are
pure Python functions.
