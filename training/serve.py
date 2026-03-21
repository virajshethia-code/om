#!/usr/bin/env python3
"""
serve.py — Darshana Inference Server
=====================================

HTTP API for serving fine-tuned darshana models. Loads LoRA adapters on top
of a base model and exposes endpoints for reasoning, routing, and vritti
classification.

Usage:
    # Serve a single darshana
    python training/serve.py --darshana nyaya --adapter training/adapters/nyaya/ --port 8000

    # Serve all darshanas (auto-routing via Buddhi)
    python training/serve.py --all --port 8000

API:
    POST /think     {"query": "...", "darshana": "nyaya"}  -> reasoning response
    POST /route     {"query": "..."}                        -> routing decision
    POST /classify  {"text": "..."}                         -> vritti classification
    GET  /health                                            -> status

Architecture reference: THESIS.md — full Darshana pipeline.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# ---------------------------------------------------------------------------
# Add parent to path for imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.darshana_router import DarshanaRouter  # noqa: E402
from src.vritti_filter import VrittiFilter       # noqa: E402
from src.prompts import DARSHANA_PROMPTS         # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ADAPTERS_DIR = SCRIPT_DIR / "adapters"
DARSHANAS = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

# ---------------------------------------------------------------------------
# Model manager — loads base model + multiple LoRA adapters
# ---------------------------------------------------------------------------

class DarshanaModelManager:
    """
    Manages a base model with multiple LoRA adapters that can be swapped.

    Architecture mapping:
        - Base model   = the raw LLM (Prakriti — undifferentiated potential)
        - LoRA adapter = a darshana specialization (differentiated reasoning)
        - Adapter swap = Buddhi routing to the right engine
    """

    def __init__(self, base_model_name: str, adapter_paths: dict[str, Path]):
        """
        Args:
            base_model_name: HuggingFace model ID for the base.
            adapter_paths: {darshana_name: path_to_adapter_dir}
        """
        self.base_model_name = base_model_name
        self.adapter_paths = adapter_paths
        self.model = None
        self.tokenizer = None
        self.loaded_adapters: set[str] = set()
        self.active_adapter: Optional[str] = None

    def load(self) -> None:
        """Load the base model and all adapters."""
        print(f"Loading base model: {self.base_model_name}")

        quant_config = None
        if torch.cuda.is_available():
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            quantization_config=quant_config,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_name, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load first adapter to create PeftModel, then add the rest
        adapter_items = list(self.adapter_paths.items())
        if adapter_items:
            first_name, first_path = adapter_items[0]
            print(f"Loading adapter: {first_name} from {first_path}")
            self.model = PeftModel.from_pretrained(
                self.model, str(first_path), adapter_name=first_name
            )
            self.loaded_adapters.add(first_name)
            self.active_adapter = first_name

            for name, path in adapter_items[1:]:
                print(f"Loading adapter: {name} from {path}")
                self.model.load_adapter(str(path), adapter_name=name)
                self.loaded_adapters.add(name)

        print(f"Loaded {len(self.loaded_adapters)} adapters: {', '.join(self.loaded_adapters)}")

    def generate(self, prompt: str, darshana: Optional[str] = None,
                 system_prompt: str = "", max_new_tokens: int = 1536) -> str:
        """
        Generate a response, optionally switching to a specific adapter.

        Args:
            prompt: User query.
            darshana: Which adapter to use (None = base model without adapter).
            system_prompt: System prompt to prepend.
            max_new_tokens: Maximum tokens to generate.

        Returns:
            Generated text.
        """
        # Switch adapter if needed
        if darshana and darshana in self.loaded_adapters:
            if self.active_adapter != darshana:
                self.model.set_adapter(darshana)
                self.active_adapter = darshana
        elif darshana and darshana not in self.loaded_adapters:
            # No adapter for this darshana — use base model
            if hasattr(self.model, "disable_adapter_layers"):
                self.model.disable_adapter_layers()
                self.active_adapter = None

        # Build chat messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            text = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        # Re-enable adapter if we disabled it
        if self.active_adapter is None and self.loaded_adapters:
            if hasattr(self.model, "enable_adapter_layers"):
                self.model.enable_adapter_layers()

        return response.strip()


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

def create_app(
    model_manager: DarshanaModelManager,
    router: DarshanaRouter,
    vritti_filter: VrittiFilter,
) -> Flask:
    """Create the Flask application with all endpoints."""

    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "base_model": model_manager.base_model_name,
            "loaded_adapters": sorted(model_manager.loaded_adapters),
            "active_adapter": model_manager.active_adapter,
            "device": str(model_manager.model.device) if model_manager.model else "not loaded",
        })

    @app.route("/think", methods=["POST"])
    def think():
        """
        Main reasoning endpoint.

        Request:
            {"query": "...", "darshana": "nyaya"}  (darshana optional — auto-routed)
            {"query": "...", "guna": "rajas"}       (guna optional — auto-detected)

        Response:
            {"darshana": "nyaya", "response": "...", "routing": {...}, "vritti": {...}}
        """
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query = data["query"]
        darshana = data.get("darshana")
        guna = data.get("guna")

        start = time.time()

        # Route if no darshana specified
        routing_info = {}
        if not darshana:
            routing_result = router.route(query)
            darshana = routing_result.top_engines[0] if routing_result.top_engines else "nyaya"
            routing_info = {
                "selected": darshana,
                "scores": routing_result.engine_scores,
                "guna": routing_result.guna.value,
                "all_engines": routing_result.top_engines,
            }

        # Get system prompt for this darshana
        system_prompt = DARSHANA_PROMPTS.get(darshana, "")

        # Generate response
        response_text = model_manager.generate(
            prompt=query,
            darshana=darshana,
            system_prompt=system_prompt,
        )

        # Classify the output with vritti filter
        vritti_result = vritti_filter.classify(response_text, context=query)

        elapsed = time.time() - start

        return jsonify({
            "darshana": darshana,
            "response": response_text,
            "routing": routing_info,
            "vritti": {
                "classification": vritti_result.vritti.value,
                "confidence": vritti_result.confidence,
                "explanation": vritti_result.explanation,
            },
            "elapsed_seconds": round(elapsed, 2),
        })

    @app.route("/route", methods=["POST"])
    def route():
        """
        Routing-only endpoint (Buddhi layer).

        Request:  {"query": "..."}
        Response: {"engines": [...], "scores": {...}, "guna": "..."}
        """
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        result = router.route(data["query"])
        return jsonify({
            "engines": result.top_engines,
            "scores": result.engine_scores,
            "guna": result.guna.value,
        })

    @app.route("/classify", methods=["POST"])
    def classify():
        """
        Vritti classification endpoint.

        Request:  {"text": "...", "context": "..."}  (context optional)
        Response: {"vritti": "pramana", "confidence": 0.85, ...}
        """
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        result = vritti_filter.classify(
            data["text"], context=data.get("context")
        )

        # Also compute depth and novelty
        depth = vritti_filter.depth_test(
            data["text"], data.get("context", "")
        )
        novelty = vritti_filter.novelty_score(data["text"])

        return jsonify({
            "vritti": result.vritti.value,
            "confidence": result.confidence,
            "explanation": result.explanation,
            "depth_score": depth.score if hasattr(depth, "score") else int(depth),
            "novelty_score": novelty,
        })

    return app


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve fine-tuned darshana models via HTTP",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--darshana", type=str, choices=DARSHANAS,
                       help="Serve a single darshana")
    group.add_argument("--all", action="store_true",
                       help="Serve all available darshanas")

    parser.add_argument("--adapter", type=str, default=None,
                        help="Path to adapter (for single darshana mode)")
    parser.add_argument("--base-model", type=str,
                        default="meta-llama/Llama-3.2-3B-Instruct",
                        help="Base model name")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to serve on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind to (default: 0.0.0.0)")

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine which adapters to load
    adapter_paths: dict[str, Path] = {}

    if args.all:
        for darshana in DARSHANAS:
            adapter_dir = ADAPTERS_DIR / darshana
            if adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists():
                adapter_paths[darshana] = adapter_dir
            else:
                print(f"No adapter found for {darshana} at {adapter_dir}, skipping")

        # Also check for router and vritti adapters
        for special in ["router", "vritti"]:
            adapter_dir = ADAPTERS_DIR / special
            if adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists():
                adapter_paths[special] = adapter_dir

    elif args.darshana:
        adapter_dir = Path(args.adapter) if args.adapter else ADAPTERS_DIR / args.darshana
        if adapter_dir.exists():
            adapter_paths[args.darshana] = adapter_dir
        else:
            print(f"WARNING: No adapter at {adapter_dir}. Serving base model only.")

    if not adapter_paths:
        print("WARNING: No adapters found. Serving base model without specialization.")

    # Detect base model from adapter metadata if available
    base_model = args.base_model
    for path in adapter_paths.values():
        meta = path / "training_metadata.json"
        if meta.exists():
            with open(meta) as f:
                base_model = json.load(f).get("base_model", base_model)
            break

    # Initialize components
    model_manager = DarshanaModelManager(base_model, adapter_paths)
    model_manager.load()

    router_instance = DarshanaRouter()
    vritti_instance = VrittiFilter()

    # Create and run app
    app = create_app(model_manager, router_instance, vritti_instance)

    print(f"\nDarshana Inference Server")
    print(f"  Base model:  {base_model}")
    print(f"  Adapters:    {', '.join(adapter_paths.keys()) or 'none'}")
    print(f"  Endpoints:")
    print(f"    POST /think     — reasoning with auto-routing")
    print(f"    POST /route     — routing decision only")
    print(f"    POST /classify  — vritti classification")
    print(f"    GET  /health    — server status")
    print(f"\n  Listening on http://{args.host}:{args.port}")
    print()

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
