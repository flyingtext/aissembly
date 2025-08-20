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

## Ollama Connect example

Ollama exposes a simple HTTP API. Start a local server with `ollama serve` or
attach to a remote instance via `ollama connect <host>:11434`. The returned
address becomes the base URL for the adapter.

```bash
ollama serve
# or
ollama connect myserver.example.com:11434
```

Configure `llm_functions.json` to point at the running service:

```json
{
  "name": "ollama_chat",
  "model": "llama3",
  "adapter": {
    "type": "http",
    "url": "http://localhost:11434/api/generate",
    "method": "POST"
  },
  "parameters": {
    "type": "object",
    "properties": {
      "prompt": {"type": "string", "description": "User prompt"}
    },
    "required": ["prompt"]
  }
}
```

The runtime will send requests to the specified URL using the HTTP adapter.
Adjust the URL if `ollama connect` reports a different host or port.

If no `adapter` field is supplied, the executor returns a debug object
containing the model name, function name and arguments.
