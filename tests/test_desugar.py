from aissembly_dsl.parser import Parser
from aissembly_dsl.desugar import desugar
from aissembly_dsl import ast_nodes as ast


def ds(src: str):
    ast_prog = Parser.from_source(src).parse()
    return desugar(ast_prog)


def test_if_desugars_to_cond():
    prog = ds("let x = if 1 < 2: 3 else: 4")
    let = prog.body[0]
    call = let.expr
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name) and call.func.id == 'cond'


def test_for_desugars_to_loop():
    prog = ds("for i in range(1,3):\n    -> acc + i\ninit 0")
    call_stmt = prog.body[0]
    assert isinstance(call_stmt, ast.Call)
    assert isinstance(call_stmt.func, ast.Name) and call_stmt.func.id == 'loop.for'
