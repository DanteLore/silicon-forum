import argparse
import os
import random
from datetime import datetime

import yaml
from agents import Agent
from conversation import run_conversation
from outputs.console import TerminalOutput
from outputs.html import HtmlOutput

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

parser = argparse.ArgumentParser(description="Run a conversation between two AI agents.")
parser.add_argument("config", nargs="?", default="debates/can_ai_think.yaml",
                    help="Path to the debate config YAML (default: debates/can_ai_think.yaml)")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = yaml.safe_load(f)

agents = [Agent(a) for a in config["agents"]]
random.shuffle(agents)
audience = Agent(config["audience"]) if "audience" in config else None

config_stem = os.path.splitext(os.path.basename(args.config))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
html_path = f"results/{config_stem}_{timestamp}.html"

outputs = [
    TerminalOutput(line_width=config.get("line_width", DEFAULT_LINE_WIDTH)),
    HtmlOutput(html_path),
]

run_conversation(
    agents[0],
    agents[1],
    topic=config["topic"],
    turns=config.get("turns", DEFAULT_TURNS),
    audience=audience,
    outputs=outputs,
)

print(f"\nHTML transcript saved to {html_path}")
