import os
import sys
from pathlib import Path
import urllib.request

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor, load_llm_defs

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"
LLM_DEFS = ROOT / "llm_functions.json"


class DummyResp:
    def __init__(self, body: str = "{}"):
        self.body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body

    def __iter__(self):
        return iter(self.body.splitlines(True))


@pytest.mark.parametrize("path", sorted(EXAMPLES_DIR.rglob("*.asl")))
def test_example_runs(path, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req: DummyResp("{}"))
    src = path.read_text()
    prog = parse_program(src)
    exe = Executor(llm_defs=load_llm_defs(str(LLM_DEFS)))
    env = exe.run(prog)
    assert isinstance(env, dict)
