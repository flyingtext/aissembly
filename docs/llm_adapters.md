# LLM Adapters

`llm_functions.json` entries can include an `adapter` field that describes how the
runtime should route a call to a language model. Adapters allow Aissembly to
connect to local scripts or remote HTTP services.

## Python file adapter

```json
{
  "name": "local_add",
  "model": "local",
  "adapter": {
    "type": "python",
    "path": "path/to/adapter.py",
    "function": "add_adapter"
  }
}
```

The runtime loads the module at `path` and invokes the specified `function`
with the positional and keyword arguments from the Aissembly program. This
method can wrap Python, Julia, Go, or any language that exposes a Python
callable.

## HTTP adapter

```json
{
  "name": "summarization",
  "model": "gpt-4o-mini",
  "adapter": {
    "type": "http",
    "url": "https://api.openai.com/v1/chat/completions",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer <token>"
    }
  }
}
```

For HTTP adapters the runtime sends a JSON payload containing the function
name, model and arguments. The JSON response body is returned as the result
of the call. This mechanism can interface with providers such as Ollama,
OpenAI, Claude or any custom service.

If no `adapter` field is supplied, the executor returns a debug object
containing the model name, function name and arguments.
