from agents import Agent
from events import DebateEvent, EventType


def run_conversation(
    agent_a: Agent,
    agent_b: Agent,
    topic: str,
    premise: str = None,
    turns: int = 6,
    audience: Agent = None,
    outputs: list = None,
):
    outputs = outputs or []

    color_map = {a.name: a.color for a in [agent_a, agent_b]}
    if audience:
        color_map[audience.name] = audience.color

    sides = {a.name: a.side for a in [agent_a, agent_b] if a.side}

    def emit(type, speaker="", content="", **meta):
        event = DebateEvent(
            type=type,
            speaker=speaker,
            content=content,
            color=color_map.get(speaker, "white"),
            metadata=meta,
        )
        for out in outputs:
            out(event)

    emit(EventType.HEADER, topic=topic, premise=premise, sides=sides,
         participants=[agent_a.name, agent_b.name],
         colors=color_map,
         personalities={a.name: a.personality for a in [agent_a, agent_b]},
         judge={
             "name": audience.name,
             "color": audience.color,
             "personality": audience.personality,
             "judging_criteria": audience.judging_criteria,
         } if audience else None)

    for agent in (agent_a, agent_b):
        emit(EventType.PLAN, agent.name, agent.plan(topic))

    opening = (
        f"Let's debate the following topic: {topic}\n\n"
        f"You're speaking with {agent_b.name}. Please open the discussion."
    )
    message = agent_a.chat(opening)
    emit(EventType.TURN, agent_a.name, message)

    scored: set = set()

    def judge_turn(speaker_name, statement):
        emit(EventType.THINK, audience.name, audience.evaluate(speaker_name, statement))
        result = audience.score(speaker_name, first=speaker_name not in scored)
        scored.add(speaker_name)
        emit(EventType.SCORE, audience.name, result.get("reasoning", ""),
             target=speaker_name, score=result.get("score"))

    if audience:
        judge_turn(agent_a.name, message)

    speaker, listener = agent_b, agent_a
    for _ in range(turns - 1):
        emit(EventType.THINK, speaker.name, speaker.think(message))
        message = speaker.respond()
        emit(EventType.TURN, speaker.name, message)
        if audience:
            judge_turn(speaker.name, message)
        speaker, listener = listener, speaker

    if audience:
        result = audience.verdict([agent_a.name, agent_b.name],
                                  premise=premise, sides=sides)
        winner = result.get("winner")
        premise_upheld = None
        if premise and winner and sides:
            winner_side = sides.get(winner)
            if winner_side:
                premise_upheld = (winner_side == "for")

        emit(EventType.VERDICT, audience.name, result.get("reasoning", ""),
             winner=winner, scores=result.get("scores", {}),
             premise=premise, premise_upheld=premise_upheld)
