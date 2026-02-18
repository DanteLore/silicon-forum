import argparse
import os
import random
from datetime import datetime

import yaml
from agents import Agent
from conversation import run_conversation
from outputs.collector import ResultCollector
from outputs.console import TerminalOutput
from outputs.html import HtmlOutput
from outputs.summary import SummaryHtml

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80

parser = argparse.ArgumentParser(description="Run multiple debates and collect results.")
parser.add_argument("config", help="Path to the debate config YAML")
parser.add_argument("count", type=int, nargs="?", default=5,
                    help="Number of debate runs (default: 5)")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = yaml.safe_load(f)

config_stem = os.path.splitext(os.path.basename(args.config))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
summary_path = f"results/{config_stem}_summary_{timestamp}.html"
summary = SummaryHtml(summary_path, title=config.get("topic", config_stem))

print(f"Running {args.count} debate(s) from {args.config}")
print(f"Summary: {summary_path}\n")

for run_num in range(1, args.count + 1):
    print(f"\n{'=' * 60}")
    print(f"  RUN {run_num} of {args.count}")
    print(f"{'=' * 60}\n")

    agents = [Agent(a) for a in config["agents"]]
    random.shuffle(agents)
    audience = Agent(config["audience"]) if "audience" in config else None

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"results/{config_stem}_{run_timestamp}.html"

    collector = ResultCollector()
    outputs = [
        TerminalOutput(line_width=config.get("line_width", DEFAULT_LINE_WIDTH)),
        HtmlOutput(html_path),
        collector,
    ]

    run_conversation(
        agents[0],
        agents[1],
        topic=config["topic"],
        premise=config.get("premise"),
        turns=config.get("turns", DEFAULT_TURNS),
        audience=audience,
        outputs=outputs,
    )

    agent_for = next((a.name for a in agents if a.side == "for"), None)
    agent_against = next((a.name for a in agents if a.side == "against"), None)

    # transcript_filename is relative — both files live in results/
    transcript_filename = os.path.basename(html_path)

    summary.add_row(
        run_num=run_num,
        winner=collector.winner,
        scores=collector.scores,
        transcript_filename=transcript_filename,
        agent_for=agent_for,
        agent_against=agent_against,
        premise=collector.premise,
        premise_upheld=collector.premise_upheld,
    )

    print(f"\nTranscript: {html_path}")

print(f"\nAll done! Summary: {summary_path}")
