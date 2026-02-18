from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

from events import DebateEvent, EventType

# Colorama color names mapped to values that read well on a white background
_CSS_COLOR = {
    "cyan":    "#00838f",
    "yellow":  "#e65100",
    "magenta": "#8e24aa",
    "green":   "#2e7d32",
    "red":     "#c62828",
    "blue":    "#1565c0",
    "white":   "#757575",
    "black":   "#222222",
}

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


def _paragraphs_filter(text: str) -> Markup:
    """Split on double newlines and wrap each paragraph in <p> tags."""
    parts = [" ".join(block.split()) for block in text.strip().split("\n\n") if block.strip()]
    return Markup("".join(f"<p>{escape(p)}</p>" for p in parts))


def _wordwrap_collapse_filter(text: str) -> str:
    """Collapse internal whitespace to a single space."""
    return " ".join(text.split())


_env.filters["paragraphs"] = _paragraphs_filter
_env.filters["wordwrap_collapse"] = _wordwrap_collapse_filter


def _css(color_name: str) -> str:
    return _CSS_COLOR.get(color_name.lower(), "#666666")


class HtmlOutput:
    def __init__(self, path: str):
        self._path = Path(path)
        self._topic = ""
        self._participants: list[dict] = []   # {name, color, bio}
        self._colors: dict[str, str] = {}     # name -> CSS color
        self._events: list[dict] = []
        self._verdict: dict | None = None
        self._template = _env.get_template("debate.html")

    def __call__(self, event: DebateEvent):
        color = _css(event.color)

        if event.type == EventType.HEADER:
            self._topic = event.metadata["topic"]
            self._colors = {
                name: _css(col)
                for name, col in event.metadata["colors"].items()
            }
            personalities = event.metadata.get("personalities", {})
            self._participants = [
                {
                    "name": name,
                    "color": self._colors.get(name, "#666"),
                    "bio": personalities.get(name, ""),
                }
                for name in event.metadata["participants"]
            ]

        elif event.type == EventType.PLAN:
            self._events.append({"type": "plan", "speaker": event.speaker,
                                  "color": color, "content": event.content})

        elif event.type == EventType.THINK:
            self._events.append({"type": "think", "speaker": event.speaker,
                                  "color": color, "content": event.content})

        elif event.type == EventType.TURN:
            self._events.append({"type": "turn", "speaker": event.speaker,
                                  "color": color, "content": event.content})

        elif event.type == EventType.SCORE:
            target = event.metadata["target"]
            self._events.append({
                "type": "score",
                "speaker": event.speaker,
                "color": color,
                "content": event.content,
                "target": target,
                "target_color": self._colors.get(target, "#666"),
            })

        elif event.type == EventType.VERDICT:
            self._verdict = {"judge": event.speaker, "color": color,
                             "content": event.content}

        self._flush()

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        html = self._template.render(
            topic=self._topic,
            participants=self._participants,
            events=self._events,
            verdict=self._verdict,
        )
        self._path.write_text(html, encoding="utf-8")
