"""CLI to parse and execute Aissembly programs."""
from __future__ import annotations

import argparse
import json
from typing import Dict

from .parser import parse_program
from .executor import Executor, load_llm_defs


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run Aissembly program")
    parser.add_argument("program", help="Path to program file")
    parser.add_argument("--llm", dest="llm", help="Path to LLM definition JSON", default=None)
    args = parser.parse_args(argv)

    with open(args.program, "r", encoding="utf-8") as f:
        source = f.read()
    prog = parse_program(source)

    llm_defs: Dict[str, Dict] | None = None
    if args.llm:
        llm_defs = load_llm_defs(args.llm)

    executor = Executor(llm_defs=llm_defs)
    env = executor.run(prog)
    print(json.dumps(env, ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
