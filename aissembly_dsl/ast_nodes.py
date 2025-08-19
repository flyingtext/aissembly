from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


class Node:  # pragma: no cover - minimal base
    pass


@dataclass
class Program(Node):
    body: List[Node]


@dataclass
class Let(Node):
    name: str
    expr: Node
    mutable: bool = False


@dataclass
class Set(Node):
    name: str
    expr: Node


@dataclass
class If(Node):
    test: Node
    then: List[Node]
    otherwise: List[Node]


@dataclass
class For(Node):
    var: str
    iter: Node
    body: Node
    init: Node


@dataclass
class While(Node):
    test: Node
    body: Node
    init: Node


@dataclass
class ExprStmt(Node):
    expr: Node


@dataclass
class Break(Node):
    pass


@dataclass
class Continue(Node):
    pass


# Expressions ---------------------------------------------------------------


@dataclass
class Number(Node):
    value: int


@dataclass
class String(Node):
    value: str


@dataclass
class Name(Node):
    id: str


@dataclass
class Call(Node):
    func: Node
    args: List[Node]


@dataclass
class BinOp(Node):
    left: Node
    op: str
    right: Node


@dataclass
class IfExpr(Node):
    test: Node
    then: Node
    otherwise: Node


@dataclass
class Lambda(Node):
    params: List[str]
    body: Node
