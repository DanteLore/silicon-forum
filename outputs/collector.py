from events import DebateEvent, EventType


class ResultCollector:
    """Lightweight output strategy that captures structured result data."""

    def __init__(self):
        self.winner: str | None = None
        self.scores: dict = {}
        self.premise: str | None = None
        self.premise_upheld: bool | None = None
        self.sides: dict = {}

    def __call__(self, event: DebateEvent):
        if event.type == EventType.HEADER:
            self.sides = event.metadata.get("sides", {})
            self.premise = event.metadata.get("premise")
        elif event.type == EventType.VERDICT:
            self.winner = event.metadata.get("winner")
            self.scores = event.metadata.get("scores", {})
            self.premise_upheld = event.metadata.get("premise_upheld")
