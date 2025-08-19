# Aissembly Language Specification (Developer Draft v0.1)

**Status:** Working Draft 0.1
**Audience:** Implementers of the Aissembly parser, planner, JIT, and tooling.
**Scope:** The *core language* (lexical rules, types, expressions, statements, functions), the *runtime semantics* (evaluation order, error model, standard library), and *host/JIT interfaces*.

---

## 0. Design Goals

* **Simple, practical, embeddable.** Syntax familiar to Python/JS users, with a minimal, orthogonal core.
* **JIT-first.** Semantics designed to admit SSA-based IR, common optimizations (CSE, DCE, inlining), and partial evaluation.
* **Deterministic by default.** Side effects explicit. No implicit I/O or time access in core.
* **Data-centric.** First-class literals: **number, string, list, dict**. (Booleans are numbers `0|1` or dedicated `true|false`; both forms accepted.)
* **Interpretable → JIT-able.** Reference interpreter must match JIT outputs bit-for-bit on pure functions.

---

## 1. Lexical Structure

### 1.1 Character Set

* Source files are UTF-8. Identifiers may include Unicode letters and `_`, digits after first char.

### 1.2 Whitespace & Newlines

* Significant newlines **end statements**, unless an explicit continuation `\` or unmatched delimiter `(` `[` `{` is present.
* Indentation is **not** significant for blocks; blocks are delimited by braces `{ ... }`.

### 1.3 Comments

* Line: `// comment...` until end of line.
* Block: `/* comment */` (nesting **not** allowed in v0.1).

### 1.4 Tokens

* Keywords (reserved):
  `let, const, fn, if, else, for, while, break, continue, return, true, false, null, import, as, from, try, catch, finally, throw`
* Literals: numbers, strings, lists, dicts, booleans, null.
* Operators & punctuators: see §3.

---

## 2. Types & Values

### 2.1 Primitive Types

* **Number**: 64-bit IEEE-754 float. Integers are subset. Implementation **may** add bignum later; not in v0.1.
* **String**: immutable sequence of Unicode code points.
* **Bool**: `true` or `false`. In numeric contexts: `true→1`, `false→0`.
* **Null**: singleton `null`.

### 2.2 Composite Types

* **List\[T]**: ordered, zero-based, mutable. Heterogeneous allowed.
* **Dict\[K→V]**: hash map with string keys (v0.1 restriction). Values heterogeneous.

### 2.3 Type Semantics

* Dynamic typing with **gradual type hints** (optional, not enforced at runtime in v0.1; used by optimizer). See §8.4.
* Equality: `==` deep for primitives; lists/dicts compare by value (deep) in v0.1. Identity operator `is` compares reference identity.

---

## 3. Operators

**Precedence (high→low), left-associative unless noted:**

1. Member/index/call: `x.y`, `x[expr]`, `fn(args)`
2. Unary: `+ - !` (logical not) `len` (see §6.1 builtins)
3. Multiplicative: `* / %`
4. Additive: `+ -`
5. Relational: `< <= > >=`
6. Equality: `== != is`
7. Logical AND: `&&`
8. Logical OR: `||`
9. Conditional (right-assoc): `cond ? a : b`
10. Assignment (right-assoc): `= += -= *= /= %=`, also destructuring: `let [a,b] = expr; let {x,y} = expr;`

**Notes**

* `+` on strings performs concatenation; on list performs concatenation; on dict is **illegal** (use merge builtin `merge(a,b)`).
* Division `/` is floating-point. Use `floor_div(a,b)` for integer-like behavior.
* Indexing `x[i]`: lists accept number index; dicts accept string key; strings accept number index (returns 1-char string).
* Short-circuit semantics for `&&`, `||`.

---

## 4. Expressions

* Literals:

  * Numbers: `42`, `3.14`, scientific `1e-9`. No numeric separators in v0.1.
  * Strings: `"..."` or `'...'`, backslash escapes `\n`, `\t`, `\uXXXX`.
  * Lists: `[1, 2, "a"]`.
  * Dicts: `{ "k": 1, "s": "v" }`.
* Comprehensions (v0.1):

  * List: `[expr for x in xs if cond]`
  * Dict: `{ key_expr: val_expr for x in xs if cond }`
* Function literals (lambda) **not in v0.1**; use named `fn`.

---

## 5. Statements & Blocks

* Variable declarations:

  * `let x = expr;` (mutable)
  * `const x = expr;` (binding immutable; deep structure may still mutate—see §7.3)
* Control flow:

  * `if (cond) { ... } else { ... }`
  * `while (cond) { ... }`
  * `for (let x in iterable) { ... }` — iterates lists (values), dicts (keys), strings (1-char strings).
  * `break;`, `continue;`, `return expr;`
* Try/catch:

  * `try { ... } catch (e) { ... } finally { ... }`
  * `throw expr;` (any value allowed; runtime wraps non-error values).

---

## 6. Builtins & Standard Library (Core)

### 6.1 Builtins (keywords or intrinsics)

* `len(x)` → number length of string/list/dict.
* `type(x)` → string: `"number"|"string"|"bool"|"null"|"list"|"dict"`.
* `print(x, ...)` → dev/host console (side-effect; may be disabled in restricted mode).
* `assert(cond, msg?)` → throws `AssertionError` on falsey.

### 6.2 List API

* `push(list, value)` → append, returns new length.
* `pop(list)` → remove last, returns value.
* `slice(list, start?, end?)` → sub-list (non-mutating).

### 6.3 Dict API

* `get(dict, key, default?)` → value or default/null.
* `set(dict, key, value)` → sets value, returns dict.
* `merge(a, b)` → shallow merge; right-biased.

### 6.4 Number/String helpers

* `floor(x)`, `ceil(x)`, `abs(x)`, `min(a,b)`, `max(a,b)`
* `split(str, sep)` → list of strings
* `join(list, sep)` → string

---

## 7. Functions & Modules

### 7.1 Function Declarations

```
fn name(param1, param2=default, *rest) {
  // body
  return expr; // implicit return null if omitted
}
```

* Arity is flexible; missing params default to `null` unless default provided.
* `*rest` gathers remaining arguments into list; only at end.

### 7.2 Scope & Binding

* Lexical scope. `let`/`const` bind to nearest function or block.
* Shadowing allowed; no hoisting (use before declaration is error).

### 7.3 Mutability

* `const` prevents *re-binding*; it **does not** deep-freeze lists/dicts. Use `freeze(x)` (future) for deep immutability.

### 7.4 Modules (v0.1 minimal)

* Single-file scripts are modules. Import syntax is declared but host-provided:

```
import util from "util";
import { sum, mean as avg } from "stats";
```

* Resolution rules are host-defined. The language only defines *shape* of the import table.

---

## 8. Semantics

### 8.1 Evaluation Order

* **Left-to-right** evaluation for expressions and arguments.
* Assignments evaluate RHS before LHS binding.

### 8.2 Truthiness

* Falsey: `false`, `0`, `null`, `""`, empty list/dict. Everything else truthy.

### 8.3 Error Model

* Runtime errors are first-class values of type `Error` with fields `{type, message, stack}`.
* Throwing non-Error wraps as `{type:"Thrown", value:original}`.
* Division by zero → `Error{type:"ZeroDivision"}`.

### 8.4 Type Hints (optional)

* Syntax:

```
// hint-only, ignored at runtime by v0.1, used by tooling/JIT
let xs: list = [1,2,3];
fn f(a:number, b:string): number { ... }
```

* Hints must not change runtime behavior.

---

## 9. Grammar (EBNF)

```
Program     := Stmt* EOF
Stmt        := VarDecl | FnDecl | IfStmt | WhileStmt | ForStmt | TryStmt | ReturnStmt | Block | ExprStmt
VarDecl     := ("let" | "const") Identifier (TypeHint?) "=" Expr ";"
TypeHint    := ":" Type
Type        := Identifier | Identifier "[" "]" | "dict" | "list" | "number" | "string" | "bool" | "null"
FnDecl      := "fn" Identifier "(" ParamList? ")" Block
ParamList   := Param ("," Param)*
Param       := Identifier (TypeHint?) ("=" Expr)? | "*" Identifier
IfStmt      := "if" "(" Expr ")" Block ("else" Block)?
WhileStmt   := "while" "(" Expr ")" Block
ForStmt     := "for" "(" "let" Identifier "in" Expr ")" Block
TryStmt     := "try" Block "catch" "(" Identifier ")" Block ("finally" Block)?
ReturnStmt  := "return" Expr? ";"
Block       := "{" Stmt* "}"
ExprStmt    := Expr ";"
Expr        := Assign
Assign      := Cond (AssignOp Assign)?
AssignOp    := "=" | "+=" | "-=" | "*=" | "/=" | "%="
Cond        := Or ("?" Expr ":" Expr)?
Or          := And ("||" And)*
And         := Eq ("&&" Eq)*
Eq          := Rel (("=="|"!="|"is") Rel)*
Rel         := Add (("<"|"<="|">"|">=") Add)*
Add         := Mul (("+"|"-") Mul)*
Mul         := Unary (("*"|"/"|"%") Unary)*
Unary       := ("+"|"-"|"!"|Builtin1) Unary | Postfix
Builtin1    := "len"
Postfix     := Primary ( Call | Index | Member )*
Call        := "(" ArgList? ")"
ArgList     := Expr ("," Expr)*
Index       := "[" Expr "]"
Member      := "." Identifier
Primary     := Literal | Identifier | "(" Expr ")" | ListLit | DictLit | Comp
Literal     := Number | String | "true" | "false" | "null"
ListLit     := "[" (Expr ("," Expr)*)? "]"
DictLit     := "{" (String ":" Expr ("," String ":" Expr)*)? "}"
Comp        := "[" Expr "for" Identifier "in" Expr ("if" Expr)? "]"
Number      := /-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?/
String      := /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/
Identifier  := /[A-Za-z_\p{L}][A-Za-z0-9_\p{L}]*/
```

---

## 10. Standard Library: Deterministic Core (v0.1)

* All functions listed in §6 must be pure **except** `print`, `set`, `push`, `pop`.
* No I/O, filesystem, network in core.

---

## 11. Host & JIT Interface

### 11.1 Compilation Pipeline

1. **Parse → AST** (concrete per §9).
2. **Plan** (hoist consts, resolve imports into host symbols, collect type hints).
3. **Compile → IR** (SSA, typed where possible).
4. **Optimize** (CSE, DCE, const-fold, inlining, loop-invariant motion).
5. **Execute** (interpreter or native backend).

### 11.2 Logging Hooks (recommended)

* Phases: `parse|plan|compile|optimize|execute|finalize` with `*.start|end` events.
* Event fields: `ts, level, event, jit_phase, trace_id, span_id, parent_span_id, message, meta, metrics, error?`.
* See separate *JIT Structured Logging Spec* for full schema.

### 11.3 Foreign Function Interface (FFI)

* Host registers functions in an **import table** by module/name.
* Value mapping:

  * host `None/null` ↔ `null`
  * host `bool/int/float/str/list/dict` ↔ same-name Aissembly types (dict keys must be strings)
* Errors thrown by host functions propagate as Aissembly `Error`.

### 11.4 Determinism Contract

* Given same source and same import table values, execution must be deterministic.
* JIT optimizations must not change observable results (except performance).

---

## 12. Error List (normative)

* `NameError` — undefined identifier
* `TypeError` — invalid operand types for operator or builtin
* `IndexError` — list/string index out of range
* `KeyError` — dict key missing (only for direct `x["k"]` access; `get` returns default/null)
* `ZeroDivision` — division by zero
* `SyntaxError` — parse failure
* `AssertionError` — `assert` failure

---

## 13. Conformance & Tests

* **Reference tests** (must-pass for any implementation):

  1. Arithmetic & precedence
  2. String/list/dict ops
  3. Control flow (if/while/for)
  4. Functions (params, defaults, rest)
  5. Errors (each from §12)
  6. Comprehensions
  7. Truthiness & short-circuit
  8. Import table bindings (host stubs)
* Each test is a pair `(source, expected JSON)` where `expected` includes `result` or `error`.

---

## 14. Examples

### 14.1 Basics

```ais
let a = 10;
let b = 3;
let c = a / b;        // 3.333...
let s = "hi" + "!";   // "hi!"
let xs = [1,2,3];
push(xs, 4);          // xs = [1,2,3,4]
let d = {"k":"v"};
set(d, "n", 42);
```

### 14.2 Functions

```ais
fn sum(xs) {
  let t = 0;
  for (let x in xs) { t += x; }
  return t;
}

fn fib(n) {
  if (n <= 1) { return n; }
  let a = 0, b = 1, i = 2;
  while (i <= n) { let t = a + b; a = b; b = t; i += 1; }
  return b;
}
```

### 14.3 Comprehensions

```ais
let evens = [x for x in [1,2,3,4,5,6] if x % 2 == 0];
let tbl = { "k_" + x: x*x for x in [1,2,3] };
```

### 14.4 Try/Catch

```ais
try {
  let q = 10 / 0; // throws ZeroDivision
} catch (e) {
  print("caught:", e.type);
}
```

---

## 15. Versioning & Compatibility

* **v0.1** is the *minimum viable* core. Future versions may add:

  * Lambdas/closures; pattern matching; iterators/generators; dict key types ≠ string; bigint; deep immutability; module resolution; concurrency primitives.
* Backward compatibility policy: additive when possible; breaking changes require major version.

---

## 16. Implementation Notes (non-normative)

* A simple Pratt parser is sufficient; tokens from a single-pass lexer.
* Use SSA IR with explicit `Phi` at loop headers; perform const-prop, copy-prop, DCE, strength reduction.
* Lists/dicts use copy-on-write semantics **optional**; baseline can mutate in place.
* Provide a debug flag to dump AST/IR for tooling.

---

## 17. Open Questions

* Should `==` on dicts be deep or by-key-set only? (v0.1: deep)
* Add `map/filter/reduce` builtins? (pending)
* Module side-effects on import? (default: allowed; discourage for determinism)

---

**End of Draft v0.1**
