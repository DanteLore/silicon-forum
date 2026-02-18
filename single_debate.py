import argparse
import os
import random
from datetime import datetime

import yaml
from engine.agent_pool import make_picker, setup_model_selection
from engine.debate import run_debate
from outputs.console import TerminalOutput
from outputs.html import HtmlOutput

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

parser = argparse.ArgumentParser(description="Run a single debate between two AI agents.")
parser.add_argument("config", nargs="?", default="debates/can_ai_think.yaml",
                    help="Path to the debate config YAML (default: debates/can_ai_think.yaml)")
parser.add_argument("--model", default=None,
                    help="Force all agents to use this Ollama model (default: random per agent)")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = yaml.safe_load(f)

_available_models = setup_model_selection(args.model)
_pick = make_picker(args.model, _available_models)

debater_for     = _pick(config["for"],      side="for")
debater_against = _pick(config["against"],  side="against")
judge           = _pick(config["audience"]) if "audience" in config else None

debaters = [debater_for, debater_against]
random.shuffle(debaters)

config_stem = os.path.splitext(os.path.basename(args.config))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
html_path = f"results/{config_stem}_{timestamp}.html"

run_debate(
    debaters[0],
    debaters[1],
    topic=config["topic"],
    premise=config.get("premise"),
    turns=config.get("turns", DEFAULT_TURNS),
    judge=judge,
    outputs=[
        TerminalOutput(line_width=config.get("line_width", DEFAULT_LINE_WIDTH)),
        HtmlOutput(html_path),
    ],
)

print(f"\nHTML transcript saved to {html_path}")
