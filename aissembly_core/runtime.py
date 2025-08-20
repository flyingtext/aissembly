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
    parser.add_argument("--accuracy_opt_passes", 
        dest="accuracy_opt_passes", 
        type=int, 
        default=0, 
        help="Prompt accuracy optimization"
    )
    parser.add_argument("--decomposition_opt_passes", 
        dest="decomposition_opt_passes", 
        type=int, 
        default=0, 
        help="Prompt decomposition optimization"
    )
    parser.add_argument("--integration_opt_passes", 
        dest="integration_opt_passes", 
        type=int, 
        default=0, 
        help="Prompt integration optimization"
    )
    parser.add_argument("--loop_to_operation_opt_passes", 
        dest="loop_to_operation_opt_passes", 
        type=int, 
        default=0, 
        help="Loop to operation optimization"
    )
    parser.add_argument("--operation_to_loop_opt_passes", 
        dest="operation_to_loop_opt_passes", 
        type=int, 
        default=0, 
        help="Operation to loop optimization"
    )
    parser.add_argument("--condition_to_operation_opt_passes", 
        dest="condition_to_operation_opt_passes", 
        type=int, 
        default=0, 
        help="Condition to operation optimization"
    )
    parser.add_argument(
        "--reparse-iterations",
        dest="reparse_iterations",
        type=int,
        default=1,
        help="Number of line-by-line re-parsing iterations to run",
    )
    args = parser.parse_args(argv)

    with open(args.program, "r", encoding="utf-8") as f:
        source = f.read()

    prog = parse_program(source, options=args)

    llm_defs: Dict[str, Dict] | None = None
    if args.llm:
        llm_defs = load_llm_defs(args.llm)

    executor = Executor(llm_defs=llm_defs)
    env = executor.run(prog)
    print(json.dumps(env, ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
