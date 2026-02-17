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
