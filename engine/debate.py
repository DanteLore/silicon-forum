from .agents import Agent
from .events import DebateEvent, EventType


class Debate:
    """Orchestrates a single debate between two agents with an optional judge."""

    def __init__(
        self,
        agent_a: Agent,
        agent_b: Agent,
        topic: str,
        premise: str = None,
        turns: int = 6,
        judge: Agent = None,
        outputs: list = None,
    ):
        self._agent_a = agent_a
        self._agent_b = agent_b
        self._topic = topic
        self._premise = premise
        self._turns = turns
        self._judge = judge
        self._outputs = outputs or []

        self._color_map = {a.name: a.color for a in [agent_a, agent_b]}
        if judge:
            self._color_map[judge.name] = judge.color

        self._sides = {a.name: a.side for a in [agent_a, agent_b] if a.side}
        self._scored: set = set()

    # ── Event dispatch ──────────────────────────────────────────────────────

    def _emit(self, event_type, speaker="", content="", **meta):
        event = DebateEvent(
            type=event_type,
            speaker=speaker,
            content=content,
            color=self._color_map.get(speaker, "white"),
            metadata=meta,
        )
        for out in self._outputs:
            out(event)

    # ── Debate phases ────────────────────────────────────────────────────────

    def _emit_header(self):
        self._emit(
            EventType.HEADER,
            topic=self._topic,
            premise=self._premise,
            sides=self._sides,
            participants=[self._agent_a.name, self._agent_b.name],
            colors=self._color_map,
            personalities={a.name: a.personality for a in [self._agent_a, self._agent_b]},
            models={a.name: a.model for a in [self._agent_a, self._agent_b]},
            judge={
                "name":             self._judge.name,
                "color":            self._judge.color,
                "personality":      self._judge.personality,
                "judging_criteria": self._judge.judging_criteria,
                "model":            self._judge.model,
            } if self._judge else None,
        )

    def _planning_phase(self):
        for agent in (self._agent_a, self._agent_b):
            self._emit(EventType.PLAN, agent.name, agent.plan(self._topic))

    def _opening_statement(self) -> str:
        self._emit(EventType.THINK, self._agent_a.name,
                   self._agent_a.think_opening(
                       self._topic,
                       premise=self._premise,
                       side=self._agent_a.side,
                       opponent_name=self._agent_b.name,
                   ))
        side_line = ""
        if self._agent_a.side and self._premise:
            label = "FOR" if self._agent_a.side == "for" else "AGAINST"
            side_line = f"You are arguing {label} the premise: \"{self._premise}\"\n\n"
        opening = (
            f"The debate topic is: {self._topic}\n\n"
            f"{side_line}"
            f"Your opponent is {self._agent_b.name}. "
            f"Deliver your opening argument now, in your own voice. "
            f"Speak directly and make your case. "
            f"Do not write stage directions, do not write your opponent's lines, "
            f"and do not present both sides — give only your own argument."
        )
        message = self._agent_a.chat(opening)
        self._emit(EventType.TURN, self._agent_a.name, message)
        return message

    def _judge_turn(self, speaker_name: str, statement: str):
        self._emit(EventType.THINK, self._judge.name,
                   self._judge.evaluate(speaker_name, statement))
        result = self._judge.score(speaker_name, first=speaker_name not in self._scored)
        self._scored.add(speaker_name)
        self._emit(EventType.SCORE, self._judge.name, result.get("reasoning", ""),
                   target=speaker_name, score=result.get("score"))

    def _turn_loop(self, opening_message: str):
        message = opening_message
        speaker, listener = self._agent_b, self._agent_a
        remaining = self._turns - 1
        for i in range(remaining):
            final = (i >= remaining - 2)  # last two turns: each debater's final go
            self._emit(EventType.THINK, speaker.name, speaker.think(message, final=final))
            message = speaker.respond(final=final)
            self._emit(EventType.TURN, speaker.name, message)
            if self._judge:
                self._judge_turn(speaker.name, message)
            speaker, listener = listener, speaker

    def _verdict_phase(self):
        result = self._judge.verdict(
            [self._agent_a.name, self._agent_b.name],
            premise=self._premise,
            sides=self._sides,
        )
        winner = result.get("winner")
        premise_upheld = None
        if self._premise and winner and self._sides:
            winner_side = self._sides.get(winner)
            if winner_side:
                premise_upheld = (winner_side == "for")

        if result.get("deliberation"):
            self._emit(EventType.THINK, self._judge.name, result["deliberation"])

        self._emit(
            EventType.VERDICT,
            self._judge.name,
            result.get("reasoning", ""),
            winner=winner,
            scores=result.get("scores", {}),
            premise=self._premise,
            premise_upheld=premise_upheld,
        )

    # ── Entry point ──────────────────────────────────────────────────────────

    def run(self):
        self._emit_header()
        self._planning_phase()
        opening_message = self._opening_statement()
        if self._judge:
            self._judge_turn(self._agent_a.name, opening_message)
        self._turn_loop(opening_message)
        if self._judge:
            self._verdict_phase()


def run_debate(
    agent_a: Agent,
    agent_b: Agent,
    topic: str,
    premise: str = None,
    turns: int = 6,
    judge: Agent = None,
    outputs: list = None,
):
    Debate(agent_a, agent_b, topic, premise, turns, judge, outputs).run()
