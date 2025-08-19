import pytest
from aissembly_dsl.parser import Parser
from aissembly_dsl.desugar import desugar
from aissembly_dsl.evaluator import evaluate
from aissembly_dsl.errors import Error


def run(src: str):
    prog = Parser.from_source(src).parse()
    ir = desugar(prog)
    return evaluate(ir)


def test_cond_eval():
    src = "let t = if 1 < 2: 'a' else: 'b'\nt"
    assert run(src) == 'a'


def test_loop_for_eval():
    src = "for i in range(1,6):\n    -> acc + i*i\ninit 0"
    assert run(src) == 55


def test_while_limit_error():
    with pytest.raises(Error):
        run("loop_while(fn()-> true, fn(acc)-> acc, 0, 5)")
