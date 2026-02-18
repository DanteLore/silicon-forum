import html as _html
from pathlib import Path
from events import DebateEvent, EventType

# Maps colorama-style color names to CSS values
_CSS_COLOR = {
    "cyan":    "#26c6da",
    "yellow":  "#fdd835",
    "magenta": "#e040fb",
    "green":   "#66bb6a",
    "red":     "#ef5350",
    "blue":    "#42a5f5",
    "white":   "#e0e0e0",
    "black":   "#212121",
}

_STYLESHEET = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: #12121e;
    color: #ddd;
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.75;
    padding: 2.5rem 1.5rem;
}

.debate {
    max-width: 820px;
    margin: 0 auto;
}

/* ── Header ─────────────────────────────────────────── */
.debate-header {
    border-bottom: 1px solid #333;
    padding-bottom: 1.75rem;
    margin-bottom: 2rem;
}

.debate-header h1 {
    font-size: 1.7rem;
    font-weight: normal;
    color: #fff;
    margin-bottom: 1.25rem;
    letter-spacing: 0.02em;
}

.participants {
    display: flex;
    gap: 1.25rem;
    flex-wrap: wrap;
}

.participant {
    border-left: 3px solid;
    padding: 0.4rem 0.9rem;
    flex: 1;
    min-width: 220px;
}

.participant-name {
    display: block;
    font-weight: bold;
    font-size: 1rem;
    margin-bottom: 0.25rem;
}

.participant-bio {
    font-size: 0.85rem;
    opacity: 0.65;
    font-style: italic;
}

/* ── Transcript ──────────────────────────────────────── */
.transcript {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* ── Collapsible thoughts ────────────────────────────── */
details.thought {
    background: #1a1a2a;
    border-radius: 4px;
    padding: 0.45rem 1rem;
    opacity: 0.6;
}

details.thought summary {
    cursor: pointer;
    font-size: 0.82rem;
    font-style: italic;
    list-style: none;
    user-select: none;
}

details.thought summary::-webkit-details-marker { display: none; }
details.thought summary::before { content: "▶  "; font-size: 0.65rem; }
details[open].thought summary::before { content: "▼  "; }

.thought-body {
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid #2a2a3a;
    font-size: 0.84rem;
    white-space: pre-wrap;
    opacity: 0.85;
}

/* ── Debate turns ────────────────────────────────────── */
.turn {
    background: #1c1c30;
    border-radius: 6px;
    padding: 1.1rem 1.4rem;
}

.turn-speaker {
    font-weight: bold;
    font-size: 0.82rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.turn-speech p { margin-bottom: 0.65rem; }
.turn-speech p:last-child { margin-bottom: 0; }

/* ── Scores ──────────────────────────────────────────── */
.score {
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
    flex-wrap: wrap;
    background: #111120;
    border-radius: 4px;
    padding: 0.45rem 1rem;
    font-size: 0.84rem;
}

.score-judge { font-weight: bold; }
.score-sep { opacity: 0.4; }
.score-target { font-weight: bold; }
.score-text { opacity: 0.82; flex: 1; }

/* ── Verdict ─────────────────────────────────────────── */
.verdict {
    margin-top: 2.5rem;
    border-top: 1px solid #333;
    padding-top: 1.75rem;
}

.verdict h2 {
    font-size: 1.3rem;
    font-weight: normal;
    margin-bottom: 1rem;
    letter-spacing: 0.03em;
}

.verdict-body p { margin-bottom: 0.65rem; }
.verdict-body p:last-child { margin-bottom: 0; }
"""


def _e(text: str) -> str:
    """HTML-escape a string."""
    return _html.escape(text)


def _paragraphs(text: str) -> str:
    """Convert newline-separated text into <p> tags."""
    parts = [" ".join(block.split()) for block in text.strip().split("\n\n") if block.strip()]
    return "".join(f"<p>{_e(p)}</p>" for p in parts)


def _css(color_name: str) -> str:
    return _CSS_COLOR.get(color_name.lower(), "#e0e0e0")


class HtmlOutput:
    def __init__(self, path: str):
        self._path = Path(path)
        self._topic = ""
        self._participants: list[str] = []
        self._colors: dict[str, str] = {}   # name -> CSS color
        self._header_html = ""
        self._transcript: list[str] = []
        self._verdict_html = ""

    def __call__(self, event: DebateEvent):
        color = _css(event.color)

        if event.type == EventType.HEADER:
            self._topic = event.metadata["topic"]
            self._participants = event.metadata["participants"]
            self._colors = {
                name: _css(col)
                for name, col in event.metadata["colors"].items()
            }
            self._header_html = self._build_header(event)

        elif event.type == EventType.PLAN:
            self._transcript.append(
                self._collapsible(event.speaker, "opening plan", event.content, color)
            )

        elif event.type == EventType.THINK:
            self._transcript.append(
                self._collapsible(event.speaker, "thinks", event.content, color)
            )

        elif event.type == EventType.TURN:
            self._transcript.append(self._turn(event.speaker, event.content, color))

        elif event.type == EventType.SCORE:
            target = event.metadata["target"]
            self._transcript.append(
                self._score(event.speaker, target, event.content, color)
            )

        elif event.type == EventType.VERDICT:
            self._verdict_html = self._verdict(event.speaker, event.content, color)

        self._flush()

    # ── Renderers ────────────────────────────────────────────────────────────

    def _build_header(self, event: DebateEvent) -> str:
        personalities = event.metadata.get("personalities", {})
        cards = ""
        for name in self._participants:
            c = self._colors.get(name, "#e0e0e0")
            bio = personalities.get(name, "")
            bio_html = f'<span class="participant-bio">{_e(bio)}</span>' if bio else ""
            cards += (
                f'<div class="participant" style="border-color:{c}">'
                f'<span class="participant-name" style="color:{c}">{_e(name)}</span>'
                f'{bio_html}'
                f'</div>'
            )
        return (
            f'<header class="debate-header">'
            f'<h1>{_e(self._topic)}</h1>'
            f'<div class="participants">{cards}</div>'
            f'</header>'
        )

    def _collapsible(self, speaker: str, label: str, content: str, color: str) -> str:
        return (
            f'<details class="thought">'
            f'<summary><span style="color:{color}">{_e(speaker)}</span> — {_e(label)}</summary>'
            f'<div class="thought-body">{_e(content.strip())}</div>'
            f'</details>'
        )

    def _turn(self, speaker: str, content: str, color: str) -> str:
        return (
            f'<div class="turn">'
            f'<div class="turn-speaker" style="color:{color}">{_e(speaker)}</div>'
            f'<div class="turn-speech">{_paragraphs(content)}</div>'
            f'</div>'
        )

    def _score(self, judge: str, target: str, content: str, judge_color: str) -> str:
        target_color = self._colors.get(target, "#e0e0e0")
        return (
            f'<div class="score">'
            f'<span class="score-judge" style="color:{judge_color}">{_e(judge)}</span>'
            f'<span class="score-sep">→</span>'
            f'<span class="score-target" style="color:{target_color}">{_e(target)}</span>'
            f'<span class="score-text">{_e(" ".join(content.split()))}</span>'
            f'</div>'
        )

    def _verdict(self, judge: str, content: str, color: str) -> str:
        return (
            f'<div class="verdict">'
            f'<h2>Final Verdict — <span style="color:{color}">{_e(judge)}</span></h2>'
            f'<div class="verdict-body">{_paragraphs(content)}</div>'
            f'</div>'
        )

    # ── File output ──────────────────────────────────────────────────────────

    def _flush(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(self._document(), encoding="utf-8")

    def _document(self) -> str:
        transcript = "\n".join(self._transcript)
        return (
            f'<!DOCTYPE html>\n'
            f'<html lang="en">\n'
            f'<head>\n'
            f'<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>Debate: {_e(self._topic)}</title>\n'
            f'<style>{_STYLESHEET}</style>\n'
            f'</head>\n'
            f'<body>\n'
            f'<div class="debate">\n'
            f'{self._header_html}\n'
            f'<div class="transcript">\n{transcript}\n</div>\n'
            f'{self._verdict_html}\n'
            f'</div>\n'
            f'</body>\n'
            f'</html>\n'
        )
