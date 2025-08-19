import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor

PROGRAM = """
let x = 7 + 6
let tag = cond(test=x >= 10) -> "ok" ::else-> "ng"
let total = for(range(1, 4), init=0) -> acc + i
let steps = while(test=acc < 3, init=0) -> acc + 1
"""

def test_execution():
    prog = parse_program(PROGRAM)
    exe = Executor()
    env = exe.run(prog)
    assert env["x"] == 13
    assert env["tag"] == "ok"
    assert env["total"] == 6
    assert env["steps"] == 3
