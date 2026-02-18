import textwrap
from colorama import Fore, Style, init as colorama_init
from events import DebateEvent, EventType

colorama_init()


class TerminalOutput:
    def __init__(self, line_width: int = 80):
        self.line_width = line_width
        self._colors: dict = {}     # built from HEADER event
        self._seen_plan = False     # tracks whether planning phase occurred
        self._debate_started = False

    def __call__(self, event: DebateEvent):
        color = getattr(Fore, event.color.upper(), Fore.WHITE)

        if event.type == EventType.HEADER:
            self._colors = {
                name: getattr(Fore, col.upper(), Fore.WHITE)
                for name, col in event.metadata["colors"].items()
            }
            self._print_header(event)

        elif event.type in (EventType.PLAN, EventType.THINK):
            self._seen_plan = True
            self._print_thought(event.speaker, event.content, color)

        elif event.type == EventType.TURN:
            if self._seen_plan and not self._debate_started:
                print(f"{Style.BRIGHT}{'— ' * 30}{Style.RESET_ALL}\n")
                self._debate_started = True
            self._print_turn(event.speaker, event.content, color)

        elif event.type == EventType.SCORE:
            target = event.metadata["target"]
            self._print_score(event.speaker, target, event.content, color,
                              score=event.metadata.get("score"))

        elif event.type == EventType.VERDICT:
            self._print_verdict(event.speaker, event.content, color,
                                winner=event.metadata.get("winner"),
                                scores=event.metadata.get("scores"))

    def _print_header(self, event: DebateEvent):
        topic = event.metadata["topic"]
        participants = event.metadata["participants"]
        personalities = event.metadata.get("personalities", {})
        sep = Style.BRIGHT + "=" * 60 + Style.RESET_ALL
        print(f"\n{sep}")
        print(f"{Style.BRIGHT}Topic:{Style.RESET_ALL} {topic}")
        names = " and ".join(
            f"{self._colors.get(n, Fore.WHITE)}{n}{Style.RESET_ALL}"
            for n in participants
        )
        print(f"{Style.BRIGHT}Participants:{Style.RESET_ALL} {names}")
        for name in participants:
            bio = personalities.get(name, "")
            if bio:
                color = self._colors.get(name, Fore.WHITE)
                prefix = f"{color}{Style.DIM}{name}:{Style.RESET_ALL}"
                leader_width = len(name) + 2
                indent = " " * leader_width
                wrap_width = self.line_width - leader_width
                first_line = True
                for line in textwrap.wrap(" ".join(bio.split()), width=wrap_width):
                    if first_line:
                        print(f"{Style.DIM}{prefix} {line}{Style.RESET_ALL}")
                        first_line = False
                    else:
                        print(f"{Style.DIM}{indent}{line}{Style.RESET_ALL}")
        print(f"{sep}\n")

    def _print_thought(self, name: str, content: str, color):
        prefix = f"{color}{Style.DIM}[{name} thinks]{Style.RESET_ALL}"
        leader_width = len(name) + 10
        indent = " " * leader_width
        wrap_width = self.line_width - leader_width

        first_line = True
        for paragraph in content.strip().split("\n\n"):
            para_text = " ".join(paragraph.split())
            for line in textwrap.wrap(para_text, width=wrap_width):
                if first_line:
                    print(f"{Style.DIM}{prefix} {line}{Style.RESET_ALL}")
                    first_line = False
                else:
                    print(f"{Style.DIM}{indent}{line}{Style.RESET_ALL}")
            print()

    def _print_turn(self, name: str, content: str, color):
        prefix = f"{color}{Style.BRIGHT}{name.upper()}:{Style.RESET_ALL}"
        leader_width = len(name) + 2
        indent = " " * leader_width
        wrap_width = self.line_width - leader_width

        first_line = True
        for paragraph in content.strip().split("\n\n"):
            para_text = " ".join(paragraph.split())
            for line in textwrap.wrap(para_text, width=wrap_width):
                if first_line:
                    print(f"{prefix} {line}")
                    first_line = False
                else:
                    print(f"{indent}{line}")
            print()

    def _print_score(self, judge: str, target: str, content: str, color, score=None):
        score_str = f" {Style.BRIGHT}{score}/10{Style.RESET_ALL}" if score is not None else ""
        prefix = f"{color}{Style.BRIGHT}[{judge} → {target}]{Style.RESET_ALL}{score_str}"
        leader_width = len(judge) + len(target) + 6 + (len(f" {score}/10") if score is not None else 0)
        indent = " " * leader_width
        wrap_width = self.line_width - leader_width

        first_line = True
        for line in textwrap.wrap(" ".join(content.split()), width=max(wrap_width, 20)):
            if first_line:
                print(f"{prefix} {line}")
                first_line = False
            else:
                print(f"{indent}{line}")
        print()

    def _print_verdict(self, judge: str, content: str, color, winner=None, scores=None):
        sep = color + Style.BRIGHT + "=" * 60 + Style.RESET_ALL
        print(f"{sep}")
        print(f"{color}{Style.BRIGHT}FINAL VERDICT — {judge}{Style.RESET_ALL}\n")
        if winner:
            winner_color = self._colors.get(winner, color)
            print(f"{Style.BRIGHT}WINNER: {winner_color}{winner}{Style.RESET_ALL}\n")
        if scores:
            score_line = "  ".join(
                f"{self._colors.get(n, Fore.WHITE)}{n}{Style.RESET_ALL} {Style.BRIGHT}{s}/10{Style.RESET_ALL}"
                for n, s in scores.items()
            )
            print(f"{score_line}\n")
        for line in textwrap.wrap(" ".join(content.split()), width=self.line_width):
            print(line)
        print(f"\n{sep}\n")
