import json
import urllib.request

OLLAMA_BASE_URL = "http://localhost:11434"


def list_models() -> list[str]:
    """Return names of models currently installed in Ollama."""
    with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags") as resp:
        data = json.loads(resp.read())
    return [m["name"] for m in data.get("models", [])]
