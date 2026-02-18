import random

from .agents import Agent
from .ollama import list_models

DEFAULT_MODEL = "llama3.1:8b"


def setup_model_selection(fixed_model: str | None) -> list[str]:
    """Query Ollama for available models unless a fixed model is specified.

    Returns the list of available model names (empty when a fixed model is given).
    Prints a warning if Ollama returns no models and no fixed model was given.
    """
    if fixed_model:
        return []
    available = list_models()
    if not available:
        print(f"Warning: no models found in Ollama — falling back to {DEFAULT_MODEL}")
    return available


def make_picker(fixed_model: str | None, available_models: list[str]):
    """Return a _pick(cfg_list, side=None) -> Agent closure.

    Each call picks a random persona from cfg_list and assigns a model:
    the fixed model (--model flag), a random choice from available Ollama
    models, or DEFAULT_MODEL as a last resort.
    """
    def _pick(cfg_list: list[dict], side: str | None = None) -> Agent:
        cfg = dict(random.choice(cfg_list))
        if side is not None:
            cfg["side"] = side
        if fixed_model:
            cfg["model"] = fixed_model
        elif available_models:
            cfg["model"] = random.choice(available_models)
        else:
            cfg["model"] = DEFAULT_MODEL
        return Agent(cfg)
    return _pick
