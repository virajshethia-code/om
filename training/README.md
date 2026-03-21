# Darshana Fine-Tuning Pipeline

Fine-tune open-source LLMs into specialized reasoning engines using LoRA adapters, one per darshana school. This is the bridge from philosophy to neural networks.

## What Gets Built

| Adapter | Purpose | Training Data |
|---|---|---|
| `nyaya/` | Formal logic, syllogisms, fallacy detection | `nyaya_train.jsonl` |
| `samkhya/` | Exhaustive enumeration, causal chain mapping | `samkhya_train.jsonl` |
| `yoga/` | Attention filtering, signal/noise optimization | `yoga_train.jsonl` |
| `vedanta/` | Contradiction resolution, unifying abstractions | `vedanta_train.jsonl` |
| `mimamsa/` | Text-to-action extraction, command parsing | `mimamsa_train.jsonl` |
| `vaisheshika/` | Atomic decomposition, type systems | `vaisheshika_train.jsonl` |
| `router/` | Buddhi layer: routes queries to the right engine | `router_train.jsonl` |
| `vritti_reward/` | Classifies output quality on the 5 vritti types | `vritti_train.jsonl` |

## Hardware Requirements

| Base Model | VRAM (4-bit) | VRAM (Training) | Recommended GPU |
|---|---|---|---|
| Llama 3.2 3B | ~4 GB | ~6 GB | RTX 3060 12GB, T4 |
| Mistral 7B / Qwen 2.5 7B | ~6 GB | ~10 GB | RTX 3090 24GB, A10 |
| Llama 3.2 8B | ~7 GB | ~12 GB | RTX 4090 24GB, A10G |
| 13B models | ~10 GB | ~18 GB | A100 40GB |

Apple Silicon Macs (M1/M2/M3) work but are slower. bitsandbytes 4-bit quantization requires CUDA; MPS falls back to fp16.

## Quick Start

### 1. Install dependencies

```bash
pip install -r training/requirements.txt
```

### 2. Generate training data

```bash
# Generate all datasets (180 darshana + 100 router + 50 vritti examples)
python training/generate_data.py

# Validate generated JSONL
python training/generate_data.py --validate

# Print statistics (counts, token estimates, domain coverage)
python training/generate_data.py --stats
```

This generates chat-format JSONL files in `training/data/`:

```json
{"messages": [
    {"role": "system", "content": "<darshana system prompt>"},
    {"role": "user", "content": "<query>"},
    {"role": "assistant", "content": "<structured reasoning output>"}
]}
```

Example content lives in `training/examples/` with one module per darshana. Each example follows the darshana's exact method structure with 300-800 word responses covering 10 domains (software engineering, business strategy, scientific analysis, personal decisions, debugging, ethics, project planning, legal, creative, education).

### 3. Fine-tune

```bash
# Single darshana
python training/finetune.py --darshana nyaya --base-model meta-llama/Llama-3.2-3B-Instruct

# All six
python training/finetune.py --all --base-model meta-llama/Llama-3.2-3B-Instruct

# Router (Buddhi layer)
python training/finetune.py --router --base-model meta-llama/Llama-3.2-3B-Instruct

# Vritti classifier
python training/finetune.py --vritti --base-model meta-llama/Llama-3.2-3B-Instruct

# Custom hyperparameters
python training/finetune.py --darshana nyaya --epochs 5 --lr 1e-4 --lora-rank 32

# Resume from checkpoint
python training/finetune.py --darshana nyaya --resume training/adapters/nyaya/checkpoint-400
```

### 4. Evaluate

```bash
# Single adapter
python training/evaluate.py --adapter training/adapters/nyaya/ \
    --test-data training/data/nyaya_test.jsonl

# Side-by-side comparison (base vs fine-tuned)
python training/evaluate.py --adapter training/adapters/nyaya/ \
    --test-data training/data/nyaya_test.jsonl --compare

# All adapters
python training/evaluate.py --all
```

### 5. Train the vritti reward model

```bash
python training/reward_model.py --train --data training/data/vritti_train.jsonl
```

### 6. Serve

```bash
# Single darshana
python training/serve.py --darshana nyaya --port 8000

# All darshanas with auto-routing
python training/serve.py --all --port 8000
```

## API Endpoints

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/think` | POST | `{"query": "...", "darshana": "nyaya"}` | Reasoning response with vritti classification |
| `/route` | POST | `{"query": "..."}` | Routing decision (which darshana) |
| `/classify` | POST | `{"text": "..."}` | Vritti classification + depth/novelty scores |
| `/health` | GET | — | Server status |

The `darshana` field in `/think` is optional. If omitted, the Buddhi router selects the best engine automatically.

## Choosing a Base Model

**Llama 3.2 3B-Instruct** is the recommended starting point:
- Fits on consumer GPUs (6 GB VRAM for training)
- Fast iteration (8 min/epoch for 1k examples)
- Good instruction following out of the box
- The darshana prompts are heavily structured, so even 3B can learn the patterns

**Scale up to 7B/8B** when:
- You have 24+ GB VRAM
- You need better reasoning depth (especially for Nyaya and Vedanta)
- Training data exceeds 5k examples per darshana

**Mistral 7B vs Qwen 2.5 7B**: Mistral is slightly better at logical reasoning (good for Nyaya); Qwen handles multilingual content better if your training data includes Sanskrit terms.

## Expected Training Times (A100 40GB)

| Model | Examples | Epochs | Time |
|---|---|---|---|
| 3B | 500 | 3 | ~12 min |
| 3B | 2,000 | 3 | ~48 min |
| 7B | 500 | 3 | ~27 min |
| 7B | 2,000 | 3 | ~108 min |

## Cost Estimates (Cloud GPU)

| Provider | GPU | Cost/hr | 3B x 3 epochs (2k) | 7B x 3 epochs (2k) |
|---|---|---|---|---|
| Lambda | A100 40GB | ~$1.10/hr | ~$0.90 | ~$2.00 |
| RunPod | A100 40GB | ~$1.20/hr | ~$1.00 | ~$2.20 |
| HF Spaces | A10G | ~$1.00/hr | ~$1.00 | ~$2.50 |
| Vast.ai | RTX 4090 | ~$0.40/hr | ~$0.50 | ~$1.00 |

Training all 6 darshanas + router + vritti on 2k examples each at 3B: roughly $8-12 total.

## Using Adapters with the Main Architecture

The adapters integrate with the existing `src/` codebase. The serve.py server loads them onto a base model and exposes the same routing/filtering pipeline:

1. Query arrives
2. **Buddhi** (DarshanaRouter or router adapter) selects the engine
3. **LoRA adapter** activates for the selected darshana
4. Model generates with the darshana's system prompt
5. **Vritti filter** (or vritti reward model) classifies the output
6. Response returned with classification metadata

For programmatic use without the server:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base + adapter
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
model = PeftModel.from_pretrained(model, "training/adapters/nyaya/")

# Generate with the Nyaya system prompt
from src.prompts import DARSHANA_PROMPTS
system_prompt = DARSHANA_PROMPTS["nyaya"]
```

## Configuration

All defaults live in `training/config.yaml`. Override via CLI flags or edit the YAML directly.

Key settings:
- `lora.rank`: Higher = more capacity, more VRAM. 16 is a good default; 32 for complex darshanas.
- `lora.alpha`: Usually 2x the rank. Controls the learning rate scaling of LoRA.
- `training.max_length`: 2048 is sufficient for most darshana outputs. Increase for Samkhya (long enumerations).
- `training.gradient_accumulation_steps`: Increase if you need to reduce batch_size for VRAM.

## The Vritti Reward Model

This is the novel piece. Instead of human preference labels, the reward model scores outputs on an epistemological scale:

| Vritti | Reward | Meaning |
|---|---|---|
| Pramana | +1.0 | Valid cognition grounded in evidence |
| Smriti | +0.2 | Correct recall, but not fresh reasoning |
| Nidra | 0.0 | Honest "I don't know" — not penalized |
| Vikalpa | -0.8 | Sounds right but means nothing |
| Viparyaya | -1.0 | Factual error or logical fallacy |

The key insight: **nidra (absence) gets zero reward, not negative**. A system that admits ignorance is epistemically healthier than one that generates confident nonsense. This is Patanjali's contribution to RLHF.
