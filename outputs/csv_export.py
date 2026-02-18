import csv
from pathlib import Path

_FIELDS = [
    "run_num",
    "agent_for",
    "model_for",
    "agent_against",
    "model_against",
    "judge",
    "model_judge",
    "first_speaker",
    "premise",
    "premise_upheld",
    "winner",
    "winner_side",
    "score_for",
    "score_against",
    "transcript_filename",
]


def _flatten(row: dict) -> dict:
    agent_for     = row.get("agent_for") or ""
    agent_against = row.get("agent_against") or ""
    winner        = row.get("winner") or ""
    scores        = row.get("scores", {})
    upheld        = row.get("premise_upheld")

    if winner == agent_for:
        winner_side = "for"
    elif winner == agent_against:
        winner_side = "against"
    else:
        winner_side = ""

    return {
        "run_num":            row.get("run_num", ""),
        "agent_for":          agent_for,
        "model_for":          row.get("model_for") or "",
        "agent_against":      agent_against,
        "model_against":      row.get("model_against") or "",
        "judge":              row.get("judge") or "",
        "model_judge":        row.get("model_judge") or "",
        "first_speaker":      row.get("first_speaker") or "",
        "premise":            row.get("premise") or "",
        "premise_upheld":     "" if upheld is None else ("TRUE" if upheld else "FALSE"),
        "winner":             winner,
        "winner_side":        winner_side,
        "score_for":          scores.get(agent_for, ""),
        "score_against":      scores.get(agent_against, ""),
        "transcript_filename": row.get("transcript_filename") or "",
    }


class SummaryCsv:
    """Accumulates per-run result rows and rewrites the CSV after each run."""

    def __init__(self, path: str):
        self._path = Path(path)
        self.rows: list[dict] = []

    def add_row(self, row: dict) -> None:
        self.rows.append(row)
        self._flush()

    def finalize(self) -> None:
        pass  # already flushed incrementally after each add_row

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDS)
            writer.writeheader()
            for row in self.rows:
                writer.writerow(_flatten(row))
