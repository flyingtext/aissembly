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
    LazyStr,
    lazy_to_str,
    eval_node,
    parse_program,
)

def find_key_with_path(obj, target_key, path=(), _seen=None,
                       _parent=None, _gparent=None, _ggparent=None):
    """
    컨테이너(객체.__dict__, dict, list/tuple)를 재귀 탐색.
    target_key를 찾으면 (path_tuple, value_node,
                        parent, grandparent, great_grandparent) 를 yield.
    """
    if _seen is None:
        _seen = set()
    oid = id(obj)
    if oid in _seen:
        return
    _seen.add(oid)

    # 1) dict: 키 직접 확인 + 값들 재귀
    if isinstance(obj, dict):
        if target_key in obj:
            yield (path + (target_key,), obj[target_key], obj, _parent, _gparent)
        for k, v in obj.items():
            # 조상 포인터 한 칸씩 밀어서 전달
            yield from find_key_with_path(
                v, target_key, path + (str(k),), _seen,
                _parent=obj, _gparent=_parent, _ggparent=_gparent
            )

    # 2) list/tuple 등 시퀀스: 인덱스로 재귀
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        for i, v in enumerate(obj):
            yield from find_key_with_path(
                v, target_key, path + (f'[{i}]',), _seen,
                _parent=obj, _gparent=_parent, _ggparent=_gparent
            )

    # 3) 일반 객체: __dict__로 재귀
    elif hasattr(obj, "__dict__"):
        d = obj.__dict__
        if target_key in d:
            yield (path + (target_key,), d[target_key], obj, _parent, _gparent)
        for k, v in d.items():
            yield from find_key_with_path(
                v, target_key, path + (k,), _seen,
                _parent=obj, _gparent=_parent, _ggparent=_gparent
            )

    # 리프면 종료
    else:
        return

def decomposition_opt_passes_optimization(options, program) :
    f = open(options.llm, 'r', encoding='utf-8')
    llm_defs = f.read()
    f.close()

    _defs = json.loads(llm_defs)

    ind = None

    for n, item in enumerate(_defs) :
        if item['name'] == 'decomposition_opt_passes' :
            ind = n

    executor = Executor(llm_defs=_defs)
    
    for line_count, line in enumerate(program.statements) :
        for path, node, parent, pparent, ppparent in find_key_with_path(program.statements[line_count], 'prompt') :
            nodes = []
            val = executor.call_llm(ind, args=[], kwargs={
                'system': 'You are a professional prompt engineer. Only to make the prompt much more sophisticated.',
                'prompt': '''Split GIVEN PROMPT in several steps owning its answer from previous step. The prompts targets making answers better step-by-step. Output of the engineered prompt only step by step in line by each line. Output nothing more than the prompt only step by step in line by each line. No step notation. No explaination. Only the prompts to be placed each in line. Each prompts must not have to loose original attempt of GIVEN PROMPT.
                GIVEN PROMPT: ''' + node.value
            })
            if '</think>' in val :
                val = val.split('</think>')[1].strip()
            
            prompts = val.strip().replace('\n\n', '\n').split('\n')

            before_node = None

            for p in prompts :
                if p == '' : continue
                if before_node is None :
                    _kwargs = parent.copy()
                    _kwargs['prompt'] = p

                    _node = Call(name = pparent.name, args=pparent.args, kwargs=_kwargs)
                    nodes.append(_node)
                    before_node = _node
                else :
                    _kwargs = parent.copy()
                    _kwargs['prompt'] = '[[[[Context]]]] ' + LazyStr(lambda: str(eval_node(before_node))) + '\n[[[[Prompt]]]] ' + p

                    _node = Call(name = pparent.name, args=pparent.args, kwargs=_kwargs)
                    nodes.append(_node)
                    before_node = _node

            ppparent = nodes
    return program