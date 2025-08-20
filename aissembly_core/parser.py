from __future__ import annotations

"""Parser for Aissembly minimal language."""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from lark import Lark, Transformer
from lark.exceptions import UnexpectedEOF, UnexpectedInput
from lark.indenter import Indenter

@dataclass
class Program:
    statements: List[Any]

@dataclass
class LetStmt:
    name: str
    expr: Any

@dataclass
class Var:
    name: str

@dataclass
class Number:
    value: Union[int, float]

@dataclass
class String:
    value: str

@dataclass
class Boolean:
    value: bool

@dataclass
class ListLiteral:
    elements: List[Any]

@dataclass
class DictLiteral:
    items: List[Tuple[Any, Any]]

@dataclass
class NamedArg:
    name: str
    value: Any

@dataclass
class Call:
    name: str
    args: List[Any]
    kwargs: Dict[str, Any]

@dataclass
class ForLoop:
    start: Any
    end: Any
    step: Any
    init: Any
    body: Any

@dataclass
class WhileLoop:
    test: Any
    init: Any
    body: Any

@dataclass
class Cond:
    test: Any
    then: Any
    else_: Any


# ---- 간단한 evaluator (핵심: Call 처리) ----
def eval_node(node):
    if isinstance(node, String):
        return node.value
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Call):
        fn = ENV[node.name]
        args = [eval_node(a) for a in node.args]
        kwargs = {k: eval_node(v) for k, v in node.kwargs.items()}
        return fn(*args, **kwargs)
    # Dict/List/Cond 등은 필요에 맞게 추가
    return node

# ---- lazy-to-str 데코레이터 ----
def lazy_to_str(func: Callable[..., str]) -> Callable[..., LazyStr]:
    def _wrap(*a, **kw) -> LazyStr:
        return LazyStr(lambda: func(*a, **kw))
    return _wrap

class LazyStr:
    def __init__(self, thunk: Callable[[], str]):
        self._thunk = thunk
        self._value = None
        self._done = False

    def force(self) -> str:
        if not self._done:
            self._value = self._thunk()
            self._done = True
        return self._value

    def __str__(self) -> str:
        return self.force()

    def __repr__(self) -> str:
        return f"LazyStr({self._value!r})" if self._done else "LazyStr(<pending>)"

    def __add__(self, other):
        return LazyStr(lambda: str(self) + str(other))
    def __radd__(self, other):
        return LazyStr(lambda: str(other) + str(self))
    def __format__(self, spec):
        return format(self.force(), spec)


class TreeIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types: List[str] = []
    CLOSE_PAREN_types: List[str] = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8




GRAMMAR = r"""
start: (statement _NEWLINE*)*

statement: "let" NAME "=" expr ";"?        -> let_stmt
         | expr ";"?                       -> expr_stmt

?expr: cond_block
     | cond_inline
     | for_loop
     | while_loop
     | or_expr

?or_expr: or_expr "or" and_expr       -> or_op
        | and_expr

?and_expr: and_expr "and" not_expr    -> and_op
         | not_expr

?not_expr: "not" not_expr             -> not_op
         | comparison

?comparison: arith_expr (comp_op arith_expr)? -> comparison

comp_op: "==" -> eq
       | "!=" -> neq
       | "<"  -> lt
       | "<=" -> le
       | ">"  -> gt
       | ">=" -> ge

?arith_expr: arith_expr "+" term      -> add
           | arith_expr "-" term      -> sub
           | term

?term: term "*" factor                -> mul
     | term "/" factor                -> div
     | term "%" factor                -> mod
     | factor

?factor: "-" factor                   -> neg
       | atom

?atom: primary trailer*

?primary: list_literal
        | dict_literal
        | call
        | var
        | STRING                      -> string
        | "true"                      -> true
        | "false"                     -> false
        | SIGNED_NUMBER               -> number
        | "(" expr ")"

trailer: "[" expr "]"                 -> index
       | "[" expr? ":" expr? "]"      -> slice

call: dotted_name "(" [arguments] ")" -> call
var: dotted_name                      -> var
dotted_name: NAME ("." NAME)*

arguments: argument ("," argument)*
argument: NAME "=" expr               -> named_arg
        | expr                        -> positional_arg

list_literal: "[" [expr ("," expr)*] "]"      -> list_lit
dict_literal: "{" [pair ("," pair)*] "}"      -> dict_lit
pair: expr ":" expr

for_loop: "for" "(" "range" "(" expr "," expr ("," expr)? ")" "," "init" "=" expr ")" block_or_inline -> for_loop

while_loop: "while" "(" "test" "=" expr "," "init" "=" expr ")" block_or_inline -> while_loop

block_or_inline: ":" _NEWLINE _INDENT "->" expr _DEDENT      -> block_body
               | "->" expr                                    -> inline_body

cond_block: "cond" "(" "test" "=" expr ")" ":" _NEWLINE _INDENT "then" ":" _NEWLINE _INDENT "->" expr _NEWLINE _DEDENT "else" ":" _NEWLINE _INDENT "->" expr _NEWLINE _DEDENT _DEDENT -> cond_block

cond_inline: "if" "(" expr ")" "?" expr ":" expr              -> inline_if
           | "cond" "(" "test" "=" expr ")" "->" expr "::else->" expr -> inline_cond

%import common.CNAME -> NAME
%import common.SIGNED_NUMBER
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING
_NEWLINE: /(\r?\n[ \t]*)+/

%declare _INDENT _DEDENT
%ignore WS_INLINE
"""




class ASTBuilder(Transformer):
    def start(self, items):
        return Program(items)

    def let_stmt(self, items):
        name = items[0]
        expr = items[1]
        return LetStmt(str(name), expr)

    def expr_stmt(self, items):
        return items[0]

    def dotted_name(self, items):
        return ".".join(str(i) for i in items)

    def var(self, items):
        return Var(items[0])

    def number(self, items):
        s = str(items[0])
        if any(ch in s for ch in ".eE"):
            return Number(float(s))
        return Number(int(s))

    def string(self, items):
        value = items[0][1:-1]
        return String(value)

    def true(self, items):
        return Boolean(True)

    def false(self, items):
        return Boolean(False)

    def list_lit(self, items):
        return ListLiteral(items)

    def dict_lit(self, items):
        if items and items[0] is None:
            items = []
        return DictLiteral(items)

    def pair(self, items):
        return (items[0], items[1])

    def named_arg(self, items):
        return NamedArg(str(items[0]), items[1])

    def positional_arg(self, items):
        return items[0]

    def arguments(self, items):
        return items

    def call(self, items):
        name = items[0]
        args = []
        kwargs: Dict[str, Any] = {}
        if len(items) > 1:
            for arg in items[1]:
                if isinstance(arg, NamedArg):
                    kwargs[arg.name] = arg.value
                else:
                    args.append(arg)
        return Call(name, args, kwargs)

    def atom(self, items):
        node = items[0]
        for tr in items[1:]:
            if tr[0] == "index":
                node = Call("op.get", [node, tr[1]], {})
            else:
                start, end = tr[1], tr[2]
                node = Call("op.slice", [node, start, end], {})
        return node

    def index(self, items):
        return ("index", items[0])

    def slice(self, items):
        start = items[0] if len(items) > 0 else None
        end = items[1] if len(items) > 1 else None
        return ("slice", start, end)

    def add(self, items):
        a, b = items
        return Call("op.add", [a, b], {})

    def sub(self, items):
        a, b = items
        return Call("op.sub", [a, b], {})

    def mul(self, items):
        a, b = items
        return Call("op.mul", [a, b], {})

    def div(self, items):
        a, b = items
        return Call("op.div", [a, b], {})

    def mod(self, items):
        a, b = items
        return Call("op.mod", [a, b], {})

    def neg(self, items):
        val = items[0]
        return Call("op.sub", [Number(0), val], {})

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        left, op, right = items
        return Call(f"op.{op}", [left, right], {})

    def eq(self, _):
        return "eq"

    def neq(self, _):
        return "neq"

    def lt(self, _):
        return "lt"

    def le(self, _):
        return "le"

    def gt(self, _):
        return "gt"

    def ge(self, _):
        return "ge"

    def and_op(self, items):
        a, b = items
        return Call("op.land", [a, b], {})

    def or_op(self, items):
        a, b = items
        return Call("op.lor", [a, b], {})

    def not_op(self, items):
        a = items[0]
        return Call("op.lnot", [a], {})

    def block_body(self, items):
        return items[0]

    def inline_body(self, items):
        return items[0]

    def for_loop(self, items):
        start = items[0]
        end = items[1]
        if len(items) == 5:
            step = items[2]
            init = items[3]
            body = items[4]
        else:
            step = Number(1)
            init = items[2]
            body = items[3]
        return ForLoop(start, end, step, init, body)

    def while_loop(self, items):
        test, init, body = items
        return WhileLoop(test, init, body)

    def cond_block(self, items):
        test, then, else_ = items
        return Cond(test, then, else_)

    def inline_if(self, items):
        test, then, else_ = items
        return Cond(test, then, else_)

    def inline_cond(self, items):
        test, then, else_ = items
        return Cond(test, then, else_)


def _identity(program: Program) -> Program:
    """Placeholder optimization that returns the program unchanged."""

    return program


def parse_program(source: str, options) -> Program:
    """Parse source code into a :class:`Program`.

    The parser incrementally consumes the source line by line.  Each line is
    appended to a buffer and reparsed until a complete statement is produced.
    This enables re-parsing of individual lines during interactive development
    or when streaming program text from an LLM.  After parsing, a series of
    optimisation hooks are executed according to ``options``.  Each optimisation
    currently performs no transformation; they serve as placeholders for future
    LLM-based workflows.

    Args:
        source: Raw program text.
        options: Options.

    Returns:
        Parsed :class:`Program` instance.
    """

    def _parse_once() -> Program:
        parser = Lark(GRAMMAR, parser="lalr", postlex=TreeIndenter(), start="start")
        builder = ASTBuilder()

        statements: List[Any] = []
        lines = [ln for ln in source.strip().splitlines() if ln.strip()]
        buffer = ""
        for line in lines:
            buffer += line + "\n"
            try:
                tree = parser.parse(buffer)
            except UnexpectedEOF:
                continue
            except UnexpectedInput as e:
                token_type = getattr(getattr(e, "token", None), "type", "")
                if token_type in ("$END", "_DEDENT"):
                    continue
                raise
            else:
                prog = builder.transform(tree)
                if isinstance(prog, Program):
                    statements.extend(prog.statements)
                else:
                    statements.append(prog)
                buffer = ""

        if buffer.strip():
            tree = parser.parse(buffer)
            prog = builder.transform(tree)
            if isinstance(prog, Program):
                statements.extend(prog.statements)
            else:
                statements.append(prog)

        return Program(statements)

    program = None
    for _ in range(max(options.reparse_iterations, 1)):
        program = _parse_once()
    
    return program
