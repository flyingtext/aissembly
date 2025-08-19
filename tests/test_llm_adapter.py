import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program
from aissembly_core.executor import Executor, load_llm_defs


def test_python_adapter(tmp_path):
    adapter_file = tmp_path / "adapter.py"
    adapter_file.write_text("""
from typing import Any

def add_adapter(a: Any, b: Any) -> Any:
    return a + b
""")

    llm_json = tmp_path / "defs.json"
    llm_json.write_text(json.dumps([
        {
            "name": "py_add",
            "model": "local",
            "adapter": {
                "type": "python",
                "path": str(adapter_file),
                "function": "add_adapter"
            },
            "parameters": {"type": "object", "properties": {}}
        }
    ]))

    llm_defs = load_llm_defs(str(llm_json))
    program = parse_program("let result = py_add(1, 2)")
    exe = Executor(llm_defs=llm_defs)
    env = exe.run(program)
    assert env["result"] == 3

