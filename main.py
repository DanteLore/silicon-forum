import yaml
from agents import Agent
from conversation import run_conversation

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

with open("config/can_ai_think.yaml", "r") as f:
    config = yaml.safe_load(f)

agents = [Agent(a) for a in config["agents"]]

run_conversation(
    agents[0],
    agents[1],
    topic=config["topic"],
    turns=config.get("turns", DEFAULT_TURNS),
    line_width=config.get("line_width", DEFAULT_LINE_WIDTH),
)
