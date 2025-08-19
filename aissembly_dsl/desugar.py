from __future__ import annotations

from . import ast_nodes as ast

OP_MAP = {
    "+": "op.add",
    "-": "op.sub",
    "*": "op.mul",
    "/": "op.div",
    ">": "op.gt",
    "<": "op.lt",
    ">=": "op.ge",
    "<=": "op.le",
    "==": "op.eq",
    "!=": "op.ne",
}


def desugar(node: ast.Node) -> ast.Node:
    if isinstance(node, ast.Program):
        return ast.Program([desugar(n) for n in node.body])
    if isinstance(node, ast.Let):
        return ast.Let(node.name, desugar(node.expr), node.mutable)
    if isinstance(node, ast.Set):
        return ast.Set(node.name, desugar(node.expr))
    if isinstance(node, ast.ExprStmt):
        return ast.ExprStmt(desugar(node.expr))
    if isinstance(node, (ast.Number, ast.String, ast.Name)):
        return node
    if isinstance(node, ast.Call):
        return ast.Call(desugar(node.func), [desugar(a) for a in node.args])
    if isinstance(node, ast.BinOp):
        func = ast.Name(OP_MAP[node.op])
        return ast.Call(func, [desugar(node.left), desugar(node.right)])
    if isinstance(node, ast.IfExpr):
        return ast.Call(
            ast.Name("cond"),
            [
                ast.Lambda([], desugar(node.test)),
                ast.Lambda([], desugar(node.then)),
                ast.Lambda([], desugar(node.otherwise)),
            ],
        )
    if isinstance(node, ast.For):
        return ast.Call(
            ast.Name("loop.for"),
            [
                desugar(node.iter),
                ast.Lambda([node.var, "acc"], desugar(node.body)),
                desugar(node.init),
            ],
        )
    if isinstance(node, ast.While):
        return ast.Call(
            ast.Name("loop.while"),
            [
                ast.Lambda([], desugar(node.test)),
                ast.Lambda(["acc"], desugar(node.body)),
                desugar(node.init),
            ],
        )
    if isinstance(node, ast.Lambda):
        return ast.Lambda(node.params, desugar(node.body))
    raise TypeError(f"unsupported node {node}")
