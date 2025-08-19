# Aissembly

Aissembly is an experimental compiler and IDE that treats natural-language descriptions as executable functions. Instead of writing traditional syntax, developers describe computations in plain language and let a language model produce the result.

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

This repository currently contains documentation describing the vision for Aissembly. Implementation work will expand upon these files.

## License

This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

