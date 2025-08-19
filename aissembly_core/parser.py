from __future__ import annotations

"""Parser for Aissembly minimal language."""

from dataclasses import dataclass
from typing import List, Dict, Any

from lark import Lark, Transformer
from lark.exceptions import UnexpectedEOF, UnexpectedInput
from lark.indenter import Indenter


@dataclass
class Program:
    statements: List[Any]


@dataclass
class ParserOptions:
    """Configuration for parser optimizations.

    Each field represents how many times the corresponding optimization should
    be attempted.  The optimizations themselves are placeholders and will be
    handled by higher-level components (likely using an LLM) in future
    iterations.
    """

    accuracy_opt_passes: int = 0
    decomposition_opt_passes: int = 0
    integration_opt_passes: int = 0
    loop_to_operation_opt_passes: int = 0
    operation_to_loop_opt_passes: int = 0
    condition_to_operation_opt_passes: int = 0

@dataclass
class LetStmt:
    name: str
    expr: Any

@dataclass
class Var:
    name: str

@dataclass
class Number:
    value: int

@dataclass
class String:
    value: str

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


class TreeIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types: List[str] = []
    CLOSE_PAREN_types: List[str] = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8


GRAMMAR = r"""
start: (statement _NEWLINE*)*

statement: "let" NAME "=" expr        -> let_stmt
         | expr                         -> expr_stmt

?expr: cond_block
     | cond_inline
     | for_loop
     | while_loop
     | call
     | STRING                        -> string
     | SIGNED_NUMBER                 -> number
     | NAME                          -> var

for_loop: "for" "(" "range" "(" expr "," expr ("," expr)? ")" "," "init" "=" expr ")" block_or_inline -> for_loop

while_loop: "while" "(" "test" "=" expr "," "init" "=" expr ")" block_or_inline -> while_loop

block_or_inline: ":" _NEWLINE _INDENT "->" expr _DEDENT      -> block_body
               | "->" expr                            -> inline_body

cond_block: "cond" "(" "test" "=" expr ")" ":" _NEWLINE _INDENT "then" ":" _NEWLINE _INDENT "->" expr _NEWLINE _DEDENT "else" ":" _NEWLINE _INDENT "->" expr _NEWLINE _DEDENT _DEDENT -> cond_block

cond_inline: "if" "(" expr ")" "?" expr ":" expr              -> inline_if
           | "cond" "(" "test" "=" expr ")" "->" expr "::else->" expr -> inline_cond

call: NAME "(" [arguments] ")"                    -> call

arguments: argument ("," argument)*

argument: NAME "=" expr                             -> named_arg
        | expr                                      -> positional_arg

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
        name, expr = items
        return LetStmt(str(name), expr)

    def expr_stmt(self, items):
        return items[0]

    def var(self, items):
        return Var(str(items[0]))

    def number(self, items):
        return Number(int(items[0]))

    def string(self, items):
        value = items[0][1:-1]
        return String(value)

    def named_arg(self, items):
        return NamedArg(str(items[0]), items[1])

    def positional_arg(self, items):
        return items[0]

    def arguments(self, items):
        return items

    def call(self, items):
        name = str(items[0])
        args = []
        kwargs: Dict[str, Any] = {}
        if len(items) > 1:
            for arg in items[1]:
                if isinstance(arg, NamedArg):
                    kwargs[arg.name] = arg.value
                else:
                    args.append(arg)
        return Call(name, args, kwargs)

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


def parse_program(source: str, options: ParserOptions | None = None) -> Program:
    """Parse source code into a :class:`Program`.

    The parser incrementally consumes the source line by line.  Each line is
    appended to a buffer and reparsed until a complete statement is produced.
    This enables re-parsing of individual lines during interactive development
    or when streaming program text from an LLM.  After parsing, a series of
    optimization hooks are executed according to ``options``.  Each optimization
    currently performs no transformation; they serve as placeholders for future
    LLM-based workflows.

    Args:
        source: Raw program text.
        options: Optional :class:`ParserOptions` specifying how many times each
            optimization should run.

    Returns:
        Parsed :class:`Program` instance.
    """

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

    program = Program(statements)
    options = options or ParserOptions()

    for _ in range(options.accuracy_opt_passes):
        program = _identity(program)
    for _ in range(options.decomposition_opt_passes):
        program = _identity(program)
    for _ in range(options.integration_opt_passes):
        program = _identity(program)
    for _ in range(options.loop_to_operation_opt_passes):
        program = _identity(program)
    for _ in range(options.operation_to_loop_opt_passes):
        program = _identity(program)
    for _ in range(options.condition_to_operation_opt_passes):
        program = _identity(program)

    return program
