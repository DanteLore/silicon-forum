from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from outputs import stats as stats_mod

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
        self.rows: list[dict] = []
        self._template = _env.get_template("summary.html")

    def add_row(
        self,
        run_num: int,
        winner: str | None,
        scores: dict,
        transcript_filename: str,
        agent_for: str | None,
        agent_against: str | None,
        judge: str | None,
        premise: str | None,
        premise_upheld: bool | None,
        first_speaker: str | None = None,
        model_for: str | None = None,
        model_against: str | None = None,
        model_judge: str | None = None,
    ):
        self.rows.append({
            "run_num":             run_num,
            "winner":              winner,
            "scores":              scores,
            "transcript_filename": transcript_filename,
            "agent_for":           agent_for,
            "agent_against":       agent_against,
            "judge":               judge,
            "premise":             premise,
            "premise_upheld":      premise_upheld,
            "first_speaker":       first_speaker,
            "model_for":           model_for,
            "model_against":       model_against,
            "model_judge":         model_judge,
        })
        self._flush()

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        html = self._template.render(
            title=self._title,
            rows=self.rows,
            stats=stats_mod.compute(self.rows),
        )
        self._path.write_text(html, encoding="utf-8")
