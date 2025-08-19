# Aissembly DSL Overview

Aissembly is a minimal Python‑like domain specific language that desugars to a
small functional core. Control flow constructs such as conditionals and loops
compile to first‑class functions in the Core IR.  The goal of this repository is
to provide a reference implementation together with documentation and a tiny
test suite that demonstrates the design.

This document gives a bird eye view of the code base and how the pieces fit
together.  The major components are:

* **Tokenizer** – splits source files into a stream of tokens with INDENT/DEDENT
  information similar to Python.
* **Parser** – produces an abstract syntax tree (AST) according to the grammar
  documented in `02_language_surface.md`.
* **Desugar** – rewrites the surface AST into Core IR calls.  For example an
  `if` expression becomes a call to the `cond` primitive.
* **Core IR / Evaluator** – defines functional primitives such as `cond`,
  `loop.for` and `loop.while` and evaluates desugared programs.

The remaining documents describe the language and runtime in more detail.
