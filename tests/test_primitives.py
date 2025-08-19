import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor


def run(src: str):
    prog = parse_program(src)
    exe = Executor()
    return exe.run(prog)


def test_primitives():
    program = """
let nums = 1 + 2 * 3
let s = "he" + "llo"
let sub = s[1:4]
let lst = [1, 2]
let lst2 = op.append(lst, 3)
let first = lst2[0]
let part = lst2[1:3]
let d = {"x": 1}
let d2 = op.set(d, "y", 2)
let val = d2["y"]
let hasx = op.has(d2, "x")
let total = for(range(0, op.len(lst2)), init=0) -> acc + lst2[i]
let tag = if(total == 6) ? "ok" : "ng"
"""
    env = run(program)
    assert env["nums"] == 7
    assert env["s"] == "hello"
    assert env["sub"] == "ell"
    assert env["lst2"] == [1, 2, 3]
    assert env["first"] == 1
    assert env["part"] == [2, 3]
    assert env["d2"] == {"x": 1, "y": 2}
    assert env["val"] == 2
    assert env["hasx"] is True
    assert env["total"] == 6
    assert env["tag"] == "ok"
