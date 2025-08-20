# === Unparser (Block-only pretty printer) ===
import json
from typing import Any, Dict, List, Tuple

from .parser import (
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

# --- atom helpers ---
def _quote(s: str) -> str:
    # Grammar가 ESCAPED_STRING("...")를 쓰므로 json.dumps로 안전 이스케이프
    return json.dumps(s, ensure_ascii=False)

def _indent(s: str, n: int = 4) -> str:
    pad = " " * n
    return "\n".join(pad + ln if ln else ln for ln in s.splitlines())

def _paren(s: str) -> str:
    return f"({s})"

def _is_atom_node(node: Any) -> bool:
    return isinstance(node, (Number, String, Boolean, Var, ListLiteral, DictLiteral))

def _is_blockish(node: Any) -> bool:
    return isinstance(node, (ForLoop, WhileLoop, Cond))

# --- op name mappings ---
_BINOP = {
    "op.add": "+",
    "op.sub": "-",
    "op.mul": "*",
    "op.div": "/",
    "op.mod": "%",
    "op.eq": "==",
    "op.neq": "!=",
    "op.lt": "<",
    "op.le": "<=",
    "op.gt": ">",
    "op.ge": ">=",
}
_BOOLBIN = {
    "op.land": "and",
    "op.lor": "or",
}
_UNARY = {
    "op.lnot": "not",
}

# --- index/slice chain unwrap: op.get / op.slice 를 [] 표기로 되살림 ---
def _unwrap_trailer_chain(node: Any):
    chain = []
    cur = node
    while isinstance(cur, Call) and cur.name in ("op.get", "op.slice") and cur.args:
        if cur.name == "op.get" and len(cur.args) == 2:
            base, idx = cur.args
            chain.append(("index", idx))
            cur = base
        elif cur.name == "op.slice":
            base = cur.args[0] if len(cur.args) >= 1 else None
            start = cur.args[1] if len(cur.args) >= 2 else None
            end   = cur.args[2] if len(cur.args) >= 3 else None
            chain.append(("slice", (start, end)))
            cur = base
        else:
            break
    chain.reverse()
    return cur, chain

# --- atom to source ---
def atom_to_source(node: Any) -> str:
    if isinstance(node, Number):
        return str(node.value)
    if isinstance(node, String):
        return _quote(node.value)
    if isinstance(node, Boolean):
        return "true" if node.value else "false"
    if isinstance(node, Var):
        return node.name
    if isinstance(node, ListLiteral):
        return "[" + ", ".join(expr_to_source(e) for e in node.elements) + "]"
    if isinstance(node, DictLiteral):
        return "{" + ", ".join(f"{expr_to_source(k)}: {expr_to_source(v)}" for (k, v) in node.items) + "}"
    return expr_to_source(node)

# --- expr to source (BLOCK-ONLY) ---
def expr_to_source(node: Any) -> str:
    # 1) op.get / op.slice 체인 우선 복원
    base, trailers = _unwrap_trailer_chain(node)
    if trailers:
        left = expr_to_source(base) if not _is_atom_node(base) else atom_to_source(base)
        for kind, payload in trailers:
            if kind == "index":
                left += f"[{expr_to_source(payload)}]"
            else:  # slice
                s, e = payload
                s_str = expr_to_source(s) if s is not None else ""
                e_str = expr_to_source(e) if e is not None else ""
                left += f"[{s_str}:{e_str}]"
        return left

    # 2) 원자
    if isinstance(node, Number):
        return str(node.value)
    if isinstance(node, String):
        return _quote(node.value)
    if isinstance(node, Boolean):
        return "true" if node.value else "false"
    if isinstance(node, Var):
        return node.name
    if isinstance(node, ListLiteral):
        return "[" + ", ".join(expr_to_source(e) for e in node.elements) + "]"
    if isinstance(node, DictLiteral):
        return "{" + ", ".join(f"{expr_to_source(k)}: {expr_to_source(v)}" for (k, v) in node.items) + "}"

    # 3) 조건(항상 블록 표기)
    if isinstance(node, Cond):
        test = expr_to_source(node.test)
        then_src = expr_to_source(node.then)
        else_src = expr_to_source(node.else_)
        return (
            f"cond(test={test}):\n"
            f"    then:\n"
            f"{_indent('-> ' + then_src, 8)}\n"
            f"    else:\n"
            f"{_indent('-> ' + else_src, 8)}"
        )

    # 4) 루프(항상 블록 표기)
    if isinstance(node, ForLoop):
        rng = f"range({expr_to_source(node.start)}, {expr_to_source(node.end)}"
        if not (isinstance(node.step, Number) and node.step.value == 1):
            rng += f", {expr_to_source(node.step)}"
        rng += ")"
        head = f"for ({rng}, init={expr_to_source(node.init)}):"
        body = "-> " + expr_to_source(node.body)
        return f"{head}\n{_indent(body, 4)}"

    if isinstance(node, WhileLoop):
        head = f"while (test={expr_to_source(node.test)}, init={expr_to_source(node.init)}):"
        body = "-> " + expr_to_source(node.body)
        return f"{head}\n{_indent(body, 4)}"

    # 5) 연산/호출
    if isinstance(node, Call):
        # 단항 NOT
        if node.name in _UNARY and len(node.args) == 1:
            inner_node = node.args[0]
            inner = expr_to_source(inner_node)
            return f"{_UNARY[node.name]} {_paren(inner) if not _is_atom_node(inner_node) else inner}"

        # 단항 음수: op.sub(0, x)
        if node.name == "op.sub" and len(node.args) == 2 and isinstance(node.args[0], Number) and node.args[0].value == 0:
            x = node.args[1]
            inner = expr_to_source(x)
            return f"-{_paren(inner) if not _is_atom_node(x) else inner}"

        # 산술/비교
        if node.name in _BINOP and len(node.args) == 2:
            a, b = node.args
            sa = expr_to_source(a)
            sb = expr_to_source(b)
            if not _is_atom_node(a): sa = _paren(sa)
            if not _is_atom_node(b): sb = _paren(sb)
            return f"{sa} {_BINOP[node.name]} {sb}"

        # 불리언 and/or
        if node.name in _BOOLBIN and len(node.args) == 2:
            a, b = node.args
            sa = expr_to_source(a)
            sb = expr_to_source(b)
            if not _is_atom_node(a): sa = _paren(sa)
            if not _is_atom_node(b): sb = _paren(sb)
            return f"{sa} {_BOOLBIN[node.name]} {sb}"

        # 일반 호출
        arg_strs: List[str] = []
        for a in node.args:
            arg_strs.append(expr_to_source(a))
        for k in sorted(node.kwargs.keys()):
            arg_strs.append(f"{k}={expr_to_source(node.kwargs[k])}")
        return f"{node.name}(" + ", ".join(arg_strs) + ")"

    # 6) fallback
    return f"<unknown:{type(node).__name__}>"

# --- stmt/program ---
def stmt_to_source(stmt: Any) -> str:
    if isinstance(stmt, LetStmt):
        return f"let {stmt.name} = {expr_to_source(stmt.expr)};"
    if _is_blockish(stmt):
        # 블록식은 문장 끝 세미콜론 없이 그대로
        return expr_to_source(stmt)
    # 보통의 표현식 문장
    return expr_to_source(stmt) + ";"

def program_to_source(program: Program) -> str:
    return "\n".join(stmt_to_source(s) for s in program.statements)
