# Aissembly Architecture

Aissembly builds software from natural-language descriptions. The system is divided into layers that convert human intent into executable behavior.

## 1. Function Layer

Natural-language **operation functions** serve as the atomic unit. Each function is a Python wrapper around a language-model query:

```python
def 함수(param1, param2):
    return llm_query(f"{param1}을 가지고 {param2}를 통해 연산 결과값을 도출한다.")
```

- Parameters describe inputs in plain language.
- The LLM interprets the instruction and returns an output.

## 2. Control-Flow Layer

- **반복문 함수 (Loops)** iterate over datasets, repeatedly invoking operation functions.
- **조건문 함수 (Conditionals)** evaluate natural-language predicates and choose which functions to execute.

These constructs allow developers to assemble complex logic without leaving natural language.

## 3. Compiler Pipeline

1. **Parsing** – Tokenizes natural-language descriptions and identifies operations, loops, and conditions.
2. **Optimization** – Organizes functions into modules for reuse and minimizes repeated queries to the LLM.
3. **Execution** – Sends prompts to the model and captures the outputs as program results.

## 4. IDE Integration

The IDE provides:

- Syntax highlighting for natural-language constructs.
- Inline previews of LLM responses.
- Debug tools for inspecting prompts and outputs.

## Future Work

- Implement a runtime for deterministic execution where possible.
- Support additional languages and domains.
- Develop caching and safety features for LLM interactions.

