import textwrap
from colorama import Fore, Style, init as colorama_init
from agents import Agent

colorama_init()


def run_conversation(
    agent_a: Agent,
    agent_b: Agent,
    topic: str,
    turns: int = 6,
    line_width: int = 80,
    audience: Agent = None,
):
    """
    Run a back-and-forth conversation between two agents on a given topic.

    agent_a speaks first, then they alternate for `turns` total messages.
    Colors are taken from each agent's own config.
    """
    color_map = {
        agent_a.name: getattr(Fore, agent_a.color.upper()),
        agent_b.name: getattr(Fore, agent_b.color.upper()),
    }
    if audience:
        color_map[audience.name] = getattr(Fore, audience.color.upper())

    _print_header(topic, agent_a, agent_b, color_map)

    for agent in (agent_a, agent_b):
        plan = agent.plan(topic)
        _print_plan(agent.name, plan, color_map, line_width)

    print(f"{Style.BRIGHT}{'— ' * 30}{Style.RESET_ALL}\n")

    # Seed the first message — agent_a opens on the topic
    opening = (
        f"Let's discuss the following topic: {topic}\n\n"
        f"You're speaking with {agent_b.name}. Please open the discussion."
    )
    message = agent_a.chat(opening)
    _print_turn(agent_a.name, message, color_map, line_width)
    if audience:
        _judge_turn(audience, agent_a.name, message, color_map, line_width)

    # Alternate turns
    speaker, listener = agent_b, agent_a
    for _ in range(turns - 1):
        thought = speaker.think(message)
        _print_plan(speaker.name, thought, color_map, line_width)
        message = speaker.respond()
        _print_turn(speaker.name, message, color_map, line_width)
        if audience:
            _judge_turn(audience, speaker.name, message, color_map, line_width)
        speaker, listener = listener, speaker

    if audience:
        _print_verdict(audience, [agent_a, agent_b], color_map, line_width)


def _print_header(topic: str, agent_a: Agent, agent_b: Agent, color_map: dict):
    a_col, b_col = color_map[agent_a.name], color_map[agent_b.name]
    sep = Style.BRIGHT + "=" * 60 + Style.RESET_ALL
    print(f"\n{sep}")
    print(f"{Style.BRIGHT}Topic:{Style.RESET_ALL} {topic}")
    print(
        f"{Style.BRIGHT}Participants:{Style.RESET_ALL} "
        f"{a_col}{agent_a.name}{Style.RESET_ALL} and "
        f"{b_col}{agent_b.name}{Style.RESET_ALL}"
    )
    print(f"{sep}\n")


def _print_plan(name: str, plan: str, color_map: dict, line_width: int):
    color = color_map[name]
    prefix = f"{color}{Style.DIM}[{name} thinks]{Style.RESET_ALL}"
    leader_width = len(name) + 10  # len(" thinks] [")
    indent = " " * leader_width
    wrap_width = line_width - leader_width

    first_line = True
    for paragraph in plan.strip().split("\n\n"):
        para_text = " ".join(paragraph.split())
        for line in textwrap.wrap(para_text, width=wrap_width):
            if first_line:
                print(f"{Style.DIM}{prefix} {line}{Style.RESET_ALL}")
                first_line = False
            else:
                print(f"{Style.DIM}{indent}{line}{Style.RESET_ALL}")
        print()


def _judge_turn(audience: Agent, speaker_name: str, statement: str, color_map: dict, line_width: int):
    thought = audience.evaluate(speaker_name, statement)
    _print_plan(audience.name, thought, color_map, line_width)
    verdict = audience.score(speaker_name)
    _print_score(audience.name, speaker_name, verdict, color_map, line_width)


def _print_score(judge_name: str, speaker_name: str, verdict: str, color_map: dict, line_width: int):
    color = color_map[judge_name]
    prefix = f"{color}{Style.BRIGHT}[{judge_name} → {speaker_name}]{Style.RESET_ALL}"
    leader_width = len(judge_name) + len(speaker_name) + 6
    indent = " " * leader_width
    wrap_width = line_width - leader_width

    first_line = True
    for line in textwrap.wrap(" ".join(verdict.split()), width=wrap_width):
        if first_line:
            print(f"{prefix} {line}")
            first_line = False
        else:
            print(f"{indent}{line}")
    print()


def _print_verdict(audience: Agent, agents: list, color_map: dict, line_width: int):
    color = color_map[audience.name]
    sep = color + Style.BRIGHT + "=" * 60 + Style.RESET_ALL
    print(f"{sep}")
    print(f"{color}{Style.BRIGHT}FINAL VERDICT — {audience.name}{Style.RESET_ALL}\n")
    result = audience.verdict([a.name for a in agents])
    leader_width = 0
    for line in textwrap.wrap(" ".join(result.split()), width=line_width):
        print(line)
    print(f"\n{sep}\n")


def _print_turn(name: str, message: str, color_map: dict, line_width: int):
    color = color_map[name]
    prefix = f"{color}{Style.BRIGHT}{name.upper()}:{Style.RESET_ALL}"
    # Visual width of "NAME: " — used for indenting continuation lines
    leader_width = len(name) + 2
    indent = " " * leader_width
    wrap_width = line_width - leader_width

    first_line = True
    for paragraph in message.strip().split("\n\n"):
        # Collapse any mid-paragraph line breaks before wrapping
        para_text = " ".join(paragraph.split())
        for line in textwrap.wrap(para_text, width=wrap_width):
            if first_line:
                print(f"{prefix} {line}")
                first_line = False
            else:
                print(f"{indent}{line}")
        print()  # blank line between paragraphs and after final paragraph
