import json
from collections.abc import Sequence
from ..executor import Executor

def integration_opt_passes_optimization(program_source):
    f = open(options.llm, 'r', encoding='utf-8')
    llm_defs = f.read()
    f.close()

    _defs = json.loads(llm_defs)

    ind = None

    for n, item in enumerate(_defs) :
        if item['name'] == 'integration_opt_passes_optimization' :
            ind = n

    executor = Executor(llm_defs=_defs)
    val = executor.call_llm(ind, args=[], kwargs={
                'system': 'You are a professional programming architecture developer. Only to make the more code optimized.',
                'prompt': '''Split GIVEN PROMPT in several steps owning its answer from previous step without omitting the smallest details of given conditions. The prompts targets making answers better step-by-step without omitting the given conditions. Output of the engineered prompt only step by step in line by each line without omitting the given conditions. Output nothing more than the prompt only step by step in line by each lin without omitting the given conditionse. No step notation. No explaination. Only the prompts to be placed each in line without omitting the given conditions. Each prompts must not have to loose original attempt of GIVEN PROMPT.
                GIVEN PROMPT: ''' + node.value
            })