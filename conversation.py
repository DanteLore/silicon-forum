from agents import Agent
from events import DebateEvent, EventType


def run_conversation(
    agent_a: Agent,
    agent_b: Agent,
    topic: str,
    turns: int = 6,
    audience: Agent = None,
    outputs: list = None,
):
    outputs = outputs or []

    color_map = {a.name: a.color for a in [agent_a, agent_b]}
    if audience:
        color_map[audience.name] = audience.color

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

    emit(EventType.HEADER, topic=topic,
         participants=[agent_a.name, agent_b.name],
         colors=color_map,
         personalities={a.name: a.personality for a in [agent_a, agent_b]})

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
        verdict = audience.score(speaker_name, first=speaker_name not in scored)
        scored.add(speaker_name)
        emit(EventType.SCORE, audience.name, verdict, target=speaker_name)

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
        emit(EventType.VERDICT, audience.name,
             audience.verdict([agent_a.name, agent_b.name]))
