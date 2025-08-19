from __future__ import annotations

"""Parser for Aissembly minimal language."""

from dataclasses import dataclass
from typing import List, Dict, Any

from lark import Lark, Transformer
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


def parse_program(source: str) -> Program:
    parser = Lark(GRAMMAR, parser="lalr", postlex=TreeIndenter(), start="start")
    tree = parser.parse(source.strip())
    return ASTBuilder().transform(tree)
