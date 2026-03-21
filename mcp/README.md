# Darshana MCP Server

MCP (Model Context Protocol) server that exposes the Darshana Architecture as tools any AI client can use.

## Prerequisites

```bash
pip install mcp
```

The server imports from `/Users/harsh/om/src/` — no additional setup needed.

## Quick Start

```bash
python3 /Users/harsh/om/mcp/server.py
```

The server uses stdio transport (reads from stdin, writes to stdout).

## Connecting Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "darshana": {
      "command": "python3",
      "args": ["/Users/harsh/om/mcp/server.py"],
      "env": {}
    }
  }
}
```

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "darshana": {
      "command": "python3",
      "args": ["/Users/harsh/om/mcp/server.py"],
      "env": {}
    }
  }
}
```

Or add to an agent-specific config in `~/mik/mcp-configs/`:

```json
{
  "mcpServers": {
    "darshana": {
      "command": "python3",
      "args": ["/Users/harsh/om/mcp/server.py"],
      "env": {}
    }
  }
}
```

### Other MCP Clients (Cursor, etc.)

Use stdio transport with `python3 /Users/harsh/om/mcp/server.py` as the command.

## Tools

| Tool | Description |
|------|-------------|
| `darshana_route` | Route a query through the Buddhi layer — get recommended engine(s), guna mode, confidence scores |
| `darshana_think` | Full reasoning through a specific darshana (or auto-routed) — get system prompt, approach, pramana tags |
| `darshana_think_multi` | Yaksha Protocol — multi-darshana analysis with Vedanta synthesis |
| `vritti_classify` | Classify text quality — pramana/viparyaya/vikalpa/nidra/smriti with scores |
| `vritti_filter` | Filter text based on vritti classification — warnings, corrections, honest "I don't know" |
| `smriti_store` | Store a memory (samskara) with pramana tagging |
| `smriti_recall` | Recall relevant memories ranked by keyword match, recency, and confidence |
| `smriti_context` | Get formatted memory context ready to inject into an LLM prompt |
| `darshana_introspect` | Self-model report — memory stats, vasanas, domains, knowledge gaps |

## Resources

| URI Pattern | Description |
|-------------|-------------|
| `darshana://prompts/{darshana_name}` | System prompt for any of the six darshanas |
| `darshana://curriculum/{path}` | Curriculum lesson content (e.g., `philosophy/04-nyaya-logic-and-epistemology`) |

## The Six Darshanas

| Engine | Cognitive Function |
|--------|-------------------|
| **Nyaya** | Formal logic, proof chains, fallacy detection |
| **Samkhya** | Decomposition, enumeration, layer mapping |
| **Yoga** | Noise filtering, focus, signal extraction |
| **Vedanta** | Contradiction resolution, unifying abstractions |
| **Mimamsa** | Text-to-action, intent parsing, command extraction |
| **Vaisheshika** | Atomic decomposition, type checking, ontology |

## Memory System (Smriti)

Memories are stored in `~/.darshana/smriti.db` (SQLite). Each memory (samskara) is tagged with:
- **Pramana** — how it was learned (pratyaksha/anumana/upamana/shabda)
- **Source** — where it came from (user_interaction/tool_output/inference/training/correction)
- **Confidence** — decays over time, strengthened by recall
- **Domain** — auto-detected topic area

Accumulated patterns become **vasanas** (tendencies) that the system can detect and report.

## Architecture

See `/Users/harsh/om/THESIS.md` for the full Darshana Architecture specification.
