# agent-test

A Python project for running conversations between two locally-hosted AI agents with configurable personalities.

## Stack

- **Python 3.13** in a venv (`venv/Scripts/python`)
- **Ollama** — local LLM server at `http://localhost:11434/v1`, OpenAI-compatible API
- **openai** — Python client pointed at Ollama
- **pyyaml** — config loading
- **colorama** — terminal colour output

## Project structure

```
main.py            entry point; loads config, constructs agents, runs conversation
agents.py          Agent class — loads from dict, manages chat history
conversation.py    run_conversation(); handles turn-taking and terminal output
config/            one YAML file per conversation scenario
```

## Running

```bash
venv/Scripts/python main.py                        # uses config/can_ai_think.yaml
venv/Scripts/python main.py config/other.yaml      # specify a config
```

## Conversation config (YAML)

```yaml
topic: "..."
turns: 10          # optional, default 6
line_width: 80     # optional, default 80

agents:
  - name: Archie
    model: llama3.1:8b
    color: cyan            # any colorama Fore.* name, lowercase
    personality: >         # who they are
    position: >            # what they're arguing for
    instructions: >        # behavioural directives (brevity etc)
```

All three agent text fields are optional and are joined into the system prompt in order: personality → position → instructions.

## Code style

- Simple, readable code — optimised for clarity over cleverness
- Short files, minimal comments (only where logic isn't obvious)
- No defensive guards or unnecessary fallbacks — fail fast
- No error handling for internal/expected paths; only at real boundaries
- No docstrings on obvious functions
