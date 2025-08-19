from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List


@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"{self.kind}({self.value!r})@{self.line}:{self.col}"


KEYWORDS = {
    "let",
    "mut",
    "set",
    "fn",
    "if",
    "else",
    "for",
    "in",
    "while",
    "init",
    "break",
    "continue",
    "true",
    "false",
    "none",
}

TOKEN_RE = re.compile(
    r"(?:"
    r"(?P<number>\d+)|"
    r"(?P<string>'[^']*'|\"[^\"]*\")|"
    r"(?P<eq>=)|"
    r"(?P<op>==|!=|>=|<=|->|[+\-*/%><])|"
    r"(?P<ident>[A-Za-z_][A-Za-z0-9_]*)|"
    r"(?P<punct>[(),:])"
    r")"
)


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []
    indent_stack = [0]
    lines = src.splitlines()
    for lineno, line in enumerate(lines, 1):
        if line.strip() == "" or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent > indent_stack[-1]:
            tokens.append(Token("INDENT", "", lineno, 1))
            indent_stack.append(indent)
        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "", lineno, 1))
        pos = indent
        line_len = len(line)
        while pos < line_len:
            while pos < line_len and line[pos] in " \t":
                pos += 1
            if pos >= line_len or line[pos] == '#':
                break
            m = TOKEN_RE.match(line, pos)
            if not m:
                raise SyntaxError(f"unknown token at line {lineno} col {pos+1}")
            kind = m.lastgroup or ""
            text = m.group(kind)
            if kind == "ident":
                if text in KEYWORDS:
                    kind = text.upper()
                else:
                    kind = "IDENT"
            elif kind == "number":
                kind = "NUMBER"
            elif kind == "string":
                kind = "STRING"
            elif kind == "eq":
                kind = "EQUAL"
            elif kind == "op":
                if text == "->":
                    kind = "ARROW"
                else:
                    kind = "OP"
            elif kind == "punct":
                if text == ",":
                    kind = "COMMA"
                elif text == ":":
                    kind = "COLON"
                elif text == "(":
                    kind = "LPAREN"
                elif text == ")":
                    kind = "RPAREN"
            tokens.append(Token(kind, text, lineno, m.start() + 1))
            pos = m.end()
        tokens.append(Token("NEWLINE", "", lineno, line_len + 1))
    while len(indent_stack) > 1:
        tokens.append(Token("DEDENT", "", lineno + 1, 1))
        indent_stack.pop()
    tokens.append(Token("EOF", "", lineno + 1, 1))
    return tokens
