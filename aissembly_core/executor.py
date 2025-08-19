"""Execution engine for Aissembly minimal language."""
from __future__ import annotations

from typing import Any, Dict, Iterable
import json

from .parser import (
    Program,
    LetStmt,
    Var,
    Number,
    String,
    Call,
    ForLoop,
    WhileLoop,
    Cond,
    parse_program,
)


# Built-in operations
BUILTINS = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "div": lambda a, b: a / b,
    "mod": lambda a, b: a % b,
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gt": lambda a, b: a > b,
    "ge": lambda a, b: a >= b,
    "lt": lambda a, b: a < b,
    "le": lambda a, b: a <= b,
    "land": lambda a, b: a and b,
    "lor": lambda a, b: a or b,
    "lnot": lambda a: not a,
}


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
        # Placeholder for actual LLM call
        return {
            "model": spec.get("model", "unknown"),
            "name": name,
            "args": args,
            "kwargs": kwargs,
        }


def load_llm_defs(path: str) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["name"]: item for item in data}
