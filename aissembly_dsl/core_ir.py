from __future__ import annotations

import time
from .errors import Error


class LoopBreak(Exception):
    def __init__(self, value=None):
        self.value = value


class LoopContinue(Exception):
    pass


def cond(test, then, else_, trace=None):
    return then() if test() else else_()


def loop_for(iterable, body, init, max_iter=None, timeout_ms=None, trace=None):
    acc = init
    start = time.time()
    for idx, item in enumerate(iterable):
        if max_iter is not None and idx >= max_iter:
            raise Error("LimitExceeded", "max_iter", {"max_iter": max_iter})
        if timeout_ms is not None and (time.time() - start) * 1000 >= timeout_ms:
            raise Error("LimitExceeded", "timeout", {"timeout_ms": timeout_ms})
        try:
            acc = body(item, acc)
        except LoopBreak as b:
            return b.value
        except LoopContinue:
            continue
    return acc


def loop_while(test, body, init, max_iter=None, timeout_ms=None, trace=None):
    acc = init
    start = time.time()
    count = 0
    while test():
        if max_iter is not None and count >= max_iter:
            raise Error("LimitExceeded", "max_iter", {"max_iter": max_iter})
        if timeout_ms is not None and (time.time() - start) * 1000 >= timeout_ms:
            raise Error("LimitExceeded", "timeout", {"timeout_ms": timeout_ms})
        count += 1
        try:
            acc = body(acc)
        except LoopBreak as b:
            return b.value
        except LoopContinue:
            continue
    return acc


class ctrl:
    @staticmethod
    def break_(value=None):
        raise LoopBreak(value)

    @staticmethod
    def continue_():
        raise LoopContinue()


class op:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def sub(a, b):
        return a - b

    @staticmethod
    def mul(a, b):
        return a * b

    @staticmethod
    def div(a, b):
        return a / b

    @staticmethod
    def eq(a, b):
        return a == b

    @staticmethod
    def ne(a, b):
        return a != b

    @staticmethod
    def gt(a, b):
        return a > b

    @staticmethod
    def lt(a, b):
        return a < b

    @staticmethod
    def ge(a, b):
        return a >= b

    @staticmethod
    def le(a, b):
        return a <= b


ENV = {
    "cond": cond,
    "loop": {"for": loop_for, "while": loop_while},
    "op": op,
    "ctrl": ctrl,
}
