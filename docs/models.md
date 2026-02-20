# Model Biographies

Six models currently installed in Ollama for Silicon Forum debates. Two models were evaluated and removed - see their entries below.

---

## llama3.1:8b

**Developer:** Meta AI
**Released:** July 2024
**Parameters:** 8 billion
**Architecture:** Llama 3.1 (decoder-only transformer)

Meta's Llama 3.1 family was a landmark release in open-weight AI. The 8B model supports a 128k token context window and strong multilingual capability - a significant step up from earlier Llama generations. Instruction-tuned variants follow directions reliably, making it a solid debate participant.

The Llama lineage began when Meta released Llama 1 in early 2023, touching off the open-source LLM explosion. Llama 3.1 consolidated Meta's position as the dominant force in open-weight models. The 8B version is widely used as a baseline and workhorse - fast, cheap to run, and capable enough for most tasks. Community reception has been overwhelmingly positive; it remains one of the most downloaded models on Hugging Face.

**Strengths:** Reliable instruction following, good general reasoning, well-documented behaviour from extensive community use.
**Weaknesses:** Can be verbose; sometimes hedges where a confident take would be more interesting.

---

## ~~mistral:7b~~ (removed)

**Developer:** Mistral AI (Paris, France)
**Released:** September 2023
**Parameters:** 7 billion
**Architecture:** Grouped-query attention, sliding window attention

Mistral 7B was a watershed moment. When it dropped in September 2023, it outperformed Llama 2 13B on most benchmarks despite being nearly half the size. The architectural choices - grouped-query attention for inference speed, sliding window attention for efficient long-context handling - demonstrated that architectural cleverness could substitute for raw parameter count.

Mistral AI was founded by former DeepMind and Meta researchers and quickly became one of the most respected names in the European AI scene. The 7B model established their reputation for efficiency-first design. It remains a favourite for anyone running models locally - fast enough to be practical, capable enough to be useful.

**Strengths:** Speed, efficiency, punches above its weight, strong at structured tasks.
**Weaknesses:** Older model now; newer options have surpassed it on most benchmarks. Can be blunt.

**Removed from Silicon Forum (February 2026).** Observed failures in debate testing:
- Freezes on its opening framing after Turn 1 and repeats the same argument near-verbatim for every subsequent turn - useless as a debater once the round gets going.
- Breaks judge persona mid-evaluation with "As an assistant, I don't have personal experiences or emotions", destroying the illusion required for the format.
- Has credited debaters for citing specific evidence or statistics they never actually cited.
Replaced by mistral-nemo:12b, which is substantially more capable at holding and developing a position.

---

## mistral-nemo:12b

**Developer:** Mistral AI and NVIDIA (joint)
**Released:** July 2024
**Parameters:** 12 billion
**Architecture:** Transformer with 128k context window

Mistral NeMo was developed in collaboration with NVIDIA, bringing NVIDIA's NeMo training infrastructure to bear on a mid-size model. The 12B parameter count sits between the scrappy 7B and heftier open models, and the 128k context window makes it one of the more capable local models for tasks requiring sustained attention.

The collaboration with NVIDIA is notable - it signals Mistral's ambition beyond pure model research into the enterprise and infrastructure space. Community reception has been positive, particularly for multilingual tasks where NeMo outperforms earlier Mistral releases.

**Strengths:** Large context window, good multilingual capability, balanced size vs. quality.
**Weaknesses:** The collaborative design means it lacks some of the tight opinionation of pure Mistral releases; can feel committee-designed.

---

## gemma2:9b

**Developer:** Google DeepMind
**Released:** June 2024
**Parameters:** 9 billion
**Architecture:** Based on Gemini research; uses alternating local/global attention

Gemma 2 is Google's open-weight model family, derived from the research underpinning the proprietary Gemini models. The 9B variant is the mid-size option in the family (alongside 2B and 27B). It uses an architectural trick of alternating local and global attention layers, which improves efficiency while preserving long-range reasoning.

Google's entry into the open-weight space was initially met with scepticism - their first Gemma release was competent but not exciting. Gemma 2 changed that. Benchmarks showed it significantly outperforming same-size competitors, and the community warmed to it quickly. It is particularly noted for instruction-following quality and relatively safe, coherent output.

**Strengths:** Strong reasoning for its size, clean and coherent outputs, good instruction following.
**Weaknesses:** Tends toward caution and balance; may struggle to commit to a position with genuine conviction.

---

## ~~qwen2.5:7b~~ (removed)

**Developer:** Alibaba Cloud (Qwen Team, China)
**Released:** September 2024
**Parameters:** 7 billion
**Architecture:** Decoder-only transformer with GQA

Qwen 2.5 is Alibaba's flagship open-weight model family, and the 7B variant punches well above its weight. Trained on 18 trillion tokens - a significantly larger dataset than most competitors - Qwen 2.5 shows the effect of data scale even at small parameter counts. It has exceptional multilingual capability, unsurprisingly strong in Chinese, but surprisingly competitive in English reasoning tasks.

The Qwen family has become a genuine contender that Western AI labs can no longer ignore. The 2.5 generation showed significant improvements in mathematics, coding, and instruction following over its predecessors. Community reception has been enthusiastic, particularly among users who want capable local models without Meta or Google provenance.

**Strengths:** Data-rich training, strong reasoning, excellent multilingual support, competitive on math/coding.
**Weaknesses:** Some reports of verbose or over-qualified responses in conversational tasks.

**Removed from Silicon Forum (February 2026).** Observed failures in debate testing:
- Switches from English to Mandarin mid-sentence in public debate turns (e.g. "they could thrive if we简化税制，降低税率"), rendering output unusable for an English-language debate format.
- Copies the opponent's most recent public statement verbatim into its own think box rather than reflecting on it, suggesting the model loses track of whose voice it is generating.
- Chinese characters also appear in think boxes even after "Write in English only" instructions were added.
The multilingual training that makes the model strong in other contexts is a liability here. The 14B variant (qwen2.5:14b) does not exhibit these problems and remains in use.

---

## phi4:latest

**Developer:** Microsoft Research
**Released:** December 2024
**Parameters:** 14 billion
**Architecture:** Decoder-only transformer, trained heavily on synthetic data

Phi-4 is the latest in Microsoft's "small but mighty" Phi series, which has consistently demonstrated that model capability is more about training data quality than raw parameter count. Where most models are trained primarily on web-scraped text, Phi-4 leans heavily into synthetic data - problems, solutions, and reasoning chains generated specifically to teach structured thinking.

The result is a model that performs remarkably well on reasoning and STEM benchmarks, often matching models two or three times its size. The AI research community has watched the Phi series with great interest as evidence that the "just scale it up" orthodoxy has limits. Phi-4 at 14B is larger than the earlier Phi models but still comfortably runnable on consumer hardware.

**Strengths:** Excellent structured reasoning, strong STEM performance, efficient relative to capability.
**Weaknesses:** The synthetic data diet can make it feel slightly artificial in open-ended conversation; less comfortable with nuance and ambiguity than empirically-trained models.

---

## deepseek-r1:8b

**Developer:** DeepSeek (Hangzhou, China)
**Released:** January 2025
**Parameters:** 8 billion (distilled from the full R1 671B model)
**Architecture:** Reasoning model; trained with reinforcement learning on chain-of-thought traces

DeepSeek R1 caused a genuine shock to the AI industry when it launched in January 2025. The full R1 model (671B parameters) matched or exceeded GPT-4o and Claude 3.5 Sonnet on reasoning benchmarks at a fraction of the reported training cost. The 8B version used here is a distillation of that larger model - the reasoning patterns of a frontier-class model compressed into a package that runs on a laptop.

DeepSeek's approach - using reinforcement learning to train the model to reason step by step, then distilling that capability into smaller models - demonstrated a viable alternative path to frontier capability. The release triggered a stock market reaction (Nvidia dropped significantly on fears about GPU demand) and forced a rethink in the industry about the economics of AI development.

The 8B distilled version retains much of R1's characteristic "thinking out loud" style - extended internal reasoning chains before arriving at conclusions. This makes it distinctive as a debate participant: it tends to explore a problem more thoroughly before committing to a position.

**Strengths:** Exceptional reasoning depth, trained explicitly on chain-of-thought, strong at structured argument.
**Weaknesses:** Can over-think simple questions; the extended reasoning style may produce longer, more meandering responses than the debate format rewards.

---

## deepseek-r1:14b

**Developer:** DeepSeek (Hangzhou, China)
**Released:** January 2025
**Parameters:** 14 billion (distilled from the full R1 671B model)
**Architecture:** Reasoning model; trained with reinforcement learning on chain-of-thought traces

The 14B distillation of DeepSeek R1 sits one step above the 8B variant in the distilled family. Both inherit the same RL-trained reasoning style from the 671B parent - the capacity to work through a problem systematically before committing to a position - but the 14B retains more of the parent model's nuance and is noticeably stronger on complex multi-step arguments.

At 14B, the model occupies a sweet spot: it fits comfortably in 16GB VRAM at Q4 quantization while delivering meaningfully better output than the 8B distill. For debate purposes, this translates to more coherent rebuttals, better retention of what has been said earlier in the exchange, and a reduced tendency to meander before reaching the point.

**Strengths:** Strong structured reasoning, better argument coherence and sustained attention than the 8B distill.
**Weaknesses:** Shares the parent model's tendency toward deliberate, methodical responses - can feel slow to land a punch compared to more instinctive debaters.

---

## qwen2.5:14b

**Developer:** Alibaba Cloud (Qwen Team, China)
**Released:** September 2024
**Parameters:** 14 billion
**Architecture:** Decoder-only transformer with GQA

The 14B variant of Qwen 2.5 is where the family's data-scale advantage becomes most apparent. Trained on 18 trillion tokens - more than most competitors regardless of size - Qwen 2.5 shows that training data quality and quantity can compensate for a modest parameter count. The 14B model extends this further: more capacity to encode what that massive dataset taught it.

In practice, Qwen 2.5 14B is competitive with models significantly larger. It is particularly strong at tasks requiring sustained logical consistency - following a line of argument across multiple exchanges without quietly shifting position. The model's Chinese provenance occasionally surfaces in the framing of arguments, which can make for an interesting counterpoint to the Western-centric assumptions baked into Meta and Google models.

**Strengths:** Data-rich training pays off at this scale; strong reasoning consistency, good at holding and developing a position across turns.
**Weaknesses:** Can be overly qualified in conversational registers; occasionally verbose when a direct answer would serve better.
