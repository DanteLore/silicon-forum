# agent-test

A Python project for running structured debates between locally-hosted AI agents with configurable personalities, scoring, and HTML output.

## Stack

- **Python 3.13** in a venv (`venv/Scripts/python`)
- **Ollama** — local LLM server at `http://localhost:11434/v1`, OpenAI-compatible API
- **openai** — Python client pointed at Ollama
- **pyyaml** — config loading
- **colorama** — terminal colour output
- **jinja2** — HTML template rendering
- **markupsafe** — safe HTML escaping in templates

## Project structure

```
single_debate.py          Run one debate; outputs to terminal + HTML transcript
multi_debate.py           Run N debates from one config; outputs per-run transcripts + summary HTML

agents.py                 Agent class — loads from dict, manages chat history, LLM calls
conversation.py           run_conversation(); handles turn-taking, judge scoring, event emission
events.py                 DebateEvent dataclass and EventType enum

outputs/
  console.py              TerminalOutput — coloured terminal output strategy
  html.py                 HtmlOutput — per-debate HTML transcript strategy
  collector.py            ResultCollector — captures structured result data (winner, scores, judge)
  summary.py              SummaryHtml — writes/updates the multi-run summary HTML table
  templates/
    debate.html           Jinja2 template for per-debate transcript
    summary.html          Jinja2 template for multi-run summary table

debates/                  YAML config files, one per debate topic
  can_ai_think.yaml
  immigration.yaml
  tax_the_rich.yaml
  gun_control.yaml
  free_healthcare.yaml
  break_up_big_tech.yaml

results/                  Output directory — HTML transcripts and summary files (gitignored)
```

## Running

```bash
# Single debate (random persona selection per run)
venv/Scripts/python single_debate.py debates/immigration.yaml

# Multiple debates with summary
venv/Scripts/python multi_debate.py debates/immigration.yaml 10
```

Both scripts default to `debates/can_ai_think.yaml` if no config is given.
Output HTML files are written to `results/`.

## Debate YAML schema

Each config defines three pools of personas. One is randomly selected from each pool per run.

```yaml
topic: "..."
premise: "..."   # the specific claim being debated; determines premise_upheld in verdict
turns: 10        # optional, default 6
line_width: 80   # optional, default 80

audience:        # judge pool — 3 personas
  - name: ...
    model: llama3.1:8b
    color: magenta        # any colorama Fore.* name, lowercase
    personality: >        # who they are
    judging_criteria: >   # how they evaluate arguments

for:             # debater pool for the FOR side — 3 personas
  - name: ...
    model: llama3.1:8b
    color: yellow
    personality: >
    position: >           # what they are arguing
    instructions: >       # behavioural directives (brevity etc.)

against:         # debater pool for the AGAINST side — 3 personas
  - name: ...
    ...
```

The `side` field (`"for"` / `"against"`) is injected at load time by `_pick()` — it does not appear in the YAML. Debater speaking order is randomly shuffled each run.

### Persona design principles

Each pool of three should cover distinct archetypes:

1. **Academic / domain expert** — argues from research, data, technical knowledge
2. **Practitioner** — direct real-world experience in the relevant field
3. **Ordinary person** — argues from lived experience, values, or common sense

### Judge archetypes

Each debate has three judges with distinct evaluative lenses:

1. **Proceduralist / policy evaluator** — assesses argument quality, evidence standards, logical form; rewards substance over performance
2. **Ordinary person / common sense** — judges on whether arguments hold up in real life; suspicious of both academic abstraction and political sloganeering
3. **Stakeholder / contextual** — directly affected by the issue; evaluates whether arguments account for the human reality of the policy

Current judge lineups:

| Debate | Proceduralist | Ordinary person | Stakeholder |
|--------|--------------|-----------------|-------------|
| can_ai_think | Rex (forensic judge) | Sheila (retired librarian) | Kai (philosophy PhD) |
| immigration | Keiko (Sciences Po professor) | Barry (retired postal worker) | Rosa (community dev worker, immigrant) |
| tax_the_rich | Claire (IFS economist) | Pat (middle manager) | Richard (retired accountant) |
| gun_control | Miriam (retired federal judge) | Marcus (school teacher, Atlanta) | Sandy (Montana rancher) |
| free_healthcare | Niamh (Trinity College health systems) | Derek (retired steelworker) | Fatima (pharmacist, Nigerian-born) |
| break_up_big_tech | Pieter (Amsterdam competition law) | Donna (market trader, Birmingham) | Jin-ho (Korean startup founder) |

### YAML style rules

- No em dashes — use ` - ` instead
- No non-ASCII characters anywhere
- Block scalars use `>` (folded); trailing whitespace stripped by YAML

## Event system

`conversation.py` emits `DebateEvent` objects consumed by all output strategies.

```python
class EventType(Enum):
    HEADER   # debate metadata: topic, premise, participants, sides, judge
    PLAN     # debater's private pre-debate planning
    THINK    # debater's private mid-debate reflection; or judge's private evaluation
    TURN     # debater's public statement
    SCORE    # judge's running score for one speaker
    VERDICT  # judge's final verdict: winner, scores, reasoning, premise_upheld
```

`DebateEvent` fields: `type`, `speaker`, `content`, `color`, `metadata` (dict).

Key metadata shapes:

- `HEADER`: `topic`, `premise`, `participants`, `sides` ({name: "for"|"against"}), `colors` ({name: color}), `personalities` ({name: str}), `judge` ({name, color, personality, judging_criteria})
- `SCORE`: `target` (speaker being scored), `score` (int)
- `VERDICT`: `winner`, `scores` ({name: int}), `premise`, `premise_upheld` (bool|None)

## Output strategies

All output strategies are callables that accept a `DebateEvent`.

### TerminalOutput (`outputs/console.py`)

Coloured terminal output. Shows:
- Header with For/Against/Judge profiles (name + bio, indented)
- Planning phase in dim style, separated from debate by a rule
- Each turn in bright colour with the speaker's name
- Judge scores and running commentary after each turn
- Final verdict box with winner, scores, and premise result

### HtmlOutput (`outputs/html.py`)

Writes a live-updating HTML transcript after every event (so the file is always readable mid-debate). Uses `debate.html` template. Maps colorama colour names to readable CSS colours for white backgrounds.

### ResultCollector (`outputs/collector.py`)

Lightweight collector for `multi_debate.py`. Captures `winner`, `scores`, `premise`, `premise_upheld`, `sides`, and `judge` name from events. No output of its own.

### SummaryHtml (`outputs/summary.py`)

Accumulates per-run results and rewrites the summary HTML table after each run. Table columns: `#`, For, Against, Judge, Winner, Scores, Result (premise upheld/rejected badge), Link.

## Agent internals (`agents.py`)

System prompt is assembled from `personality` + `position` + `judging_criteria` + `instructions` (any absent fields skipped). Chat history is maintained per-agent instance and reset between runs in `multi_debate.py`.

Key methods:
- `plan(topic)` — pre-debate argument planning
- `think(opponent_message)` — mid-debate private reflection
- `respond()` — public debate turn
- `evaluate(speaker_name, statement)` — judge privately considers a statement
- `score(speaker_name, first)` — judge gives running score; returns `{"score": int, "reasoning": str}`
- `verdict(names, premise, sides)` — judge gives final verdict; returns `{"winner": str, "scores": {...}, "reasoning": str}`

JSON responses from `score()` and `verdict()` strip markdown code fences before parsing.

## Code style

- Simple, readable code — optimised for clarity over cleverness
- Short files, minimal comments (only where logic isn't obvious)
- No defensive guards or unnecessary fallbacks — fail fast
- No error handling for internal/expected paths; only at real boundaries
- No docstrings on obvious functions
