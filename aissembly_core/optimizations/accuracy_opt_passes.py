import json
from collections.abc import Sequence
from ..executor import Executor

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

def accuracy_opt_passes_optimization(options, program) :
    f = open(options.llm, 'r', encoding='utf-8')
    llm_defs = f.read()
    f.close()

    _defs = json.loads(llm_defs)

    ind = None

    for n, item in enumerate(_defs) :
        if item['name'] == 'accuracy_opt_passes' :
            ind = n

    executor = Executor(llm_defs=_defs)

    for line_count, line in enumerate(program.statements) :
        for path, node in find_key_with_path(program.statements[line_count], 'prompt') :
            val = executor.call_llm(ind, args=[], kwargs={
                'system': 'You are a professional prompt engineer. Only to make the prompt more sophisticated.',
                'prompt': '''Sophistically engineer the GIVEN PROMPT. Output nothing more than the prompt only. No explaination. Mind that this is only a prompt engineering, not answering the prompt. Only make the GIVEN PROMPT more sophisticated.
                GIVEN PROMPT: ''' + node.value
            })
            if '</think>' in val :
                val = val.split('</think>')[1].strip()
            node.value = val
    return program