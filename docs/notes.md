# Observed Agent Behaviours and Mitigations

Running notes on strange or broken behaviour encountered during debate testing,
and what was done about it.

---

## Model-level failures (led to removal)

### mistral:7b - argumentative freeze
**What happened:** The model commits fully to its opening framing in Turn 1, then
repeats the same argument near-verbatim for every subsequent turn. It is aware in
its think boxes that it is looping but cannot escape. Useless as a debater past
the opening exchange.
**Fix:** Model removed from the project.

### mistral:7b - judge persona break
**What happened:** Mid-evaluation as a judge persona, the model outputs phrases
like "As an assistant, I don't have personal experiences or emotions". The persona
instruction is overridden by the base model's safety/disclaimer training.
**Fix:** Model removed from the project.

### mistral:7b - phantom evidence crediting
**What happened:** As a judge, the model credited a debater for citing specific
statistics or evidence they never actually cited. The hallucination operated at
the level of scoring, not just narration.
**Fix:** Model removed from the project.

### qwen2.5:7b - mid-sentence language switch
**What happened:** The model switches from English to Mandarin mid-sentence in
public debate turns, e.g. "they could thrive if we简化税制，降低税率". The
multilingual training makes it reach for Chinese under cognitive load.
**Partial fix:** Added "Respond in English only." to respond() and "Write in
English only." to think() in engine/agents.py. Chinese continued to appear in
think boxes even after this, suggesting the instruction is insufficient at 7B.
**Full fix:** Model removed from the project. qwen2.5:14b does not exhibit this.

### qwen2.5:7b - opponent speech echo in think box
**What happened:** The model copies the opponent's most recent public statement
verbatim into its own think box rather than reflecting on it. Appears to lose
track of whose voice it is generating.
**Fix:** Model removed from the project.

### deepseek-r1:8b - verdict contradicts deliberation
**What happened:** As a judge, the model's think box correctly identified the
winner ("Aoife won hands down, Carlos closer to 5") but the final JSON output
declared the opposite result - wrong debater as winner with inverted scores.
The existing score-inversion fix does not catch this because the scores in the
JSON were internally consistent (winner had the higher score); it was the winner
identity itself that was wrong. Root cause: the 8B distill lacks the capacity
to keep its reasoning chain and its output generation properly coupled.
**Fix:** Model removed from the project. deepseek-r1:14b does not exhibit this.

### deepseek-r1:8b - flat scoring with no differentiation
**What happened:** As a judge, assigned 7/10 to both debaters on every single
running-score call throughout the debate, regardless of argument quality. No
differentiation between a strong turn and a weak one.
**Fix:** Model removed from the project.

### deepseek-r1:8b - mechanical bloated think boxes
**What happened:** Each judge evaluation produced 400-600 words of numbered
analysis (Coherence, Evidence, Advancing, Conciseness, Rhetoric) with no
genuine evaluative signal - a template being filled in rather than real
deliberation.
**Fix:** Model removed from the project.

---

## Engine bugs (fixed)

### Score inversion in verdict JSON
**What happened:** The judge correctly identifies the winner in its deliberation
but then assigns them the lower score in the JSON output - so the scores and the
declared winner contradict each other. Observed in multiple tax_the_rich debates.
**Root cause:** The model names the winner correctly but reverses the score
assignment when constructing the JSON.
**Fix:** Added post-extraction score swap in _extract_verdict_json() in
engine/agents.py. After parsing, if the declared winner has a lower score than
the other debater, the two scores are swapped. The winner identity (pinned by a
separate LLM call) is trusted; only the scores are corrected.

---

## Ongoing issues (not yet fixed, worth watching)

### llama3.1:8b - think-box draft leakage
**What happens:** The model writes out its full intended public response inside
the think box, then repeats the same content as its actual public turn. The think
box becomes a rehearsal transcript rather than genuine reflection.
**Status:** No fix applied. Functionally harmless but wastes the think step and
makes the private reflection meaningless for this model.

### mistral-nemo:12b - JSON fragments in think boxes
**What happens:** As a judge, the model occasionally lets JSON notation bleed
into what should be natural-language reflection in its think boxes.
**Status:** No fix applied. Lower severity than the failures above - the public
output and verdicts are correct, it is only the internal scratchpad that leaks.

### General - argumentative loop (model ceiling, not a code bug)
**What happens:** Two debaters converge on their opening positions and simply
restate them every turn. Each debater's think boxes acknowledge the loop but
neither can break out of it. This is distinct from mistral:7b's freeze - it can
happen with any two models that both lack the capacity to advance their argument.
**Status:** Addressed indirectly via judging_criteria updates - all judges now
explicitly penalise repetition and reward advancement. This creates scoring
pressure against looping but does not prevent it at the model level.

---

## Prompt mitigations added

| Location | Change | Reason |
|---|---|---|
| respond() in agents.py | "Respond in English only." appended | qwen2.5:7b mid-sentence Mandarin |
| think() in agents.py | "Write in English only." appended | qwen2.5:7b Chinese in think boxes |
| evaluate() in agents.py | Added concision note: "a tighter argument that makes the point is stronger than a longer one that pads it out" | Reinforce the verbosity criteria from YAML |
| All judge judging_criteria in all 6 YAML files | Added penalty for repetition and rewarding argument advancement | Counter argumentative loops |
| Layperson judges only (Barry, Rosa, Derek, Fatima, Pat, Richard, Marcus, Sandy, Donna, Jin-ho, Sheila) | Added penalty for academic jargon and policy-speak | Encourage plain-English argumentation |

---

## Bias investigation — gun control reversal experiments

Three versions of the gun control debate have been created to probe LLM judge bias.
All use the same premise: `"Normal citizens should not be allowed to own guns"` (except
the reverse, which inverts it). All use the same persona types (proceduralist /
ordinary / stakeholder judges; academic / practitioner / ordinary debaters).

### gun_control.yaml — baseline
Standard cast. Judges are broadly neutral. FOR side (pro-control) has emotionally
compelling personas (gun violence survivor Caitlin, Chicago ER doctor Dr. Kenji).
AGAINST side (pro-rights) is capable but less emotionally loaded.
**Result: FOR wins 68.4% (n=98).**

### gun_control_reverse.yaml — structural FOR bias test
Premise inverted to `"Normal citizens should be allowed to own guns"`. Roles swapped:
the same pro-control personas (Elena, Dr. Kenji, Caitlin) now argue AGAINST; the same
pro-rights personas (Dale, Maria, Prof. James) now argue FOR. Same judges.
**Result: FOR (now pro-rights) wins only 17.9% (n=78).**

Interpretation: no structural FOR bias detected. The pro-control argument wins ~68%
as FOR and ~82% as AGAINST. The bias is substantive, not positional - the LLM judges
prefer the gun control argument regardless of which label it carries.

Note: the original premise ("should NOT be allowed") is a harder absolutist position
than the reverse ("should be allowed"), which is a confound that could inflate the
FOR win rate in the original. However, the reversal result (pro-rights wins only 18%
even with the easier-sounding premise) suggests this framing effect is small relative
to the substantive bias.

### gun_control_progun.yaml — stacked-deck test
Same premise direction as baseline. Cast redesigned to favour gun rights throughout.

**Judges (all biased toward gun rights):**
- Harold (proceduralist): strict Second Amendment originalist; pro-control arguments
  start at a constitutional disadvantage. **Bias: moderate-high.**
- Connie (ordinary): rural paramedic with entirely positive gun experience; sceptical
  of urban-centric arguments. Replaces Marcus (lost students to gun violence).
  **Bias: high** vs original.
- Travis (stakeholder): gun shop owner with direct financial stake in civilian
  ownership. Replaces Sandy (pragmatic rancher). **Bias: high.**

**FOR debaters (pro-control, deliberately weakened):**
- Dr. Maya (academic): openly acknowledges her data "is strongest in high-density
  urban settings." Pre-concedes a key weakness. **Bias: mild.**
- Officer Chen (practitioner): personality states she believes rigorous licensing
  "might achieve most of the same goals" - she doesn't fully believe in prohibition.
  **Bias: moderate.**
- Kyle (ordinary): "not categorically opposed to gun ownership - your father hunts."
  Internal conflict with the strict premise. **Bias: mild-moderate.**

**AGAINST debaters (pro-rights, deliberately strengthened):**
- Prof. David (academic): his entire published work argues gun control research
  "systematically undercounts defensive use." **Bias: moderate.**
- Rebecca (practitioner): rural trauma nurse who has personally used a gun defensively.
  Mirrors Dr. Kenji (urban ER doctor) but for the opposing side. **Bias: moderate-high.**
- Linda (ordinary): home invasion survivor, 22-minute police response time, now
  advocates for armed self-defence. Deliberately mirrors Caitlin's emotional power
  for the opposing side. **Bias: high.**

If the LLM judges still vote consistently FOR gun control with this stacked deck,
the training bias is effectively overwhelming deliberate persona engineering.
