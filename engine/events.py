from dataclasses import dataclass, field
from enum import Enum, auto


class EventType(Enum):
    HEADER = auto()   # debate metadata — topic, participants
    PLAN = auto()     # agent's pre-debate planning (private)
    THINK = auto()    # agent's mid-debate reflection (private)
    SEARCH = auto()   # agent performs a web search; content=query, metadata results=[{title,url}]
    TURN = auto()     # agent's public statement
    SCORE = auto()    # judge scores a speaker
    VERDICT = auto()  # judge's final verdict


@dataclass
class DebateEvent:
    type: EventType
    speaker: str = ""
    content: str = ""
    color: str = "white"        # colorama Fore name, lowercase
    metadata: dict = field(default_factory=dict)
