import argparse
import os
import random
from datetime import datetime

import yaml
from engine.agent_pool import make_picker, setup_model_selection
from engine.debate import run_debate
from outputs.collector import ResultCollector
from outputs.console import TerminalOutput
from outputs.csv_export import SummaryCsv
from outputs.html import HtmlOutput
from outputs.summary import SummaryHtml
from outputs.terminal_stats import TerminalStats

DEFAULT_TURNS = 6
DEFAULT_LINE_WIDTH = 80


def parse_args():
    parser = argparse.ArgumentParser(description="Run multiple debates and collect results.")
    parser.add_argument("config", help="Path to the debate config YAML")
    parser.add_argument("count", type=int, nargs="?", default=5,
                        help="Number of debate runs (default: 5)")
    parser.add_argument("--model", default=None,
                        help="Force all agents to use this Ollama model (default: random per agent)")
    return parser.parse_args()


def run_one(run_num: int, total: int, config: dict, run_dir: str, config_stem: str, pick) -> dict:
    """Run a single debate and return the result row dict."""
    print(f"\n{'=' * 60}")
    print(f"  RUN {run_num} of {total}")
    print(f"{'=' * 60}\n")

    debater_for     = pick(config["for"],      side="for")
    debater_against = pick(config["against"],  side="against")
    judge           = pick(config["audience"]) if "audience" in config else None

    debaters = [debater_for, debater_against]
    random.shuffle(debaters)
    first_speaker = debaters[0].name

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"{run_dir}/{config_stem}_{run_timestamp}.html"

    collector = ResultCollector()
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
            collector,
        ],
    )

    print(f"\nTranscript: {html_path}")

    return {
        "run_num":             run_num,
        "winner":              collector.winner,
        "scores":              collector.scores,
        "transcript_filename": os.path.basename(html_path),
        "agent_for":           debater_for.name,
        "agent_against":       debater_against.name,
        "judge":               collector.judge,
        "premise":             collector.premise,
        "premise_upheld":      collector.premise_upheld,
        "first_speaker":       first_speaker,
        "model_for":           debater_for.model,
        "model_against":       debater_against.model,
        "model_judge":         judge.model if judge else None,
    }


def main():
    args = parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    available_models = setup_model_selection(args.model)
    pick = make_picker(args.model, available_models)

    config_stem = os.path.splitext(os.path.basename(args.config))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"results/{config_stem}_{timestamp}"
    summary_path = f"{run_dir}/summary.html"
    csv_path = f"{run_dir}/results.csv"

    if args.model:
        print(f"Running {args.count} debate(s) from {args.config}  [model: {args.model}]")
    elif available_models:
        print(f"Running {args.count} debate(s) from {args.config}  "
              f"[random model from {len(available_models)} installed]")
    else:
        print(f"Running {args.count} debate(s) from {args.config}")
    print(f"Output:  {run_dir}/\n")

    stats_outputs = [
        SummaryHtml(summary_path, title=config.get("premise", config.get("topic", config_stem))),
        SummaryCsv(csv_path),
        TerminalStats(),
    ]

    for run_num in range(1, args.count + 1):
        try:
            row = run_one(run_num, args.count, config, run_dir, config_stem, pick)
        except Exception as e:
            print(f"\n[Run {run_num} failed: {e}] Skipping.\n")
            continue
        for out in stats_outputs:
            out.add_row(row)

    print(f"\nAll done! Output: {run_dir}/")

    for out in stats_outputs:
        out.finalize()


if __name__ == "__main__":
    main()
