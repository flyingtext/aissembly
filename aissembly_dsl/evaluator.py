from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from . import ast_nodes as ast
from .core_ir import ENV


@dataclass
class Box:
    value: Any


def initial_env() -> Dict[str, Any]:
    env = {
        **ENV,
        "range": range,
        "true": True,
        "false": False,
        "none": None,
        "loop_for": ENV["loop"]["for"],
        "loop_while": ENV["loop"]["while"],
    }
    return env


def resolve(name: str, env: Dict[str, Any]) -> Any:
    parts = name.split(".")
    obj = env[parts[0]]
    if isinstance(obj, Box):
        obj = obj.value
    for p in parts[1:]:
        obj = getattr(obj, p) if hasattr(obj, p) else obj[p]
    return obj


def evaluate(node: ast.Node, env: Dict[str, Any] | None = None) -> Any:
    if env is None:
        env = initial_env()
    if isinstance(node, ast.Program):
        result = None
        for stmt in node.body:
            result = evaluate(stmt, env)
        return result
    if isinstance(node, ast.Let):
        val = evaluate(node.expr, env)
        env[node.name] = Box(val) if node.mutable else val
        return val
    if isinstance(node, ast.Set):
        box = env[node.name]
        if isinstance(box, Box):
            box.value = evaluate(node.expr, env)
        else:
            raise RuntimeError("cannot set immutable variable")
        return box.value
    if isinstance(node, ast.ExprStmt):
        return evaluate(node.expr, env)
    if isinstance(node, ast.Number):
        return node.value
    if isinstance(node, ast.String):
        return node.value
    if isinstance(node, ast.Name):
        return resolve(node.id, env)
    if isinstance(node, ast.Call):
        func = evaluate(node.func, env)
        args = [evaluate(a, env) for a in node.args]
        return func(*args)
    if isinstance(node, ast.Lambda):
        def fn(*args):
            local = env.copy()
            for p, a in zip(node.params, args):
                local[p] = a
            return evaluate(node.body, local)
        return fn
    raise TypeError(f"unsupported node {node}")
