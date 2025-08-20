import json
import re
from collections.abc import Sequence
from .ebnf import aissembly_ebnf
from ..executor import Executor
from ..util.find_functions import find_function_blocks_excluding_strings

def decomposition_opt_passes_optimization(program_source, options) :
    f = open(options.llm, 'r', encoding='utf-8')
    llm_defs = f.read()
    f.close()

    _defs = json.loads(llm_defs)

    ind = None

    names = []

    for n, item in enumerate(_defs) :
        names.append(item['name'])
        if item['name'] == 'decomposition_opt_passes' :
            ind = n

    executor = Executor(llm_defs=_defs)

    ret = str(program_source)
    
    cnt = 0

    for full, name, params, span in find_function_blocks_excluding_strings(program_source, names) :
        # ollama_chat(prompt="What is an essence of Philosophy?") /  ollama_chat /  prompt="What is an essence of Philosophy?" / (6, 61)

        try :
            pattern = re.compile(r'prompt\s*=\s*(.*?)(?:,|$)')
            prompt = pattern.search(params).group(1).strip()
        except Exception as e :
            print(e)
            continue

        prompt = prompt.strip()

        val = executor.call_llm(ind, args=[], kwargs={
            'system': 'You are a professional prompt engineer and a programmer. Only to make the prompt much more sophisticated. You follow the strict rule that not making syntax error by make appropriate use of positions of the operaters in the string that matter with the source code. The GIVEN PROMPT is a part of Aissembly source code. Preserve the syntax of given text with following rule:' + aissembly_ebnf,
            'prompt': '''Split GIVEN PROMPT in several steps owning its answer from previous step without omitting the smallest details of given conditions. The prompts targets making answers better step-by-step without omitting the given conditions. Output of the engineered prompt only step by step in line by each line without omitting the given conditions. Output nothing more than the prompt only step by step in line by each lin without omitting the given conditionse. No step notation. No explaination. Only the prompts to be placed each in line without omitting the given conditions. Each prompts must not have to loose original attempt of GIVEN PROMPT. Output the formulation of string value in correct standard of Aissembly source code string syntax without using inline function.
            GIVEN PROMPT: ''' + prompt
        })

        val = val.replace('\n\n', '\n').split('\n')

        before_sent = None

        total = []

        n = None

        for n, sentence in enumerate(val) :
            if sentence.strip() == '' : continue
            # sentence = sentence.replace('"', '\\"')
            if before_sent is None :
                replaced = str(full)
                replaced = 'let DECOMPOSITION_OPT_' + str(cnt) + ' = ' + replaced.replace(prompt, '"Question : " + ' + sentence) +';'
                total.append(replaced)
                cnt = cnt + 1
                before_sent = sentence
            else :
                replaced = str(full)
                replaced = 'let DECOMPOSITION_OPT_' + str(cnt) + ' = ' + replaced.replace(prompt, 'DECOMPOSITION_OPT_' + str(cnt-1) + ' + " Question : " + ' + sentence) +';'
                total.append(replaced)
                cnt = cnt + 1
                before_sent = sentence
        
        pos = None
        try :
            pos = ret.lfind(full)
        except :
            continue

        enter_place = None
        try :
            enter_place = ret.lfind(';', pos)
        except :
            enter_place = 0

        ret = ret.replace(full, 'DECOMPOSITION_OPT_' + str(cnt - 1), 1)
        ret = ret[:enter_place] + '\n' + '\n'.join(total) + '\n' + ret[enter_place:]

    print(ret)
    return ret