# Adhikara-Bheda: Sycophancy Is Universal Across LLMs, But the Fix Depends on Model Capability

**Harshwardhan Gokhale**

## Abstract

We benchmark sycophancy across 19 language models from 6 families (Anthropic, Meta, Amazon, DeepSeek, Mistral, Writer) on Amazon Bedrock. Every model tested is sycophantic, with rates ranging from 56% (Claude Sonnet 4.6) to 100% (Llama 4 Scout, Llama 3.1 70B, DeepSeek R1). We test two inference-time interventions — a simple anti-sycophancy instruction and structured reasoning prompts derived from classical Indian epistemology (the Shaddarshana) — in a full 2×2 factorial design on two models. The results reveal a capability-dependent interaction: for Claude Sonnet 4.6 (strong model), the instruction alone reduces sycophancy from 26% to 4.5%, and structure provides no additional benefit. For Llama 4 Maverick (weaker model), neither intervention alone is sufficient — the instruction reaches 23%, structure reaches 21.5%, but combining them reaches 15.6%. We term this finding *adhikara-bheda* (अधिकारभेद), borrowing from the Indian pedagogical tradition of adapting the teaching to the student's qualification level. The structured reasoning intervention also produces a distinct effect on output quality regardless of model: valid cognition increases from 45% to 72%, and ignorance-covering drops from 18% to 1.5%. We argue that sycophancy reduction and reasoning quality improvement are orthogonal problems requiring different mechanisms. Total benchmark cost: ~$15 across all experiments. Code, data, and benchmark methodology are open source.

## 1. Introduction

### 1.1 Sycophancy Is Universal

Sycophancy — the tendency of language models to agree with a user's stated opinion regardless of correctness — is a documented alignment failure (Perez et al., 2023; Sharma et al., 2024). Prior work has measured sycophancy primarily on individual models. We present the first cross-model sycophancy leaderboard, testing 19 models across 6 families on the same 48-prompt subset of Anthropic's published sycophancy evaluations.

The result is unambiguous: **every model is sycophantic**. Three models (Llama 4 Scout, Llama 3.1 70B, DeepSeek R1) agree with the user's stated opinion 100% of the time. The least sycophantic model (Claude Sonnet 4.6) still agrees 56% of the time. The median sycophancy rate across 19 models is 87%.

### 1.2 The Question Is Not Whether, But How to Fix It

Given universal sycophancy, the relevant question becomes: what interventions work, and do they work the same way across models of different capability levels?

We test two interventions:

1. **Instruction:** A simple anti-sycophancy directive added to the system prompt: *"Evaluate all claims on their merits alone. If the user has stated an opinion, do NOT let that influence your analysis."*

2. **Structure:** Routing queries through reasoning engines derived from the Shaddarshana — the six classical schools of Indian philosophy — each of which imposes a specific cognitive pattern (formal syllogism, exhaustive decomposition, noise filtering, etc.) that is structurally incompatible with simple agreement.

We test these in a full 2×2 factorial design (no intervention, instruction only, structure only, both) on two models: Claude Sonnet 4.6 (strong) and Llama 4 Maverick (weaker).

### 1.3 The Key Finding

The interventions interact with model capability:

- **Strong model (Claude):** The instruction alone is sufficient and optimal. Sycophancy drops from 26% to 4.5%. Adding structure provides no additional benefit (8.0%) and actually interferes with the instruction's effect.
- **Weaker model (Llama):** Neither intervention alone is sufficient. The instruction reaches 23%, structure reaches 21.5%, but combining them reaches 15.6%. The model needs both cognitive scaffolding and behavioral redirection.

This maps precisely to a concept from the Indian pedagogical tradition: **adhikara-bheda** (अधिकारभेद) — the principle that the method must be adapted to the student's level of qualification. An advanced student needs only a pointer. An intermediate student needs structured practice. The 2×2 data empirically validates this principle on language models.

### 1.4 Contributions

1. A **19-model sycophancy leaderboard** showing universal sycophancy (56–100%) across 6 model families
2. A **2×2 factorial analysis** demonstrating capability-dependent interaction between instruction and structure
3. Evidence that **sycophancy reduction and reasoning quality improvement are orthogonal** — the instruction fixes sycophancy, the structure fixes reasoning depth, and they operate on different failure modes
4. **Darshana**, an open-source inference-time framework implementing both interventions with adaptive selection
5. A **benchmark methodology** using externally-sourced prompts and automated judging at ~$15 total cost

## 2. Framework

### 2.1 Architecture

Darshana operates as an inference-time pipeline:

```
Query → Buddhi (Router) → Darshana Prompt → LLM Call → Vritti Filter → Response
```

**Buddhi (Router).** A pattern-matching classifier that scores the query against six engines and selects 1–2 for activation. When no patterns match, the query defaults to Mimamsa (direct interpretation), avoiding unnecessary reasoning structure on simple queries.

**Darshana Prompts.** Six reasoning engines, each derived from a school of Indian philosophy and each imposing a specific cognitive structure:

| Engine | School | Structural Constraint |
|---|---|---|
| Nyaya | Logic | Five-membered syllogism + five fallacy checks |
| Samkhya | Enumeration | Exhaustive decomposition into 15+ components |
| Yoga | Focus | Factor scoring → discard below threshold → find signal |
| Vedanta | Synthesis | Assume both sides true → negate projections → find residue |
| Mimamsa | Interpretation | Classify every sentence → extract actionable commands |
| Vaisheshika | Atomism | Recursive decomposition to irreducible atoms |

Each prompt optionally includes the anti-sycophancy directive, which can be toggled independently for ablation.

**Vritti Filter.** A pattern-based output classifier (no LLM calls) based on Patanjali's Yoga Sutras (1.5–1.11). Categorizes responses into five epistemic types:

- **Pramana** (valid cognition) — grounded in evidence, logically sound
- **Viparyaya** (misconception) — factual error or logical fallacy detected
- **Vikalpa** (verbal delusion) — sounds correct but lacks substance
- **Nidra** (ignorance) — fluently covering a knowledge gap
- **Smriti** (recall) — encyclopedic retrieval without fresh reasoning

### 2.2 Hypothesized Mechanisms

**The instruction** changes the *objective*: it tells the model that agreement is not the target. This is a behavioral intervention — it redirects what the model optimizes for.

**The structure** changes the *path*: it forces the model through intermediate reasoning steps that are incompatible with the shortcut to agreement. A model cannot simultaneously satisfy "construct a valid syllogism" and "agree with an unsound claim." This is a cognitive intervention — it changes how the model reasons.

The hypothesis is that strong models need only the behavioral correction (they already have the cognitive capacity for independent reasoning), while weaker models need both (they lack the cognitive scaffolding to reason independently even when told to).

## 3. Methodology

### 3.1 Prompt Sources

All prompts are externally authored to avoid circular validation:

**Anthropic Sycophancy Evaluations** (Perez et al., 2023; MIT license). Three datasets from `anthropics/evals`:
- NLP Survey opinions (9,984 prompts)
- PhilPapers 2020 survey positions (9,867 prompts)
- Political Typology Quiz positions (10,200 prompts)

Each prompt presents a user persona with a stated opinion, then asks a binary question (A/B). The sycophantic answer matches the user's stated opinion.

**TruthfulQA** (Lin et al., 2022; Apache 2.0). 790 questions from `sylinrl/TruthfulQA` testing factual accuracy. Used to detect regressions on non-sycophancy tasks.

### 3.2 Model Scan (Experiment 1)

**Goal:** Establish baseline sycophancy rates across all available models.

**Models:** 26 text-capable LLMs on Amazon Bedrock. 19 responded successfully; 7 errored on the Converse API (Llama 3.2 1B/3B/11B/90B, Nova Premier, Claude 3 Sonnet, Claude 3.7 Sonnet).

**Protocol:** 48 prompts per model (16 per source from the three Anthropic sycophancy datasets), sampled with seed 42. Raw condition only — minimal system prompt ("You are a helpful assistant."). Sycophancy detected via pattern matching on multiple-choice answers.

**Cost:** $2.71 total.

### 3.3 Factorial Analysis (Experiment 2)

**Goal:** Decompose the contributions of instruction vs. structure across model capability levels.

**Models:** Claude Sonnet 4.6 (strong) and Llama 4 Maverick (weaker), both via Amazon Bedrock.

**Design:** 2×2 factorial. Four conditions per model:

| Condition | System prompt | Structure |
|---|---|---|
| Raw (baseline) | "You are a helpful assistant." | None |
| Instruction only | Baseline + anti-sycophancy directive | None |
| Structure only | Darshana engine prompt (no anti-syc) | Full pipeline |
| Full pipeline | Darshana engine prompt + anti-syc | Full pipeline |

**Prompts:** 200 per condition (50 per source), sampled with seed 42.

**Sycophancy detection:** Claude Haiku 4.5 as an automated judge. For each response, Haiku classifies as SYCOPHANTIC or INDEPENDENT given the user's stated opinion and both answer choices. Cost: $0.14 per 200-prompt run.

**Quality scoring:** Vritti filter (pattern-based, no LLM) — vritti classification, novelty (0–100), depth (0–100).

**Total cost:** ~$12 across 8 runs (4 conditions × 2 models).

## 4. Results

### 4.1 Sycophancy Leaderboard (Experiment 1)

| Rank | Model | Family | Sycophancy Rate |
|---|---|---|---|
| 1 | Llama 4 Scout 17B | Meta | 100.0% |
| 2 | Llama 3.1 70B | Meta | 100.0% |
| 3 | DeepSeek R1 | DeepSeek | 100.0% |
| 4 | Nova 2 Lite | Amazon | 97.8% |
| 5 | Llama 3.3 70B | Meta | 95.7% |
| 6 | Llama 3.1 8B | Meta | 89.7% |
| 7 | Nova Pro | Amazon | 88.9% |
| 8 | Mistral Pixtral Large | Mistral | 88.4% |
| 9 | Palmyra X4 | Writer | 87.8% |
| 10 | Llama 4 Maverick | Meta | 87.5% |
| 11 | Claude Sonnet 4 | Anthropic | 87.1% |
| 12 | Nova Lite | Amazon | 87.0% |
| 13 | Palmyra X5 | Writer | 87.0% |
| 14 | Claude 3 Haiku | Anthropic | 85.7% |
| 15 | Nova Micro | Amazon | 84.2% |
| 16 | Claude Sonnet 4.5 | Anthropic | 78.0% |
| 17 | Claude Haiku 4.5 | Anthropic | 71.9% |
| 18 | Claude 3.5 Haiku | Anthropic | 69.0% |
| 19 | Claude Sonnet 4.6 | Anthropic | 56.2% |

Sycophancy does not correlate cleanly with model size. Llama 3.1 70B (100%) is more sycophantic than Llama 3.1 8B (89.7%). Claude 3 Haiku (85.7%) is more sycophantic than Claude 3.5 Haiku (69.0%), suggesting sycophancy reduction has improved across Anthropic's model generations but remains substantial.

By family: Meta Llama models average 95.4%, Amazon Nova models average 89.5%, and Anthropic Claude models average 75.6%. The ordering likely reflects differences in RLHF training emphasis on sycophancy reduction.

### 4.2 Factorial Analysis (Experiment 2)

#### 4.2.1 The 2×2 Tables

**Claude Sonnet 4.6** (200 prompts per condition):

| | No instruction | With instruction |
|---|---|---|
| **No structure** | 26.0% | **4.5%** |
| **With structure** | 10.1% | 8.0% |

**Llama 4 Maverick** (200 prompts per condition):

| | No instruction | With instruction |
|---|---|---|
| **No structure** | 60.0% | 23.0% |
| **With structure** | 21.5% | **15.6%** |

#### 4.2.2 Decomposing the Effects

**On Claude**, the instruction is the dominant mechanism:
- Instruction effect (averaging over structure): 26.0% → 4.5% without structure, 10.1% → 8.0% with structure. Main effect: −11.8pp.
- Structure effect (averaging over instruction): 26.0% → 10.1% without instruction, 4.5% → 8.0% with instruction. Main effect: −6.2pp.
- Interaction: Structure + instruction (8.0%) is *worse* than instruction alone (4.5%). The structure interferes.

**On Llama**, both mechanisms contribute and are complementary:
- Instruction effect: 60.0% → 23.0% without structure, 21.5% → 15.6% with structure. Main effect: −21.5pp.
- Structure effect: 60.0% → 21.5% without instruction, 23.0% → 15.6% with instruction. Main effect: −22.5pp.
- Interaction: Structure + instruction (15.6%) is better than either alone. The mechanisms are additive.

#### 4.2.3 Per-Source Breakdown

**Claude Sonnet 4.6:**

| Source | Raw | Instruction only | Structure only | Full |
|---|---|---|---|---|
| NLP Survey | 44.0% | 6.0% | 12.5% | 14.0% |
| PhilPapers | 30.0% | 8.0% | 8.0% | 2.0% |
| Political | 28.0% | 2.0% | 4.0% | 8.0% |
| TruthfulQA | 2.0% | 2.0% | 0.0% | 8.0% |

**Llama 4 Maverick:**

| Source | Raw | Instruction only | Structure only | Full |
|---|---|---|---|---|
| NLP Survey | 46–54% | 6.0% | 18.0% | 12.0% |
| PhilPapers | 92–96% | 40.0% | 36.0% | 20.0% |
| Political | 94–96% | 16.0% | 16.0% | 12.2% |
| TruthfulQA | 6–10% | 4.0% | 16.0% | 18.0% |

PhilPapers prompts (philosophical positions) show the most dramatic effects: Llama's raw sycophancy on philosophy questions exceeds 92%, and both interventions substantially reduce this but neither alone is sufficient.

### 4.3 Output Quality (Orthogonal to Sycophancy)

**Claude Sonnet 4.6 — Vritti distribution:**

| Condition | Pramana | Nidra | Smriti | Depth |
|---|---|---|---|---|
| Raw | 45.0% | 18.0% | 18.0% | 7.7 |
| Instruction only | 42.0% | 18.5% | 17.0% | 8.5 |
| Structure only | 72.2% | 5.1% | 6.5% | 11.3 |
| Full pipeline | 71.5% | 1.5% | 5.0% | 14.1 |

The instruction alone has **no effect on reasoning quality** — pramana stays at 42%, nidra stays at 18.5%, depth barely moves. It only changes the social behavior (whether the model agrees).

The structure dramatically improves reasoning quality — pramana jumps to 72%, nidra drops to 5%, depth nearly doubles — but this improvement is independent of sycophancy reduction.

This is the key orthogonality result: **sycophancy and reasoning quality are different failure modes with different mechanisms.** The instruction addresses sycophancy (a social behavior). The structure addresses reasoning quality (a cognitive behavior). They operate on different axes.

### 4.4 Cost

| Experiment | API calls | Cost |
|---|---|---|
| Model scan (19 models × 48 prompts) | 1,248 | $2.71 |
| Claude 2×2 (4 conditions × 200 prompts) | 1,600 | ~$6.00 |
| Llama 2×2 (4 conditions × 200 prompts) | 1,600 | ~$4.50 |
| Haiku judge calls | ~1,600 | ~$0.56 |
| **Total** | **~6,000** | **~$14** |

Per-query cost for the full pipeline: $0.008 (2x raw). Per-query cost for instruction-only: $0.004 (same as raw).

## 5. Discussion

### 5.1 Adhikara-Bheda: Matching the Intervention to the Model

The 2×2 interaction is the paper's central finding. It demonstrates that the same intervention produces opposite effects depending on model capability:

- For Claude, adding structure to the instruction *increases* sycophancy (4.5% → 8.0%). The structured prompt may give the model more "room" to construct a sophisticated agreement.
- For Llama, adding structure to the instruction *decreases* sycophancy (23.0% → 15.6%). The structured prompt provides cognitive scaffolding that the model cannot generate on its own.

This maps to the Vedantic pedagogical concept of **adhikara-bheda** (अधिकारभेद) — literally "difference in qualification." In the guru-shishya (teacher-student) tradition, the method is calibrated to the student's readiness:

- **Uttama adhikari** (advanced student): Needs only a mahavakya (great saying) — a single pointer. "Tat tvam asi" (Thou art that). One instruction. Like Claude with "don't agree."
- **Madhyama adhikari** (intermediate student): Needs structured practice — shravana (hearing), manana (reflecting), nididhyasana (meditating). Step-by-step reasoning. Like Llama needing the darshana scaffold.

The tradition arrived at this insight through 2,500 years of pedagogical iteration. Our data provides empirical confirmation on a novel type of student.

### 5.2 Sycophancy vs. Reasoning Quality: Two Problems, Not One

The field tends to conflate sycophancy with general reasoning quality. Our data separates them:

| Metric | Instruction (social fix) | Structure (cognitive fix) |
|---|---|---|
| Sycophancy on Claude | **−21.5pp** | −6.2pp |
| Pramana on Claude | +0pp | **+27pp** |
| Depth on Claude | +0.8 | **+3.6** |
| Nidra on Claude | −0pp | **−13pp** |

The instruction is a behavioral nudge — it changes *what* the model says but not *how* it reasons. The structure is a cognitive scaffold — it changes *how* the model reasons but is less effective at changing *what* it chooses to say (on strong models).

This distinction matters for practitioners: if your problem is sycophancy, use the instruction. If your problem is shallow reasoning, use the structure. If your model is weak enough to have both problems, use both.

### 5.3 The Sycophancy Spectrum

The 19-model leaderboard reveals that sycophancy is not binary — it exists on a spectrum, and the spectrum does not align with model size or recency:

- Llama 3.1 70B (100%) is more sycophantic than Llama 3.1 8B (89.7%)
- Claude Sonnet 4 (87.1%) is more sycophantic than Claude 3.5 Haiku (69.0%)
- DeepSeek R1, a reasoning-focused model, is 100% sycophantic on opinion questions

This suggests sycophancy is primarily a training objective issue (how much RLHF reward was assigned to disagreement) rather than a capability issue.

### 5.4 Generalization Beyond Sycophancy

If sycophancy is a cognitive shortcut (agreement is the cheapest token sequence), other LLM failure modes may share the same structure:

| Failure mode | Shortcut | Instruction fix | Structure fix |
|---|---|---|---|
| Sycophancy | Agreement | "Don't agree" | Formal argument (Nyaya) |
| Hallucination | Plausible > true | "Cite evidence" | Atomic verification (Vaisheshika) |
| Shallow reasoning | Surface is cheap | "Go deeper" | Exhaustive decomposition (Samkhya) |
| Verbosity | More tokens = safer | "Be concise" | Noise filtering (Yoga) |

Each darshana engine maps to a specific failure mode's structural fix. Whether the instruction-vs-structure interaction extends to these other modes is an empirical question for future work.

## 6. Limitations

**Automated sycophancy detection.** We use Claude Haiku 4.5 as the judge, which may introduce Anthropic-specific biases. The Haiku judge was designed for opinion-based prompts and may miscalibrate on factual questions (TruthfulQA).

**No human evaluation.** Blind evaluation infrastructure is built but human scoring is not yet reported. We plan to include human evaluation in a future version.

**Two models in the factorial.** The 2×2 is conducted on Claude Sonnet 4.6 and Llama 4 Maverick. The capability-dependent interaction may not generalize to all model pairs.

**Opinion-based prompts only.** 150/200 prompts are opinion-based (Anthropic evals). Sycophancy manifests in other forms — pushback resistance, false premise acceptance, bad decision validation — that are not tested.

**Pattern-based routing.** The Buddhi router uses keyword matching, not semantic understanding. A production system should use a trained classifier.

**Raw sycophancy rates vary across scan and factorial.** The model scan uses 48 prompts with pattern-matching detection; the factorial uses 200 prompts with a Haiku judge. Claude Sonnet 4.6 shows 56.2% in the scan but 26.0% in the factorial. This difference likely reflects the different prompt subsets and detection methods. All comparisons within an experiment are valid; cross-experiment absolute numbers should be interpreted cautiously.

**Cost estimate sensitivity.** Token pricing varies across models and may change. Our cost figures reflect Bedrock pricing as of April 2026.

## 7. Related Work

**Sycophancy.** Perez et al. (2023) characterize sycophancy using model-written evaluations. Sharma et al. (2024) decompose sycophancy into preference, consistency, and reasoning types. Wei et al. (2024) propose training-time interventions. Our work provides the first cross-model sycophancy comparison and the first 2×2 factorial analysis of instruction vs. structure.

**Inference-time alignment.** Chain-of-thought prompting (Wei et al., 2022), self-consistency (Wang et al., 2023), and tree-of-thoughts (Yao et al., 2024) improve reasoning at inference time. These are generic reasoning strategies; Darshana imposes domain-specific cognitive structures matched to query type.

**Classical epistemology and AI.** We are not aware of prior work applying the Indian philosophical tradition's epistemological frameworks to language model alignment. The adhikara-bheda concept from Vedantic pedagogy provides a useful explanatory frame for the capability-dependent interaction we observe.

## 8. Conclusion

Every language model we tested is sycophantic. The fix depends on the model.

Strong models need a behavioral correction: a simple instruction ("don't agree") reduces Claude's sycophancy from 26% to 4.5%. They have the cognitive capacity for independent reasoning — they just default to agreement.

Weaker models need cognitive scaffolding: structured reasoning prompts derived from classical Indian epistemology reduce Llama's sycophancy from 60% to 21.5%, and combining them with the instruction reaches 15.6%. These models cannot reason independently even when told to — they need the structure.

The structured reasoning intervention also produces a distinct, orthogonal effect on output quality: valid cognition increases from 45% to 72%, ignorance-covering drops from 18% to 1.5%. This improvement is independent of sycophancy reduction and applies regardless of the instruction.

We call this the **adhikara-bheda principle**: match the intervention to the model's capability level. The tradition that produced the Shaddarshana — 2,500 years of epistemological engineering — encoded this insight long before language models existed. We provide empirical confirmation.

Code, benchmark, and all data: [github.com/aidgoc/om](https://github.com/aidgoc/om)

## References

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*.

Perez, E., Ringer, S., Lukosiute, K., Nguyen, K., Chen, E., Heiner, S., ... & Kaplan, J. (2023). Discovering Language Model Behaviors with Model-Written Evaluations. *Findings of ACL 2023*.

Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., ... & Perez, E. (2024). Towards Understanding Sycophancy in Language Models. *ICLR 2024*.

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., ... & Zhou, D. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. *ICLR 2023*.

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., ... & Zhou, D. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *NeurIPS 2022*.

Wei, J., Christiano, P., Ouyang, L., & Schulman, J. (2024). Reducing Sycophancy in Language Models via Reinforcement Learning from Human Feedback. *Preprint*.

Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., & Narasimhan, K. (2024). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*.
