import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor


def run(src: str):
    prog = parse_program(src)
    exe = Executor()
    return exe.run(prog)


def test_basic_types_example_semicolons():
    example_path = Path(os.path.dirname(os.path.dirname(__file__))) / "examples" / "basic_types.asl"
    program = example_path.read_text()
    env = run(program)
    assert env["count"] == 42
    assert env["ratio"] == 3.14
    assert env["greeting"] == "hello"
    assert env["items"] == [1, 2, 3]
    assert env["config"] == {"mode": "dev", "limit": 5}
