import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor
from aissembly_core import runtime

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


def test_execution_with_reparse_iterations(tmp_path, capsys):
    prog_path = tmp_path / "prog.asl"
    prog_path.write_text(PROGRAM)
    runtime.main([str(prog_path), "--reparse-iterations", "2"])
    captured = capsys.readouterr().out
    env = json.loads(captured)
    assert env["x"] == 13
    assert env["tag"] == "ok"
    assert env["total"] == 6
    assert env["steps"] == 3
