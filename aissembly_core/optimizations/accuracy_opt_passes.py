import json
import re
from collections.abc import Sequence
from .ebnf import aissembly_ebnf
from ..executor import Executor
from ..util.find_functions import find_function_blocks_excluding_strings

from ..parser import (
    Program,
    LetStmt,
    Var,
    Number,
    String,
    ListLiteral,
    DictLiteral,
    Call,
    ForLoop,
    WhileLoop,
    Cond,
    Boolean,
    parse_program,
)

def find_key_with_path(obj, target_key, path=(), _seen=None):
    """컨테이너(객체.__dict__, dict, list/tuple)를 재귀 탐색하며
    target_key(예: 'prompt')를 찾으면 (path, value)를 yield."""
    if _seen is None:
        _seen = set()
    oid = id(obj)
    if oid in _seen:
        return
    _seen.add(oid)

    # 1) dict: 키 직접 확인 + 값들 재귀
    if isinstance(obj, dict):
        if target_key in obj:
            yield (path + (target_key,), obj[target_key])
        for k, v in obj.items():
            yield from find_key_with_path(v, target_key, path + (str(k),), _seen)

    # 2) list/tuple 등 시퀀스: 인덱스로 재귀
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        for i, v in enumerate(obj):
            yield from find_key_with_path(v, target_key, path + (f'[{i}]',), _seen)

    # 3) 일반 객체: __dict__로 재귀 (+ 해당 이름의 속성이면 반환)
    elif hasattr(obj, "__dict__"):
        d = obj.__dict__
        if target_key in d:
            yield (path + (target_key,), d[target_key])
        for k, v in d.items():
            yield from find_key_with_path(v, target_key, path + (k,), _seen)

    # 리프면 종료
    else:
        return

def accuracy_opt_passes_optimization(program_source, options) :
    f = open(options.llm, 'r', encoding='utf-8')
    llm_defs = f.read()
    f.close()

    _defs = json.loads(llm_defs)

    ind = None

    names = []

    for n, item in enumerate(_defs) :
        names.append(item['name'])
        if item['name'] == 'accuracy_opt_passes' :
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

        if prompt.endswith(' ') or prompt.endswith(',') or prompt.endswith(')') :
            prompt = prompt[:len(prompt) - 1]

        prompt = prompt.strip()

        sentence = executor.call_llm(ind, args=[], kwargs={
            'system': 'You are a professional prompt engineer. Only to make the prompt more sophisticated. The GIVEN PROMPT is a part of Aissembly source code. Preserve the syntax of given text with following rule:' + aissembly_ebnf,
            'prompt': '''Sophistically engineer the GIVEN PROMPT without omitting the smallest details of given conditions. Output nothing more than the prompt only. No explaination. Mind that this is only a prompt engineering, not answering the prompt. Only make the GIVEN PROMPT more sophisticated without omitting the given conditions. Output the formulation of string value in correct standard of Aissembly source code string syntax without using inline function.
            GIVEN PROMPT: ''' + prompt
        })

        total = []

        if sentence.strip() == '' : continue
        
        # sentence = sentence.replace('"', '\\"')

        replaced = str(full)
        replaced = 'let ACCURACY_OPT_' + str(cnt) + ' = ' + replaced.replace(prompt, '"Question : " + ' + sentence) +';'
        total.append(replaced)
        cnt = cnt + 1
        
        pos = None
        try :
            pos = ret.find(full)
        except :
            continue

        enter_place = None
        try :
            enter_place = ret.lfind(';', pos)
        except :
            enter_place = 0

        ret = ret.replace(full, 'ACCURACY_OPT_' + str(cnt - 1), 1)
        ret = ret[:enter_place] + '\n' + '\n'.join(total) + '\n' + ret[enter_place:]

    print(ret)
    return ret



'''
'system': 'You are a professional prompt engineer. Only to make the prompt more sophisticated.',
'prompt': 'Sophistically engineer the GIVEN PROMPT without omitting the smallest details of given conditions. Output nothing more than the prompt only. No explaination. Mind that this is only a prompt engineering, not answering the prompt. Only make the GIVEN PROMPT more sophisticated without omitting the given conditions.
GIVEN PROMPT: ' + node.value
'''