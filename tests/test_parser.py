from aissembly_dsl.parser import Parser
from aissembly_dsl import ast_nodes as ast


def parse(src: str) -> ast.Program:
    return Parser.from_source(src).parse()


def test_parse_if_expr():
    program = parse("let n = if 1 < 2: 3 else: 4")
    stmt = program.body[0]
    assert isinstance(stmt, ast.Let)
    assert isinstance(stmt.expr, ast.IfExpr)


def test_parse_for_loop():
    program = parse("for i in range(1,3):\n    -> acc + i\ninit 0")
    stmt = program.body[0]
    assert isinstance(stmt, ast.For)
