import argparse
import yaml
from agents import Agent
from conversation import run_conversation

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

parser = argparse.ArgumentParser(description="Run a conversation between two AI agents.")
parser.add_argument("config", nargs="?", default="config/can_ai_think.yaml",
                    help="Path to the conversation config YAML (default: config/can_ai_think.yaml)")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = yaml.safe_load(f)

agents = [Agent(a) for a in config["agents"]]

run_conversation(
    agents[0],
    agents[1],
    topic=config["topic"],
    turns=config.get("turns", DEFAULT_TURNS),
    line_width=config.get("line_width", DEFAULT_LINE_WIDTH),
)
