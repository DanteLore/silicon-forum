from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


class SummaryHtml:
    """Accumulates per-run results and writes a summary HTML table after each run."""

    def __init__(self, path: str, title: str = ""):
        self._path = Path(path)
        self._title = title
        self._rows: list[dict] = []
        self._template = _env.get_template("summary.html")

    def add_row(
        self,
        run_num: int,
        winner: str | None,
        scores: dict,
        transcript_filename: str,
        agent_for: str | None,
        agent_against: str | None,
        premise: str | None,
        premise_upheld: bool | None,
    ):
        self._rows.append({
            "run_num": run_num,
            "winner": winner,
            "scores": scores,
            "transcript_filename": transcript_filename,
            "agent_for": agent_for,
            "agent_against": agent_against,
            "premise": premise,
            "premise_upheld": premise_upheld,
        })
        self._flush()

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        html = self._template.render(
            title=self._title,
            rows=self._rows,
        )
        self._path.write_text(html, encoding="utf-8")
