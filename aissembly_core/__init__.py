"""Core parser and executor for Aissembly minimal language."""
from .parser import parse_program
from .executor import Executor, load_llm_defs

__all__ = ["parse_program", "Executor", "load_llm_defs"]
