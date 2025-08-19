import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aissembly_core.parser import parse_program, ParserOptions

PROGRAM = """
let x = add(7, 6)
let tag = cond(test=ge(x, 10)) -> \"ok\" ::else-> \"ng\"
let total = for(range(1, 4), init=0) -> add(acc, i)
let steps = while(test=lt(acc, 3), init=0) -> add(acc, 1)
"""

def test_parser_options_acceptance():
    opts = ParserOptions(
        accuracy_opt_passes=1,
        decomposition_opt_passes=1,
        integration_opt_passes=1,
        loop_to_operation_opt_passes=1,
        operation_to_loop_opt_passes=1,
        condition_to_operation_opt_passes=1,
    )
    prog = parse_program(PROGRAM, options=opts)
    assert len(prog.statements) == 4
