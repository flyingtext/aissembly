"""Standard operation stubs.

The real implementation lives in :mod:`core_ir`.  This module merely exposes
names so that they can be referenced from the evaluated programs."""

from .core_ir import op, ctrl, loop_for, loop_while

class loop:
    for_ = loop_for
    while_ = loop_while

# Stubs for optional modules
class str:
    @staticmethod
    def concat(a, b):
        return a + b


class json:
    @staticmethod
    def dumps(value):  # pragma: no cover - placeholder
        return "{}"


class time:
    @staticmethod
    def now():  # pragma: no cover - placeholder
        return 0
