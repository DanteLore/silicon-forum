from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from outputs import stats as stats_mod

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


class SummaryHtml:
    """Accumulates per-run result rows and rewrites the summary HTML after each run."""

    def __init__(self, path: str, title: str = ""):
        self._path = Path(path)
        self._title = title
        self.rows: list[dict] = []
        self._template = _env.get_template("summary.html")

    def add_row(self, row: dict) -> None:
        self.rows.append(row)
        self._flush()

    def finalize(self) -> None:
        pass  # already flushed incrementally after each add_row

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        html = self._template.render(
            title=self._title,
            rows=self.rows,
            stats=stats_mod.compute(self.rows),
        )
        self._path.write_text(html, encoding="utf-8")
