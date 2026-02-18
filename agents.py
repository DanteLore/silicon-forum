from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"


class Agent:
    def __init__(self, config: dict):
        self.name: str = config["name"]
        self.model: str = config["model"]
        self.color: str = config.get("color", "white")

        system_prompt = "\n\n".join(filter(None, [
            config.get("personality", "").strip(),
            config.get("position", "").strip(),
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

    def chat(self, message: str) -> str:
        self._history.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=self._history,
        )

        reply = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self._history = [self._history[0]]
