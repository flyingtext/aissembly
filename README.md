# Aissembly

Aissembly is an experimental compiler and IDE that treats natural-language descriptions as executable functions. Instead of writing traditional syntax, developers describe computations in plain language and let a language model produce the result. **Philosophy of Aissembly is "Art of Aissembly is about making LLM and parser do all the craps."**

## Core Concepts

Aissembly focuses on three high-level constructs:

1. **연산 함수 (Operation functions)** – Each function expresses a single operation in natural language:

   ```python
   def 함수(param1, param2):
       return llm_query(f"{param1}을 가지고 {param2}를 통해 연산 결과값을 도출한다.")
   ```

2. **반복문 함수 (Loop functions)** – Natural-language loops repeatedly invoke operation functions over collections.

3. **조건문 함수 (Conditional functions)** – Human-readable conditions branch execution paths.

Every construct is modularized so that individual natural-language functions can be composed into larger programs.

## Goals

- Provide an IDE that assists with authoring and debugging natural-language code.
- Deliver an extensible compiler pipeline that translates natural-language descriptions into executable operations via LLMs.
- Optimize for clarity and rapid prototyping rather than low-level performance.

## Project Structure

Top-level directories and key files:

- `aissembly_core/` – prototype parser and runtime for the minimal Aissembly language.
- `docs/` – design and reference material (see [Documentation](#documentation)).
- `examples/` – sample Aissembly programs.
- `tests/` – automated tests for the language and runtime.
- `llm_functions.json` – example LLM function and adapter configuration.
- `todo.md` – status of implemented vs pending language features.

## Documentation

The `docs/` directory contains design notes and reference material:

- `PHILOSOPHY.md` – guiding principles behind Aissembly.
- `architecture.md` – overview of the system architecture that turns natural language into executable behavior.
- `language_spec.md` – working draft of the core language specification for implementers.
- `llm_adapters.md` – describes how to configure adapters that route calls to local scripts or HTTP services.
- `parser.md` – details the minimal parser and execution engine with examples.

## Prototype Parser

An initial parser and execution engine for the minimal Aissembly language is
available in the `aissembly_core` package.  The parser incrementally reparses
source code line by line, making it suitable for interactive editing or LLM
streaming. Parse and run programs with:

```bash
python -m aissembly_core.runtime path/to/program.asl --llm llm_functions.json
```

LLM function specifications can define adapters for local scripts or HTTP APIs.
See [docs/llm_adapters.md](docs/llm_adapters.md) for the configuration format.

Unit tests demonstrate language features and can be executed via:

```bash
pytest
```

## License

This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

