import argparse
import os
import random
from datetime import datetime

import yaml
from agents import Agent
from conversation import run_conversation
from ollama import list_models
from outputs.console import TerminalOutput
from outputs.html import HtmlOutput

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

parser = argparse.ArgumentParser(description="Run a conversation between two AI agents.")
parser.add_argument("config", nargs="?", default="debates/can_ai_think.yaml",
                    help="Path to the debate config YAML (default: debates/can_ai_think.yaml)")
parser.add_argument("--model", default=None,
                    help="Force all agents to use this Ollama model (default: random per agent)")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = yaml.safe_load(f)

_available_models: list[str] = []
if not args.model:
    _available_models = list_models()
    if not _available_models:
        print("Warning: no models found in Ollama — using model from YAML config")


def _pick(cfg_list, side=None):
    cfg = dict(random.choice(cfg_list))
    if side is not None:
        cfg["side"] = side
    if args.model:
        cfg["model"] = args.model
    elif _available_models:
        cfg["model"] = random.choice(_available_models)
    return Agent(cfg)


debater_for     = _pick(config["for"],      side="for")
debater_against = _pick(config["against"],  side="against")
audience        = _pick(config["audience"]) if "audience" in config else None

debaters = [debater_for, debater_against]
random.shuffle(debaters)

config_stem = os.path.splitext(os.path.basename(args.config))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
html_path = f"results/{config_stem}_{timestamp}.html"

outputs = [
    TerminalOutput(line_width=config.get("line_width", DEFAULT_LINE_WIDTH)),
    HtmlOutput(html_path),
]

run_conversation(
    debaters[0],
    debaters[1],
    topic=config["topic"],
    premise=config.get("premise"),
    turns=config.get("turns", DEFAULT_TURNS),
    audience=audience,
    outputs=outputs,
)

print(f"\nHTML transcript saved to {html_path}")
