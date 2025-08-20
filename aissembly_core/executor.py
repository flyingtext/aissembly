"""Execution engine for Aissembly minimal language."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List
import json
import importlib.util
import urllib.request
import math

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
    parse_program,
)


def _set(obj, key, val):
    obj[key] = val
    return obj


def _append(lst: List[Any], val: Any):
    lst.append(val)
    return lst


def _push(lst: List[Any], val: Any) -> int:
    lst.append(val)
    return len(lst)


def _pop(lst: List[Any]):
    return lst.pop()


def _merge(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    res = dict(a)
    res.update(b)
    return res


def _split(s: str, sep: str) -> List[str]:
    return s.split(sep)


def _join(items: List[str], sep: str) -> str:
    return sep.join(items)


def _type(obj: Any) -> str:
    return type(obj).__name__


def _assert(cond: bool, msg: str = "Assertion failed") -> bool:
    if not cond:
        raise AssertionError(msg)
    return True


def _print(*args: Any) -> None:
    print(*args)


# Built-in operations
BUILTINS = {
    "op.add": lambda a, b: a + b,
    "op.sub": lambda a, b: a - b,
    "op.mul": lambda a, b: a * b,
    "op.div": lambda a, b: a / b,
    "op.mod": lambda a, b: a % b,
    "op.eq": lambda a, b: a == b,
    "op.neq": lambda a, b: a != b,
    "op.gt": lambda a, b: a > b,
    "op.ge": lambda a, b: a >= b,
    "op.lt": lambda a, b: a < b,
    "op.le": lambda a, b: a <= b,
    "op.land": lambda a, b: a and b,
    "op.lor": lambda a, b: a or b,
    "op.lnot": lambda a: not a,
    "op.concat": lambda a, b: a + b,
    "op.len": lambda x: len(x),
    "op.substr": lambda s, start, end: s[start:end],
    "op.get": lambda obj, key: obj[key],
    "op.set": _set,
    "op.append": _append,
    "op.slice": lambda obj, start, end: obj[start:end],
    "op.has": lambda d, key: key in d,
}

# Alias names used in examples
BUILTINS.update(
    {
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "max": max,
        "min": min,
        "len": BUILTINS["op.len"],
        "get": BUILTINS["op.get"],
        "set": BUILTINS["op.set"],
        "slice": BUILTINS["op.slice"],
        "print": _print,
        "pop": _pop,
        "push": _push,
        "split": _split,
        "join": _join,
        "merge": _merge,
        "type": _type,
        "assert": _assert,
    }
)


class Executor:
    def __init__(self, llm_defs: Dict[str, Dict[str, Any]] | None = None):
        self.llm_defs = llm_defs or {}

    def run(self, program: Program, env: Dict[str, Any] | None = None) -> Dict[str, Any]:
        env = env or {}
        for stmt in program.statements:
            if isinstance(stmt, LetStmt):
                env[stmt.name] = self.eval_expr(stmt.expr, env)
            else:
                self.eval_expr(stmt, env)
        return env

    def eval_expr(self, node: Any, env: Dict[str, Any]) -> Any:
        if isinstance(node, Number):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, ListLiteral):
            return [self.eval_expr(e, env) for e in node.elements]
        if isinstance(node, DictLiteral):
            return {
                self.eval_expr(k, env): self.eval_expr(v, env) for k, v in node.items
            }
        if isinstance(node, Var):
            return env[node.name]
        if isinstance(node, Call):
            return self.eval_call(node, env)
        if isinstance(node, ForLoop):
            return self.eval_for(node, env)
        if isinstance(node, WhileLoop):
            return self.eval_while(node, env)
        if isinstance(node, Cond):
            test = self.eval_expr(node.test, env)
            branch = node.then if test else node.else_
            return self.eval_expr(branch, env)
        raise TypeError(f"Unsupported node: {node}")

    def eval_call(self, node: Call, env: Dict[str, Any]) -> Any:
        args = [self.eval_expr(a, env) for a in node.args]
        kwargs = {k: self.eval_expr(v, env) for k, v in node.kwargs.items()}
        if node.name in BUILTINS:
            return BUILTINS[node.name](*args, **kwargs)
        if node.name in self.llm_defs:
            return self.call_llm(node.name, args, kwargs)
        raise ValueError(f"Unknown function: {node.name}")

    def eval_for(self, node: ForLoop, env: Dict[str, Any]) -> Any:
        start = self.eval_expr(node.start, env)
        end = self.eval_expr(node.end, env)
        step = self.eval_expr(node.step, env)
        acc = self.eval_expr(node.init, env)
        for i in range(start, end, step):
            inner_env = env.copy()
            inner_env.update({"i": i, "acc": acc})
            acc = self.eval_expr(node.body, inner_env)
        return acc

    def eval_while(self, node: WhileLoop, env: Dict[str, Any]) -> Any:
        acc = self.eval_expr(node.init, env)
        while True:
            inner_env = env.copy()
            inner_env["acc"] = acc
            test = self.eval_expr(node.test, inner_env)
            if not test:
                break
            acc = self.eval_expr(node.body, inner_env)
        return acc

    def call_llm(self, name: str, args: Iterable[Any], kwargs: Dict[str, Any]) -> Any:
        spec = self.llm_defs[name]
        adapter = spec.get("adapter")
        if adapter is None:
            return {
                "model": spec.get("model", "unknown"),
                "name": name,
                "args": args,
                "kwargs": kwargs,
            }

        atype = adapter.get("type")
        if atype == "python":
            path = adapter.get("path")
            func_name = adapter.get("function")
            if not path or not func_name:
                raise ValueError("Python adapter requires 'path' and 'function'")
            spec_obj = importlib.util.spec_from_file_location("llm_adapter", path)
            if spec_obj is None or spec_obj.loader is None:
                raise ImportError(f"Cannot load adapter from {path}")
            module = importlib.util.module_from_spec(spec_obj)
            spec_obj.loader.exec_module(module)
            func = getattr(module, func_name)
            return func(*args, **kwargs)

        if atype == "http":
            url = adapter.get("url")
            method = adapter.get("method", "POST").upper()
            headers = {"Content-Type": "application/json"}
            headers.update(adapter.get("headers", {}))
            payload = adapter.get(
                "payload",
                {"model": spec.get("model"), "name": name, "args": args, "kwargs": kwargs},
            )
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)

        raise ValueError(f"Unsupported adapter type: {atype}")


def load_llm_defs(path: str) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["name"]: item for item in data}
