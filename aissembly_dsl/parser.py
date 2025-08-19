from __future__ import annotations

from typing import List

from .tokenizer import Token, tokenize
from . import ast_nodes as ast


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @classmethod
    def from_source(cls, src: str) -> "Parser":
        return cls(tokenize(src))

    # basic helpers -----------------------------------------------------
    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _accept(self, kind: str) -> bool:
        if self._peek().kind == kind:
            self.pos += 1
            return True
        return False

    def _expect(self, kind: str) -> Token:
        tok = self._peek()
        if tok.kind != kind:
            raise SyntaxError(f"expected {kind} but got {tok.kind}")
        self.pos += 1
        return tok

    # parsing -----------------------------------------------------------
    def parse(self) -> ast.Program:
        body: List[ast.Node] = []
        while self._peek().kind != "EOF":
            if self._peek().kind == "NEWLINE":
                self.pos += 1
                continue
            body.append(self.parse_stmt())
        return ast.Program(body)

    def parse_stmt(self) -> ast.Node:
        tok = self._peek()
        if tok.kind in {"LET", "MUT"}:
            self.pos += 1
            name = self._expect("IDENT").value
            self._expect("EQUAL")
            expr = self.parse_expr()
            return ast.Let(name, expr, mutable=(tok.kind == "MUT"))
        if tok.kind == "SET":
            self.pos += 1
            name = self._expect("IDENT").value
            self._expect("EQUAL")
            expr = self.parse_expr()
            return ast.Set(name, expr)
        if tok.kind == "IF":
            return self.parse_if_stmt()
        if tok.kind == "FOR":
            return self.parse_for()
        if tok.kind == "WHILE":
            return self.parse_while()
        if tok.kind == "BREAK":
            self.pos += 1
            return ast.Break()
        if tok.kind == "CONTINUE":
            self.pos += 1
            return ast.Continue()
        # expression statement
        expr = self.parse_expr()
        return ast.ExprStmt(expr)

    def parse_block(self) -> List[ast.Node]:
        self._expect("NEWLINE")
        self._expect("INDENT")
        stmts: List[ast.Node] = []
        while self._peek().kind != "DEDENT":
            stmts.append(self.parse_stmt())
            if self._peek().kind == "NEWLINE":
                self.pos += 1
        self._expect("DEDENT")
        return stmts

    def parse_if_stmt(self) -> ast.If:
        self._expect("IF")
        test = self.parse_expr()
        self._expect("COLON")
        then = self.parse_block()
        otherwise: List[ast.Node] = []
        if self._peek().kind == "ELSE":
            self.pos += 1
            self._expect("COLON")
            otherwise = self.parse_block()
        return ast.If(test, then, otherwise)

    def parse_loop_body(self) -> ast.Node:
        self._expect("NEWLINE")
        self._expect("INDENT")
        self._expect("ARROW")
        expr = self.parse_expr()
        if self._peek().kind == "NEWLINE":
            self.pos += 1
        self._expect("DEDENT")
        return expr

    def parse_for(self) -> ast.For:
        self._expect("FOR")
        var = self._expect("IDENT").value
        self._expect("IN")
        iter_expr = self.parse_expr()
        self._expect("COLON")
        body = self.parse_loop_body()
        init = ast.Name("none")
        if self._peek().kind == "INIT":
            self.pos += 1
            init = self.parse_expr()
        return ast.For(var, iter_expr, body, init)

    def parse_while(self) -> ast.While:
        self._expect("WHILE")
        test = self.parse_expr()
        self._expect("COLON")
        body = self.parse_loop_body()
        init = ast.Name("none")
        if self._peek().kind == "INIT":
            self.pos += 1
            init = self.parse_expr()
        return ast.While(test, body, init)

    # expressions -------------------------------------------------------
    def parse_expr(self, min_prec: int = 0) -> ast.Node:
        left = self.parse_atom()
        precedence = {
            "==": 5,
            "!=": 5,
            ">": 5,
            "<": 5,
            ">=": 5,
            "<=": 5,
            "+": 10,
            "-": 10,
            "*": 20,
            "/": 20,
        }
        while self._peek().kind == "OP" and precedence.get(self._peek().value, 0) >= min_prec:
            op_tok = self._expect("OP")
            prec = precedence.get(op_tok.value, 0)
            right = self.parse_expr(prec + 1)
            left = ast.BinOp(left, op_tok.value, right)
        return left

    def parse_atom(self) -> ast.Node:
        tok = self._peek()
        if tok.kind == "NUMBER":
            self.pos += 1
            return ast.Number(int(tok.value))
        if tok.kind == "STRING":
            self.pos += 1
            return ast.String(tok.value[1:-1])
        if tok.kind == "IDENT":
            self.pos += 1
            node: ast.Node = ast.Name(tok.value)
        elif tok.kind == "LPAREN":
            self.pos += 1
            node = self.parse_expr()
            self._expect("RPAREN")
        elif tok.kind == "IF":
            self.pos += 1
            test = self.parse_expr()
            self._expect("COLON")
            then = self.parse_expr()
            self._expect("ELSE")
            self._expect("COLON")
            otherwise = self.parse_expr()
            node = ast.IfExpr(test, then, otherwise)
        elif tok.kind == "FN":
            node = self.parse_lambda()
        elif tok.kind in {"TRUE", "FALSE", "NONE"}:
            self.pos += 1
            node = ast.Name(tok.kind.lower())
        else:
            raise SyntaxError(f"unexpected token {tok.kind}")

        # call suffix
        while self._peek().kind == "LPAREN":
            self._expect("LPAREN")
            args: List[ast.Node] = []
            if self._peek().kind != "RPAREN":
                args.append(self.parse_expr())
                while self._peek().kind == "COMMA":
                    self.pos += 1
                    args.append(self.parse_expr())
            self._expect("RPAREN")
            node = ast.Call(node, args)
        return node

    def parse_lambda(self) -> ast.Lambda:
        self._expect("FN")
        self._expect("LPAREN")
        params: List[str] = []
        if self._peek().kind != "RPAREN":
            params.append(self._expect("IDENT").value)
            while self._peek().kind == "COMMA":
                self.pos += 1
                params.append(self._expect("IDENT").value)
        self._expect("RPAREN")
        self._expect("ARROW")
        body = self.parse_expr()
        return ast.Lambda(params, body)
