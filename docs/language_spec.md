# Aissembly Language Specification

This document summarizes the basic literal forms supported by the Aissembly language. Aissembly mirrors Python's syntax for these core data types to keep the language approachable.

## Numeric Literals

- **Integers** use the same notation as Python: `42`, `-7`, `0`.
- **Floating point numbers** follow Python's syntax: `3.14`, `1e6`, `-0.5`.

## Strings

Strings are enclosed in single or double quotes, matching Python's rules. Escape sequences like `"\n"` operate the same way.

Example: `"hello"`, `'world'`.

## Lists

Lists use square brackets with comma-separated items:

```asl
[1, 2, 3]
```

## Dictionaries

Dictionaries use curly braces with colon-separated key/value pairs:

```asl
{"mode": "dev", "limit": 5}
```

## Example Program

See [examples/basic_types.asl](../examples/basic_types.asl) for a full program demonstrating these literal forms.
