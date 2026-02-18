import json
import re
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"


def _parse_json(text: str) -> dict:
    """Parse a JSON response, stripping markdown code fences if present."""
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text.strip())


class Agent:
    def __init__(self, config: dict):
        self.name: str = config["name"]
        self.model: str = config["model"]
        self.color: str = config.get("color", "white")
        self.personality: str = config.get("personality", "").strip()
        self.judging_criteria: str = config.get("judging_criteria", "").strip()
        self.side: str | None = config.get("side")   # "for" | "against" | None

        system_prompt = "\n\n".join(filter(None, [
            config.get("personality", "").strip(),
            config.get("position", "").strip(),
            config.get("judging_criteria", "").strip(),
            config.get("instructions", "").strip(),
        ]))

        self._client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        self._history: list[dict] = [
            {"role": "system", "content": system_prompt}
        ]

    def plan(self, topic: str) -> str:
        prompt = (
            f"The debate topic is: {topic}\n\n"
            "Before the debate begins, privately plan your argument. "
            "What are your two or three strongest points? "
            "What counterarguments do you expect, and how will you answer them?"
        )
        return self.chat(prompt)

    def evaluate(self, speaker_name: str, statement: str) -> str:
        prompt = (
            f"{speaker_name} just argued:\n\n\"{statement}\"\n\n"
            "Privately consider this argument. How coherent is the logic? "
            "If evidence is used, does it actually warrant the conclusion, or does it merely "
            "suggest it? If they are challenging their opponent's evidence, is that challenge "
            "well-reasoned — and if so, credit it as a strong move in its own right. "
            "How effective is the rhetoric? Note strengths and weaknesses. Do not score yet."
        )
        return self.chat(prompt)

    def score(self, speaker_name: str, first: bool = False) -> dict:
        """Return {"score": int, "reasoning": str}."""
        if first:
            prompt = (
                f"Give {speaker_name} an initial score out of 10 based on this first impression. "
                "Respond with a JSON object in exactly this format:\n"
                '{"score": 7, "reasoning": "One sentence explaining the score."}\n'
                "The score must be a whole number between 0 and 10 inclusive."
            )
        else:
            prompt = (
                f"Give your current running score for {speaker_name} out of 10. "
                "This is a cumulative score reflecting their whole performance so far — "
                "revise it up if they've strengthened their case, or down if they've been rebutted. "
                "Respond with a JSON object in exactly this format:\n"
                '{"score": 7, "reasoning": "One sentence explaining any change."}\n'
                "The score must be a whole number between 0 and 10 inclusive."
            )
        raw = self.chat(prompt, json_mode=True)
        return _parse_json(raw)

    def _extract_verdict_json(self, names: list[str]) -> dict:
        """Ask the model to emit a structured verdict dict, retrying on bad output.

        Up to 3 attempts. Each retry tells the model exactly which field was wrong.
        If all attempts fail, falls back to deriving the winner from scores (or a
        safe placeholder) so the caller always receives a usable dict.
        """
        example = (
            f'{{"winner": "{names[0]}", '
            f'"scores": {{"{names[0]}": 8, "{names[1]}": 6}}}}'
        )
        base_prompt = (
            f"Now express that verdict as a JSON object. "
            f"Output only the JSON — no other text — in exactly this format:\n"
            f"{example}\n"
            f'The "winner" must be exactly {names[0]!r} or {names[1]!r}. '
            f'The "scores" dict must contain entries for both names. '
            f"All scores must be whole numbers between 0 and 10. "
            f"The winner must be the debater with the higher score."
        )

        result: dict = {}
        for attempt in range(3):
            if attempt == 0:
                prompt = base_prompt
            else:
                problems = []
                if result.get("winner") not in names:
                    problems.append(
                        f'"winner" must be {names[0]!r} or {names[1]!r}, '
                        f'got {result.get("winner")!r}'
                    )
                for n in names:
                    if n not in result.get("scores", {}):
                        problems.append(f'"scores" is missing an entry for {n!r}')
                prompt = (
                    f"Your previous response had problems: {'; '.join(problems)}. "
                    f"Return ONLY a JSON object in exactly this format:\n{example}"
                )

            try:
                raw = self.chat(prompt, json_mode=True)
                result = _parse_json(raw)
            except Exception:
                result = {}
                continue

            if (result.get("winner") in names
                    and all(n in result.get("scores", {}) for n in names)):
                return result

        # Fallback: derive winner from whatever scores we have
        scores = result.get("scores", {})
        if all(n in scores for n in names):
            result["winner"] = max(names, key=lambda n: scores.get(n, 0))
        else:
            result.setdefault("winner", names[0])
            result.setdefault("scores", {n: 5 for n in names})
        print(f"Warning: judge {self.name!r} produced a malformed verdict after 3 attempts; "
              f"using fallback (winner={result['winner']!r})")
        return result

    def verdict(self, names: list[str], premise: str = None,
                sides: dict = None) -> dict:
        """Return {"winner": str, "scores": {name: int, ...}, "reasoning": str}."""
        context = ""
        if premise and sides:
            lines = []
            for name in names:
                side = sides.get(name)
                if side:
                    label = "FOR" if side == "for" else "AGAINST"
                    lines.append(f'  {name} argued {label} the premise: "{premise}"')
            if lines:
                context = "The debate premise was:\n" + "\n".join(lines) + "\n\n"

        # Call 1 — private deliberation; persona can come through freely
        deliberation = self.chat(
            f"{context}"
            f"The debate is over. As {self.name}, privately weigh up what you just heard. "
            f"Who made the stronger case and why? Which specific arguments or moments "
            f"swayed you, and which fell flat? Give each debater a score out of 10 "
            f"and decide on a winner. Be specific and think as yourself."
        )

        # Call 2 — extract structure from the deliberation; enforce score consistency
        result = self._extract_verdict_json(names)

        # Call 3 — public announcement in character, shown in the verdict box
        result["reasoning"] = self.chat(
            f"Now deliver your verdict to the debaters and audience. Speak as {self.name} "
            f"— briefly, in your own voice. State who won, what they did well, "
            f"and what let the other side down. No more than a short paragraph."
        )
        result["deliberation"] = deliberation   # returned for THINK emission
        return result

    def think(self, opponent_message: str) -> str:
        prompt = (
            f"Your opponent just said:\n\n\"{opponent_message}\"\n\n"
            "Before you respond, privately reflect: What did they get right or wrong? "
            "How does this shift the argument? How might the audience be reacting? "
            "Plan what you'll say next. Do not give your debate response yet."
        )
        return self.chat(prompt)

    def respond(self) -> str:
        return self.chat("Now give your actual debate response, in character.")

    def chat(self, message: str, json_mode: bool = False) -> str:
        self._history.append({"role": "user", "content": message})

        kwargs = dict(model=self.model, messages=self._history)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**kwargs)

        reply = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self._history = [self._history[0]]
