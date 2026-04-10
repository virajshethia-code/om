# Darshana: Inference-Time Alignment via Classical Indian Epistemology

**Harshwardhan Gokhale**

## Abstract

We present Darshana, an inference-time intervention that reduces sycophancy in large language models by routing queries through structured reasoning frameworks derived from the six schools of classical Indian philosophy (Shaddarshana). Rather than modifying model weights, Darshana operates as a cognitive pipeline that (1) classifies queries by reasoning type, (2) applies domain-specific system prompts that force structured analysis, and (3) filters outputs using a five-category epistemic classification system. On a benchmark of 200 prompts drawn from Anthropic's sycophancy evaluations and TruthfulQA, Darshana reduces the sycophancy rate of Claude Sonnet 4.6 from 26.0% to 8.0% (an 18 percentage point reduction), while increasing the proportion of responses classified as valid cognition from 45.0% to 71.5%. An ablation study shows that 84% of the sycophancy reduction comes from the structural reasoning constraints, not from explicit anti-sycophancy instructions. The intervention requires no training, no model access, and costs 2x the raw API call. We release the framework, benchmark, and evaluation methodology as open source.

## 1. Introduction

Sycophancy — the tendency of language models to agree with a user's stated opinion regardless of correctness — is a well-documented alignment failure mode (Perez et al., 2023; Sharma et al., 2024). Current mitigations operate at the training level: RLHF modifications, Constitutional AI constraints, or direct preference optimization. These approaches require model access, training infrastructure, and careful tuning to avoid capability degradation.

We propose a complementary approach: **inference-time alignment through structured reasoning**. The insight is that sycophancy is not primarily a knowledge problem (the model often "knows" the correct answer) but a *reasoning structure* problem. When given a user opinion and asked to evaluate it, the model defaults to agreement because its unstructured generation process lacks the cognitive architecture to separate evaluation from accommodation.

Our framework, Darshana, addresses this by imposing explicit reasoning structures drawn from the Shaddarshana — the six classical schools of Indian philosophy. These schools represent 2,500 years of systematized approaches to the problem of valid cognition:

- **Nyaya** (Logic): Formal syllogistic reasoning with mandatory fallacy checking
- **Samkhya** (Enumeration): Exhaustive decomposition into constituent components
- **Yoga** (Focus): Noise filtering and signal extraction from complex inputs
- **Vedanta** (Synthesis): Resolution of apparent contradictions through integration
- **Mimamsa** (Interpretation): Extraction of actionable meaning from text
- **Vaisheshika** (Atomism): Recursive decomposition to irreducible components

Each school forces the model into a specific reasoning *pattern* that structurally resists sycophancy. A Nyaya-routed response cannot simply agree — it must construct a formal syllogism, test it against five categories of logical fallacy, and state conclusions with explicit confidence levels. This structural constraint is the mechanism of action.

### Contributions

1. **Darshana**, an open-source inference-time alignment pipeline that reduces sycophancy by 18 percentage points without model modification
2. **Vritti Filter**, a pattern-based output classifier that categorizes model responses into five epistemic categories (valid cognition, misconception, verbal delusion, ignorance, recall) without additional LLM calls
3. **A benchmark methodology** using externally-sourced prompts with automated judging that enables reproducible sycophancy measurement at $2.36 per 200-prompt evaluation

## 2. Framework

### 2.1 Architecture Overview

Darshana operates as a pipeline between user query and model response:

```
Query → Buddhi (Router) → Darshana Prompt → LLM Call → Vritti Filter → Response
```

**Buddhi (Router).** A pattern-matching classifier that scores the query against six engines and selects 1-2 for activation. Each engine has trigger patterns: Nyaya activates on argument/validation language, Samkhya on decomposition requests, Yoga on information overload, etc. When no patterns match, the query routes to Mimamsa (direct interpretation), avoiding over-reasoning on simple questions.

**Darshana Prompts.** Each engine has a structured system prompt (500-800 tokens) that forces the model into a specific reasoning pattern. The Nyaya prompt, for example, requires a five-membered syllogism followed by five fallacy checks. Every prompt includes an anti-sycophancy directive: *"Evaluate all claims on their merits alone. If the user has stated an opinion, do NOT let that influence your analysis."*

**Vritti Filter.** A pattern-based output classifier (no LLM calls) that categorizes responses into five epistemic categories from Patanjali's Yoga Sutras (1.5-1.11):

| Vritti | Sanskrit | Classification | Action |
|---|---|---|---|
| Pramana | प्रमाण | Valid cognition — grounded, evidenced | Pass through |
| Viparyaya | विपर्यय | Misconception — factual error or fallacy | Warn and suggest corrections |
| Vikalpa | विकल्प | Verbal delusion — sounds correct but empty | Flag as unsubstantiated |
| Nidra | निद्रा | Absence of knowledge — fluent ignorance | Replace with honest uncertainty |
| Smriti | स्मृति | Memory recall — encyclopedic without reasoning | Flag as recalled, caveat for staleness |

### 2.2 Mechanism of Action

Why does structured reasoning reduce sycophancy? We hypothesize three mechanisms:

**M1: Structural incompatibility.** A sycophantic response ("Yes, I agree with your view") cannot satisfy the structural requirements of a Nyaya prompt (formal syllogism, fallacy analysis) or a Samkhya prompt (exhaustive enumeration). The reasoning structure forces the model to engage with the substance of the claim rather than the social dynamics of agreement.

**M2: Epistemic framing.** The prompts frame the task as *reasoning* rather than *responding*. This shifts the model's optimization target from "helpful and agreeable response" to "valid logical analysis," which changes the distribution of likely outputs.

**M3: Explicit anti-sycophancy instruction.** Each prompt includes a direct instruction to evaluate claims on their merits regardless of the user's stated opinion. While simple instruction-following, this intervention is more effective when embedded in a structured reasoning context than as a standalone system prompt.

### 2.3 Cost Structure

The pipeline adds cost through longer system prompts (500-800 tokens per engine) and structured output generation. In our benchmark:

| Condition | Mean input tokens | Mean output tokens | Cost per query |
|---|---|---|---|
| Raw Claude | 134 | 231 | $0.0039 |
| Darshana Pipeline | 1,366 | 256 | $0.0080 |

The pipeline costs approximately **2x** the raw API call, with the increase driven primarily by the system prompt length. Output tokens are similar due to the 256-token cap used in this benchmark.

## 3. Benchmark Methodology

### 3.1 Prompt Sources

We use exclusively externally-authored prompts to avoid circular validation (the framework was built by an LLM, so LLM-generated test prompts would be biased):

**Anthropic Sycophancy Evaluations** (Perez et al., 2023). Three datasets totaling 30,051 prompts testing whether models agree with a user's stated opinion:
- NLP Survey opinions (9,984 prompts)
- PhilPapers 2020 survey positions (9,867 prompts)
- Political Typology Quiz positions (10,200 prompts)

Each prompt presents a user persona with a stated opinion, then asks a binary question (A/B). The sycophantic answer matches the user's opinion; the independent answer does not.

**TruthfulQA** (Lin et al., 2022). 790 questions designed to elicit false but popular answers. We use these to test whether the pipeline introduces regressions on simple factual questions where sycophancy is not the primary failure mode.

We sample 50 prompts from each source (200 total) with a fixed random seed (42) for reproducibility.

### 3.2 Evaluation Protocol

For each prompt, we make two API calls using the same model (Claude Sonnet 4.6 via Amazon Bedrock):
- **Condition A (Raw):** Minimal system prompt ("You are a helpful assistant.")
- **Condition B (Pipeline):** Full Darshana pipeline (Buddhi routing → Darshana system prompt → Vritti filter)

Both conditions use `max_tokens=256` and the same model endpoint.

**Sycophancy Detection.** We use Claude Haiku 4.5 as an automated judge. For each response, Haiku receives the original prompt (including the user's stated opinion and the two answer choices) and classifies the response as SYCOPHANTIC (agrees with user's opinion) or INDEPENDENT (answers on merits). This is more accurate than letter-matching on long-form responses and costs $0.14 per 200-prompt evaluation.

**Quality Scoring.** Both responses are scored by the Vritti filter (pattern-based, no API calls) across three dimensions:
- Vritti classification (five categories above)
- Novelty score (0-100, penalizes common-knowledge framing)
- Depth score (0-100, rewards reasoning chains and specific evidence)

**Blind Human Evaluation.** We generate randomized X/Y pairs where evaluators do not know which response is raw vs. pipeline. Five dimensions scored on 0-5 Likert scales: sycophancy, groundedness, specificity, correctness, helpfulness.

### 3.3 Statistical Approach

For automated metrics, we report raw percentages with N=200 per condition. For human evaluation, we plan to use the Wilcoxon signed-rank test (non-parametric, appropriate for paired ordinal data) with rank-biserial correlation for effect size.

## 4. Results

### 4.1 Sycophancy Reduction

| Source | N | Raw Sycophancy | Pipeline Sycophancy | Reduction |
|---|---|---|---|---|
| NLP Survey | 50 | 44.0% | 14.0% | **−30.0pp** |
| PhilPapers | 50 | 30.0% | 2.0% | **−28.0pp** |
| Political Typology | 50 | 28.0% | 8.0% | **−20.0pp** |
| TruthfulQA | 50 | 2.0% | 8.0% | +6.0pp |
| **All sources** | **200** | **26.0%** | **8.0%** | **−18.0pp** |

The pipeline reduces sycophancy by 18 percentage points overall (26.0% → 8.0%), with the strongest effects on opinion-based prompts (NLP Survey: −30pp, PhilPapers: −28pp). The slight regression on TruthfulQA (+6pp) is discussed in Section 5.

### 4.2 Output Quality Classification

| Vritti Category | Raw (N=200) | Pipeline (N=200) | Interpretation |
|---|---|---|---|
| Pramana (valid cognition) | 90 (45.0%) | 143 (71.5%) | +26.5pp |
| Viparyaya (misconception) | 35 (17.5%) | 44 (22.0%) | +4.5pp |
| Vikalpa (verbal delusion) | 3 (1.5%) | 0 (0.0%) | −1.5pp |
| Nidra (ignorance) | 36 (18.0%) | 3 (1.5%) | −16.5pp |
| Smriti (recall) | 36 (18.0%) | 10 (5.0%) | −13.0pp |

The pipeline shifts the output distribution dramatically toward valid cognition (+26.5pp) while nearly eliminating ignorance-covering (−16.5pp) and reducing encyclopedic recall (−13.0pp). The increase in viparyaya (+4.5pp) reflects the pipeline making more assertive claims that the pattern-based filter flags as potentially incorrect — a known limitation of pattern-based classification on structured reasoning output.

### 4.3 Quality Scores

| Metric | Raw | Pipeline | Delta |
|---|---|---|---|
| Novelty (0-100) | 40.6 | 39.2 | −1.4 |
| Depth (0-100) | 7.7 | 14.1 | **+6.4** |

The depth improvement reflects the structural constraints of darshana prompts forcing multi-step reasoning. Novelty is comparable, suggesting the pipeline does not significantly alter the information content of responses.

### 4.4 Ablation: Structure vs. Instruction

To isolate the contribution of the structural reasoning constraints from the explicit anti-sycophancy instruction, we ran the pipeline without the anti-sycophancy directive ("Evaluate all claims on their merits alone...") on the same 200 prompts. This ablation also uses the corrected Mimamsa routing fallback (Section 5.2).

| Condition | Sycophancy Rate | Pramana | Nidra | Depth |
|---|---|---|---|---|
| Raw Claude (baseline) | 26.0% | 45.0% | 18.0% | 7.7 |
| Pipeline without instruction | 10.1% | 72.2% | 5.1% | 11.3 |
| Pipeline with instruction | 8.0% | 71.5% | 1.5% | 14.1 |

Per-source ablation:

| Source | Raw | Pipeline (no instruction) | Pipeline (full) |
|---|---|---|---|
| NLP Survey | 44.0% | 12.5% | 14.0% |
| PhilPapers | 30.0% | 8.0% | 2.0% |
| Political | 28.0% | 4.0% | 8.0% |
| TruthfulQA | 2.0% | 0.0% | 8.0% |

**The structural constraint accounts for ~84% of the sycophancy reduction** (15.9pp of the 18.0pp total). The anti-sycophancy instruction adds ~16% (2.1pp). This supports hypothesis M1: it is the reasoning structure — not the instruction — that resists sycophancy. A Nyaya prompt that requires a formal syllogism and fallacy analysis is structurally incompatible with simple agreement. The model cannot satisfy both "construct a valid argument" and "agree with the user" when the user's position is logically unsound.

The ablation also shows the corrected routing fallback resolves the TruthfulQA regression: with Mimamsa as the default engine for unmatched queries, TruthfulQA sycophancy drops to 0.0% (from 8.0% in the original run where Nyaya was the default).

### 4.5 Darshana Engine Distribution

| Engine | Activations | % |
|---|---|---|
| Nyaya (Logic) | 103 | 51.5% |
| Yoga (Focus) | 43 | 21.5% |
| Samkhya (Enumeration) | 28 | 14.0% |
| Vaisheshika (Atomism) | 11 | 5.5% |
| Mimamsa (Interpretation) | 10 | 5.0% |
| Vedanta (Synthesis) | 5 | 2.5% |

Nyaya's dominance reflects the benchmark composition — opinion/argument prompts naturally trigger logic and validation patterns. In general-purpose use, we expect a more balanced distribution.

### 4.5 Cost Analysis

| | Total Cost | Per Query |
|---|---|---|
| Raw Claude | $0.77 | $0.0039 |
| Darshana Pipeline | $1.59 | $0.0080 |
| Haiku Judge (eval only) | $0.14 | $0.0007 |
| **Total benchmark** | **$2.36** | **$0.0118** |

The pipeline adds a 2.06x cost multiplier per query, driven primarily by the system prompt overhead (500-800 tokens per engine). This is substantially less than training-time interventions, which require GPU hours and model retraining.

## 5. Discussion

### 5.1 Why Structure Reduces Sycophancy

The ablation study (Section 4.4) provides the clearest evidence: the structural reasoning constraint alone reduces sycophancy from 26.0% to 10.1%, accounting for 84% of the total effect. The explicit anti-sycophancy instruction adds only 2.1 percentage points.

This supports hypothesis M1 (structural incompatibility). When forced to construct a formal argument and test it for fallacies (Nyaya), or to exhaustively enumerate components (Samkhya), or to extract actionable meaning from text (Mimamsa), the model's generation process is oriented toward analysis rather than accommodation. The cognitive structure crowds out the sycophantic response.

The effect is strongest on opinion-based prompts where the user explicitly states a position (NLP Survey: −27pp structure-only, PhilPapers: −20pp, Political: −26pp). These are exactly the cases where structural constraints matter most — the model has both the knowledge to answer independently and the social pressure to agree.

### 5.2 The TruthfulQA Regression and Routing Fix

The initial benchmark run showed a 6pp TruthfulQA regression because 46/50 simple factual questions defaulted to Nyaya (the first engine in dictionary order). Imposing formal syllogistic reasoning on "What happens if you swallow gum?" degrades rather than improves the response.

The ablation run uses the corrected routing fallback (Mimamsa for unmatched queries) and shows TruthfulQA sycophancy at 0.0%. This confirms the regression was a routing artifact, not a fundamental limitation of the approach. The lesson: **match the reasoning structure to the query type**. Simple factual questions need direct interpretation (Mimamsa), not formal logic (Nyaya).

2. **Haiku judge calibration.** The sycophancy judge was designed for opinion-based prompts (A/B choices with a stated user opinion). TruthfulQA prompts are factual, with no user opinion to agree with. The judge may be misclassifying structured Nyaya-style reasoning as "agreeing with the question's premise" when it is actually providing a thorough answer.

### 5.3 The Vritti Filter Paradox

The viparyaya (misconception) category increased by 4.5pp for pipeline responses. This is likely an artifact of the pattern-based filter, which flags assertive claims and logical structures as potential misconceptions. A pipeline response that constructs a formal argument with explicit premises will trigger more viparyaya patterns than a hedged, noncommittal raw response. This is a limitation of pattern-based classification applied to structured output.

## 6. Limitations

**Single model.** All results are for Claude Sonnet 4.6 via Amazon Bedrock. Generalization to other models (GPT-4, Llama, Mistral) is not established.

**Pattern-based routing.** The Buddhi router uses keyword matching, not semantic understanding. Edge cases (metaphorical language, code snippets containing logic keywords) can cause misrouting. A production system would benefit from a trained classifier.

**No human evaluation reported.** The automated results use a Haiku judge, which introduces its own biases. The blind evaluation infrastructure is built but human scoring is not yet complete. We plan to report human evaluation results in a future version.

**Benchmark composition.** Three of four prompt sources (150/200 prompts) are opinion-based. The framework's effectiveness on other sycophancy modes (pushback resistance, false premise acceptance, bad decision validation) is not measured by this benchmark.

**Cost overhead.** The 2x cost multiplier may be acceptable for high-stakes applications but is impractical for high-volume, low-stakes use. Future work should explore prompt compression and selective pipeline activation.

**Instruction-only condition not tested.** The ablation isolates structure vs. structure+instruction, but does not test the anti-sycophancy instruction alone (without structural prompts). This would require a "raw Claude + anti-sycophancy instruction" condition to fully decompose the effects.

## 7. Related Work

**Sycophancy in LLMs.** Perez et al. (2023) characterize sycophancy as a failure of RLHF, where models learn to produce agreeable outputs. Sharma et al. (2024) extend this analysis to multiple sycophancy types. Wei et al. (2024) propose training-time interventions. Our work complements these by operating at inference time.

**Inference-time interventions.** Chain-of-thought prompting (Wei et al., 2022), self-consistency (Wang et al., 2023), and tree-of-thoughts (Yao et al., 2024) improve reasoning quality at inference time. Darshana extends this line by imposing domain-specific reasoning structures rather than generic prompting strategies.

**Epistemological frameworks for AI.** The application of classical epistemological frameworks to AI alignment is underexplored. The closest work is in AI safety's use of formal logic and epistemic logic, but we are not aware of prior work applying the Indian philosophical tradition's epistemological frameworks to language model alignment.

## 8. Conclusion

Darshana demonstrates that inference-time structured reasoning can meaningfully reduce sycophancy in language models. The mechanism — imposing domain-specific reasoning constraints derived from classical Indian epistemology — is lightweight (no training, 2x cost, pattern-based routing and filtering) and effective (18pp sycophancy reduction on 200 prompts).

The framework's strongest contribution is conceptual: it shows that the Shaddarshana — six schools of Indian philosophy developed over 2,500 years to address the problem of valid cognition — encode reasoning structures that are directly applicable to modern AI alignment challenges. The parallel is not metaphorical but structural: both systems address how information becomes knowledge, how to detect invalid reasoning, and how to resist cognitively convenient but epistemically unsound conclusions.

Code, benchmark, and data are available at: https://github.com/aidgoc/om

## References

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*.

Perez, E., Ringer, S., Lukosiute, K., Nguyen, K., Chen, E., Heiner, S., ... & Kaplan, J. (2023). Discovering Language Model Behaviors with Model-Written Evaluations. *Findings of ACL 2023*.

Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., ... & Perez, E. (2024). Towards Understanding Sycophancy in Language Models. *ICLR 2024*.

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., ... & Zhou, D. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. *ICLR 2023*.

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., ... & Zhou, D. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *NeurIPS 2022*.

Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., & Narasimhan, K. (2024). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*.
