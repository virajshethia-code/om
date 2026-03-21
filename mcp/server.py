"""
Darshana MCP Server — Expose the Darshana Architecture via Model Context Protocol
==================================================================================

This MCP server exposes the six reasoning engines, vritti filter, and smriti
memory system as tools that any MCP-compatible client can use (Claude Desktop,
Claude Code, Cursor, etc.).

Transport: stdio (stdin/stdout)
SDK: Official MCP Python SDK (pip install mcp)

Usage:
    python /Users/harsh/om/mcp/server.py

Architecture reference: /Users/harsh/om/THESIS.md

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import Any

# IMPORTANT: Import the MCP SDK BEFORE adding project root to sys.path.
# The project has an mcp/ directory that would shadow the mcp package otherwise.
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
)

# Now add the project root to sys.path so we can import from src/
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Lazy-loaded modules — import on first use so the server starts fast
# and gracefully handles missing modules.
# ---------------------------------------------------------------------------

_router = None
_vritti_filter = None
_smriti = None
_prompts_module = None


def _get_router():
    global _router
    if _router is None:
        from src.darshana_router import DarshanaRouter
        _router = DarshanaRouter()
    return _router


def _get_vritti_filter():
    global _vritti_filter
    if _vritti_filter is None:
        from src.vritti_filter import VrittiFilter
        _vritti_filter = VrittiFilter()
    return _vritti_filter


def _get_smriti():
    global _smriti
    if _smriti is None:
        from src.smriti import Smriti
        _smriti = Smriti()  # default: ~/.darshana/smriti.db
    return _smriti


def _get_prompts():
    global _prompts_module
    if _prompts_module is None:
        from src import prompts as p
        _prompts_module = p
    return _prompts_module


# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

app = Server("darshana")

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="darshana_route",
        description=(
            "Route a query through the Buddhi (discriminative intelligence) layer. "
            "Returns which darshana engine(s) should handle this query, the recommended "
            "guna (processing mode: sattva/rajas/tamas), confidence scores for all six "
            "engines, and the routing reasoning."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query or problem to route.",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="darshana_think",
        description=(
            "Full reasoning through a specific darshana engine. Returns the darshana's "
            "structured reasoning approach, system prompt, and pramana (epistemic source) tag. "
            "If no darshana is specified, auto-routes to the best one."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query or problem to reason about.",
                },
                "darshana": {
                    "type": "string",
                    "description": (
                        "Which darshana engine to use. One of: nyaya, samkhya, yoga, "
                        "vedanta, mimamsa, vaisheshika. If omitted, auto-routes."
                    ),
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="darshana_think_multi",
        description=(
            "Yaksha Protocol — multi-darshana analysis. Runs the query through multiple "
            "reasoning engines for a multi-perspective analysis, then synthesizes using "
            "Vedanta's unification method. Returns perspectives, tensions, the Mahavakya "
            "(great reframing), and the real question."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query or problem to analyze from multiple perspectives.",
                },
                "max_engines": {
                    "type": "integer",
                    "description": "Maximum number of darshana engines to activate (default 3).",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="vritti_classify",
        description=(
            "Classify text quality using the five vrittis (mental modifications) from "
            "Yoga philosophy: pramana (valid cognition), viparyaya (misconception), "
            "vikalpa (verbal delusion), nidra (absence of knowledge), smriti (memory recall). "
            "Returns the vritti type, confidence, explanation, suggestions, and quality scores."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to classify.",
                },
                "context": {
                    "type": "string",
                    "description": "Optional grounding context (e.g., source docs or user query) to detect contradictions.",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="vritti_filter",
        description=(
            "Filter text and improve it based on vritti classification. Passes valid text through, "
            "prepends warnings for misconceptions and verbal delusions, replaces absent knowledge "
            "with honest 'I don't know', and flags recalled knowledge with recency caveats."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to filter.",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="smriti_store",
        description=(
            "Store a memory (samskara) in the persistent Smriti memory system. "
            "Memories are tagged with pramana (how it was learned) and source, "
            "and they decay over time based on recency and epistemic type."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The memory content — what was learned or observed.",
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Retrieval keywords. Auto-extracted if omitted.",
                },
                "pramana": {
                    "type": "string",
                    "description": "How this was learned: pratyaksha (direct), anumana (inferred), upamana (analogy), shabda (testimony). Default: shabda.",
                    "enum": ["pratyaksha", "anumana", "upamana", "shabda"],
                    "default": "shabda",
                },
                "source": {
                    "type": "string",
                    "description": "Where it came from: user_interaction, tool_output, inference, training, correction. Default: training.",
                    "enum": ["user_interaction", "tool_output", "inference", "training", "correction"],
                    "default": "training",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="smriti_recall",
        description=(
            "Recall relevant memories from the Smriti system. Uses keyword matching, "
            "recency weighting, confidence scoring, and access frequency to find the "
            "most relevant stored samskaras."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The retrieval query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of memories to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="smriti_context",
        description=(
            "Get memory-informed context for a query. Returns a formatted context string "
            "of relevant memories, ready to inject into an LLM prompt. Includes content, "
            "pramana type, confidence, domain, and age for each memory."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to find context for.",
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum approximate token count for the context (default 2000).",
                    "default": 2000,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="darshana_introspect",
        description=(
            "Self-model report (Ahamkara layer). Returns the system's knowledge about "
            "itself: memory count, domain breakdown, average confidence, active vasanas "
            "(accumulated tendencies), knowledge gaps, and guna state."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _serialize(obj: Any) -> Any:
    """Recursively convert dataclasses, enums, etc. to JSON-safe dicts."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        d = {}
        for k in obj.__dataclass_fields__:
            d[k] = _serialize(getattr(obj, k))
        return d
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "value"):  # Enum
        return obj.value
    return obj


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = _dispatch_tool(name, arguments)
        text = json.dumps(result, indent=2, ensure_ascii=False)
        return [TextContent(type="text", text=text)]
    except Exception as e:
        error_result = {"error": str(e), "tool": name}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


def _dispatch_tool(name: str, args: dict) -> dict:
    if name == "darshana_route":
        return _tool_darshana_route(args)
    elif name == "darshana_think":
        return _tool_darshana_think(args)
    elif name == "darshana_think_multi":
        return _tool_darshana_think_multi(args)
    elif name == "vritti_classify":
        return _tool_vritti_classify(args)
    elif name == "vritti_filter":
        return _tool_vritti_filter(args)
    elif name == "smriti_store":
        return _tool_smriti_store(args)
    elif name == "smriti_recall":
        return _tool_smriti_recall(args)
    elif name == "smriti_context":
        return _tool_smriti_context(args)
    elif name == "darshana_introspect":
        return _tool_darshana_introspect(args)
    else:
        return {"error": f"Unknown tool: {name}"}


# --- darshana_route ---

def _tool_darshana_route(args: dict) -> dict:
    query = args["query"]
    router = _get_router()
    result = router.route(query)
    explanation = router.explain_routing(result)

    return {
        "query": result.query,
        "recommended_darshanas": result.top_engines,
        "guna_mode": result.guna.value,
        "engine_scores": {k: round(v, 4) for k, v in result.engine_scores.items()},
        "depth_mode": result.decision.depth_mode if result.decision else "deep",
        "reasoning": result.decision.reasoning if result.decision else "",
        "explanation": explanation,
    }


# --- darshana_think ---

def _tool_darshana_think(args: dict) -> dict:
    query = args["query"]
    darshana_name = args.get("darshana")

    router = _get_router()
    prompts = _get_prompts()

    if darshana_name:
        # Validate the darshana name
        valid_names = list(router.engines.keys())
        if darshana_name.lower() not in valid_names:
            return {
                "error": f"Unknown darshana: {darshana_name}. Valid: {valid_names}",
            }
        darshana_name = darshana_name.lower()
        # Still get the guna from the router
        routing = router.route(query)
        guna = routing.guna.value
    else:
        # Auto-route
        routing = router.route(query)
        darshana_name = routing.top_engines[0] if routing.top_engines else "nyaya"
        guna = routing.guna.value

    # Get the engine's reasoning approach
    engine = router.engines[darshana_name]
    reasoning_output = engine.reason(query)

    # Get the full system prompt for this darshana
    system_prompt = prompts.get_darshana_prompt(darshana_name, guna)

    return {
        "darshana": darshana_name,
        "guna_mode": guna,
        "approach": reasoning_output.approach,
        "system_prompt": system_prompt,
        "pramana_tags": [_serialize(t) for t in reasoning_output.pramana_tags],
        "auto_routed": "darshana" not in args or args.get("darshana") is None,
        "engine_description": engine.description,
    }


# --- darshana_think_multi ---

def _tool_darshana_think_multi(args: dict) -> dict:
    query = args["query"]
    max_engines = args.get("max_engines", 3)

    router = _get_router()
    prompts = _get_prompts()

    # Route and get top engines
    routing = router.route(query)
    engines_to_use = routing.top_engines[:max_engines]

    # If only one engine activated, try to get at least 2 for multi-perspective
    if len(engines_to_use) < 2:
        sorted_engines = sorted(
            routing.engine_scores.items(), key=lambda x: x[1], reverse=True
        )
        engines_to_use = [name for name, _ in sorted_engines[:min(max_engines, 3)]]

    # Build multi-darshana prompt
    multi_prompt = prompts.build_multi_darshana_prompt(engines_to_use, routing.guna.value)

    # Get reasoning from each engine
    perspectives = []
    for engine_name in engines_to_use:
        engine = router.engines[engine_name]
        output = engine.reason(query)
        perspectives.append({
            "darshana": engine_name,
            "description": engine.description,
            "approach": output.approach,
            "pramana_tags": [_serialize(t) for t in output.pramana_tags],
        })

    return {
        "query": query,
        "engines_activated": engines_to_use,
        "guna_mode": routing.guna.value,
        "perspectives": perspectives,
        "multi_darshana_prompt": multi_prompt,
        "instructions": (
            "Use the multi_darshana_prompt as a system prompt. Feed the query to an LLM "
            "with this prompt to get the full multi-perspective analysis with Vedanta synthesis."
        ),
    }


# --- vritti_classify ---

def _tool_vritti_classify(args: dict) -> dict:
    text = args["text"]
    context = args.get("context")

    vf = _get_vritti_filter()
    result = vf.classify(text, context)

    # Also get novelty and depth scores
    novelty = vf.novelty_score(text)
    try:
        depth = vf.depth_score(text)
        depth_data = depth.to_dict() if hasattr(depth, "to_dict") else {"score": depth}
    except Exception:
        depth_data = {"score": "unavailable"}

    output = result.to_dict()
    output["novelty_score"] = novelty
    output["depth_score"] = depth_data
    return output


# --- vritti_filter ---

def _tool_vritti_filter(args: dict) -> dict:
    text = args["text"]

    vf = _get_vritti_filter()
    filtered = vf.filter(text)

    # Also return the classification for transparency
    classification = vf.classify(text)

    return {
        "filtered_text": filtered,
        "vritti_type": classification.vritti.value,
        "confidence": round(classification.confidence, 3),
        "was_modified": filtered != text,
    }


# --- smriti_store ---

def _tool_smriti_store(args: dict) -> dict:
    content = args["content"]
    keywords = args.get("keywords")
    pramana = args.get("pramana", "shabda")
    source = args.get("source", "training")

    smriti = _get_smriti()
    record = smriti.store(
        content=content,
        keywords=keywords,
        pramana=pramana,
        source=source,
    )

    return {
        "stored": True,
        "samskara_id": record.id,
        "content": record.content,
        "keywords": record.keywords,
        "pramana": record.pramana.value,
        "source": record.source.value,
        "confidence": record.confidence,
        "domain": record.domain,
    }


# --- smriti_recall ---

def _tool_smriti_recall(args: dict) -> dict:
    query = args["query"]
    limit = args.get("limit", 5)

    smriti = _get_smriti()
    results = smriti.recall(query, limit=limit)

    return {
        "query": query,
        "count": len(results),
        "memories": [
            {
                "samskara_id": r.id,
                "content": r.content,
                "keywords": r.keywords,
                "pramana": r.pramana.value,
                "confidence": round(r.confidence, 4),
                "source": r.source.value,
                "domain": r.domain,
                "age_days": round(r.age_days, 1),
                "access_count": r.access_count,
                "recency_score": round(r.recency_score, 4),
            }
            for r in results
        ],
    }


# --- smriti_context ---

def _tool_smriti_context(args: dict) -> dict:
    query = args["query"]
    max_tokens = args.get("max_tokens", 2000)

    smriti = _get_smriti()
    context = smriti.context_window(query, max_tokens=max_tokens)

    return {
        "query": query,
        "context": context,
        "max_tokens": max_tokens,
    }


# --- darshana_introspect ---

def _tool_darshana_introspect(args: dict) -> dict:
    smriti = _get_smriti()
    stats = smriti.stats()
    domains = smriti.domains()
    vasanas = smriti.vasana_engine.all_vasanas()

    return {
        "system": "Darshana Architecture",
        "version": "0.2.0",
        "memory": {
            "total_samskaras": stats.get("total_memories", 0),
            "by_pramana": stats.get("by_pramana", {}),
            "by_source": stats.get("by_source", {}),
            "by_domain": stats.get("by_domain", {}),
            "avg_confidence": stats.get("avg_confidence", 0.0),
            "oldest_age_days": stats.get("oldest_age_days"),
            "newest_age_days": stats.get("newest_age_days"),
            "total_retrievals": stats.get("total_retrievals", 0),
        },
        "domains": domains,
        "active_vasanas": [
            {
                "domain": v.domain,
                "tendency": v.tendency,
                "strength": round(v.strength, 4),
                "samskara_count": v.samskara_count,
            }
            for v in vasanas
        ],
        "engines": [
            "nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika",
        ],
        "guna_modes": ["sattva", "rajas", "tamas"],
        "db_path": smriti.db_path,
    }


# ---------------------------------------------------------------------------
# Resources — darshana prompts and curriculum content
# ---------------------------------------------------------------------------

DARSHANA_NAMES = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

# Curriculum paths — scan for markdown files in the om/ tree
CURRICULUM_DIRS = ["philosophy", "texts", "practices", "sanskrit", "connections"]


@app.list_resources()
async def list_resources() -> list[Resource]:
    resources = []

    # Darshana prompts
    for name in DARSHANA_NAMES:
        resources.append(
            Resource(
                uri=f"darshana://prompts/{name}",
                name=f"{name.capitalize()} System Prompt",
                description=f"The full system prompt for the {name.capitalize()} darshana reasoning engine.",
                mimeType="text/plain",
            )
        )

    # Curriculum lessons
    for subdir in CURRICULUM_DIRS:
        dir_path = Path(PROJECT_ROOT) / subdir
        if dir_path.is_dir():
            for md_file in sorted(dir_path.glob("*.md")):
                rel = f"{subdir}/{md_file.stem}"
                resources.append(
                    Resource(
                        uri=f"darshana://curriculum/{rel}",
                        name=md_file.stem.replace("-", " ").title(),
                        description=f"Curriculum lesson: {subdir}/{md_file.name}",
                        mimeType="text/markdown",
                    )
                )

    return resources


@app.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    return [
        ResourceTemplate(
            uriTemplate="darshana://prompts/{darshana_name}",
            name="Darshana System Prompt",
            description="Get the system prompt for any of the six darshana reasoning engines.",
        ),
        ResourceTemplate(
            uriTemplate="darshana://curriculum/{path}",
            name="Curriculum Content",
            description="Access curriculum lesson content by path (e.g., philosophy/04-nyaya-logic-and-epistemology).",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    uri_str = str(uri)

    # darshana://prompts/{name}
    if uri_str.startswith("darshana://prompts/"):
        name = uri_str.replace("darshana://prompts/", "").strip("/").lower()
        if name not in DARSHANA_NAMES:
            return f"Unknown darshana: {name}. Valid: {DARSHANA_NAMES}"
        prompts = _get_prompts()
        return prompts.get_darshana_prompt(name, "sattva")

    # darshana://curriculum/{path}
    if uri_str.startswith("darshana://curriculum/"):
        rel_path = uri_str.replace("darshana://curriculum/", "").strip("/")
        # Try with .md extension
        file_path = Path(PROJECT_ROOT) / f"{rel_path}.md"
        if file_path.is_file():
            return file_path.read_text(encoding="utf-8")
        # Try exact path
        file_path = Path(PROJECT_ROOT) / rel_path
        if file_path.is_file():
            return file_path.read_text(encoding="utf-8")
        return f"Curriculum file not found: {rel_path}"

    return f"Unknown resource URI: {uri_str}"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
