# Debate Call Flow

A single debate with two debaters (A and B) and one judge. `turns=6` is used as the example,
meaning 6 public statements total: A opens, then B and A alternate for 5 more turns.

Each agent maintains its own **chat history** for the full debate — every prompt and response
is appended, so later calls have full context of everything that came before.

---

## System prompts (set once, persist for the whole debate)

### Debater system prompt
Built from YAML fields joined by double newline, in order:
```
{personality}

{position}

{instructions}
```

### Judge system prompt
```
{personality}

{judging_criteria}
```

---

## Stage 1 — Planning (both debaters, no judge involvement)

Both debaters are prompted in sequence before any public exchange.

**Prompt sent to each debater:**
```
The debate topic is: {topic}

Before the debate begins, privately plan your argument. What are your two or
three strongest points? What counterarguments do you expect, and how will you
answer them?
```

**Returns:** free-form planning text (emitted as `PLAN` event, shown dimmed in output)

---

## Stage 2 — Opening statement (debater A only)

**Prompt sent to debater A:**
```
Let's debate the following topic: {topic}

You're speaking with {B.name}. Please open the discussion.
```

**Returns:** opening statement (emitted as `TURN` event)

> Note: this is `agent_a.chat(opening)` directly, not via `respond()`. It does not use the
> think/respond two-step — the opening is generated in a single call.

---

## Stage 3 — Judge scores opening statement (judge only)

After A's opening, the judge is called twice in sequence.

### 3a. Evaluate
**Prompt sent to judge:**
```
{A.name} just argued:

"{A's opening statement}"

Privately consider this argument. How coherent is the logic? If evidence is
used, does it actually warrant the conclusion, or does it merely suggest it?
If they are challenging their opponent's evidence, is that challenge
well-reasoned — and if so, credit it as a strong move in its own right.
How effective is the rhetoric? Note strengths and weaknesses. Do not score yet.
```

**Returns:** private evaluation text (emitted as `THINK` event for the judge)

### 3b. Score (first time seeing A)
**Prompt sent to judge** (`json_mode=True`):
```
Give {A.name} an initial score out of 10 based on this first impression.
Respond with a JSON object in exactly this format:
{"score": 7, "reasoning": "One sentence explaining the score."}
The score must be a whole number between 0 and 10 inclusive.
```

**Returns:** `{"score": int, "reasoning": str}` (emitted as `SCORE` event)

---

## Stage 4 — Turn loop (repeated turns-1 times, alternating B then A)

For each remaining turn, the current speaker thinks then responds, then the judge scores.

### 4a. Speaker thinks
**Prompt sent to current speaker:**
```
Your opponent just said:

"{previous statement}"

Before you respond, privately reflect: What did they get right or wrong?
How does this shift the argument? How might the audience be reacting?
Plan what you'll say next. Do not give your debate response yet.
```

**Returns:** private reflection text (emitted as `THINK` event for the speaker)

### 4b. Speaker responds
**Prompt sent to current speaker:**
```
Now give your actual debate response, in character.
```

**Returns:** public statement (emitted as `TURN` event)

### 4c. Judge evaluates (same prompt as 3a, different statement)
```
{speaker.name} just argued:

"{statement}"

Privately consider this argument. How coherent is the logic? ...
```

**Returns:** private evaluation text (emitted as `THINK` for judge)

### 4d. Judge scores
If this is the **first time** the judge has seen this speaker (`first=True`):
```
Give {speaker.name} an initial score out of 10 based on this first impression.
Respond with a JSON object in exactly this format:
{"score": 7, "reasoning": "One sentence explaining the score."}
The score must be a whole number between 0 and 10 inclusive.
```

For **all subsequent turns** from the same speaker (`first=False`):
```
Give your current running score for {speaker.name} out of 10. This is a
cumulative score reflecting their whole performance so far — revise it up if
they've strengthened their case, or down if they've been rebutted.
Respond with a JSON object in exactly this format:
{"score": 7, "reasoning": "One sentence explaining any change."}
The score must be a whole number between 0 and 10 inclusive.
```

**Returns:** `{"score": int, "reasoning": str}` (emitted as `SCORE` event)

---

## Stage 5 — Final verdict (judge only, three calls)

Called once after all turns are complete. Three sequential LLM calls on the judge.

### 5a. Private deliberation

**Prompt sent to judge** (free text, no JSON constraint):
```
The debate premise was:
  {A.name} argued FOR the premise: "{premise}"
  {B.name} argued AGAINST the premise: "{premise}"

The debate is over. As {judge.name}, privately weigh up what you just heard.
Who made the stronger case and why? Which specific arguments or moments swayed
you, and which fell flat? Give each debater a score out of 10 and decide on a
winner. Be specific and think as yourself.
```

> The premise context block is only included when a `premise` is defined in the config.

**Returns:** in-character deliberation text — emitted as a `THINK` event for the judge
(shown dimmed in output, before the verdict box)

### 5b. JSON extraction

**Prompt sent to judge** (`json_mode=True`):
```
Now express that verdict as a JSON object in exactly this format:
{"winner": "{A.name}", "scores": {"{A.name}": 8, "{B.name}": 6}}
All scores must be whole numbers between 0 and 10 inclusive.
The winner must be the debater with the higher score.
```

**Returns:** `{"winner": str, "scores": {name: int, ...}}`

> The winner-must-have-higher-score constraint is enforced here, which prevents the
> inconsistency where the declared winner had a lower score than their opponent.
> No `reasoning` field is requested — that comes from 5a and 5c instead.

### 5c. Public announcement

**Prompt sent to judge** (free text, no JSON constraint):
```
Now deliver your verdict to the debaters and audience. Speak as {judge.name}
— briefly, in your own voice. State who won, what they did well, and what let
the other side down. No more than a short paragraph.
```

**Returns:** in-character public verdict — used as the `reasoning` field displayed
in the verdict box

---

The system then derives `premise_upheld` from `sides[winner]` — if the winner argued FOR
the premise, it is upheld; if AGAINST, it is rejected. The THINK event (deliberation) is
emitted first, then the `VERDICT` event (public announcement + winner + scores).

---

## Full sequence for turns=6

```
[no LLM calls]         HEADER emitted

A.plan()               PLAN event — A's private planning
B.plan()               PLAN event — B's private planning

A.chat(opening)        TURN event — A's opening statement

J.evaluate(A, msg)     THINK event — judge privately evaluates A
J.score(A, first=True) SCORE event — judge's initial score for A

B.think(A_msg)         THINK event — B privately reflects
B.respond()            TURN event — B's first public statement
J.evaluate(B, msg)     THINK event — judge privately evaluates B
J.score(B, first=True) SCORE event — judge's initial score for B

A.think(B_msg)         THINK event — A privately reflects
A.respond()            TURN event — A's second statement
J.evaluate(A, msg)     THINK event
J.score(A, first=False) SCORE event — judge updates running score for A

B.think(A_msg)         THINK event
B.respond()            TURN event
J.evaluate(B, msg)     THINK event
J.score(B, first=False) SCORE event

A.think(B_msg)         THINK event
A.respond()            TURN event
J.evaluate(A, msg)     THINK event
J.score(A, first=False) SCORE event

B.think(A_msg)         THINK event
B.respond()            TURN event — B's final statement (turn 6)
J.evaluate(B, msg)     THINK event
J.score(B, first=False) SCORE event

J.verdict() call 1     THINK event  — judge's private deliberation, in character
J.verdict() call 2     (no event)   — JSON extraction: winner + scores
J.verdict() call 3     VERDICT event — judge's public announcement, in character
```

**Total LLM calls for turns=6 with a judge:**
- 2 plan calls
- 1 opening call
- 5 × 2 think+respond calls = 10 debater calls
- 6 evaluate + 6 score calls = 12 judge calls
- 3 verdict calls (deliberation, JSON extraction, public announcement)

**= 28 LLM calls total**

---

## What the judge does NOT see

- The debaters' `think()` responses — private reflections are not shared across agents
- The debaters' `plan()` responses — planning is also private
- Any prompt addressed to the debaters — only the judge's own history is in its context

## What the debaters do NOT see

- Each other's `think()` responses
- The judge's `evaluate()` or `score()` reasoning
- The judge's running scores or final verdict (debaters cannot adapt to scores)
