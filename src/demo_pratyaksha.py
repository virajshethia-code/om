#!/usr/bin/env python3
"""
demo_pratyaksha.py -- Demonstration of the Pratyaksha Perception Layer
======================================================================

Shows the five Jnanendriyas (sense organs) in action:

    1. Chakshu (eye)   -- FileReader reads a Python file, extracts structure
    2. Ghrana (nose)    -- EnvironmentSniffer detects the om/ project
    3. Tvak (skin)      -- ShellSensor gets git status
    4. Manas (mind)     -- Routes a query to the right senses automatically
    5. PerceptionBundle -- Combines multiple perceptions into context

Run from the om/ directory:
    python -m src.demo_pratyaksha

Or directly:
    python src/demo_pratyaksha.py

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import json
import os
import sys

# Ensure the parent directory is on the path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pratyaksha import (
    Chakshu,
    Ghrana,
    Manas,
    Perception,
    PerceptionBundle,
    Shrotra,
    Tvak,
    Rasana,
    IndriyaType,
    KarmendriyaType,
    Vak,
    Pani,
    Pada,
    Payu,
    Upastha,
    create_manas,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def separator(title: str):
    """Print a section separator."""
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def print_perception(p: Perception, verbose: bool = False):
    """Pretty-print a Perception object."""
    status = "OK" if p.success else f"FAIL: {p.error}"
    print(f"  Source:      {p.source.value} ({p.pramana})")
    print(f"  Status:      {status}")
    print(f"  Confidence:  {p.confidence}")
    print(f"  Timestamp:   {p.timestamp}")
    print(f"  Freshness:   {p.freshness_seconds:.3f}s")
    print(f"  Query:       {p.query}")

    if p.metadata:
        print(f"  Metadata:    {json.dumps(p.metadata, indent=2, default=str)[:500]}")

    if p.success and p.content is not None:
        content_str = p.content if isinstance(p.content, str) else json.dumps(
            p.content, indent=2, default=str
        )
        # Truncate for display
        if len(content_str) > 800:
            content_str = content_str[:800] + "\n  ... (truncated)"
        print(f"  Content:")
        for line in content_str.splitlines()[:25]:
            print(f"    {line}")


# ---------------------------------------------------------------------------
# Demo 1: Chakshu (Eye) -- FileReader
# ---------------------------------------------------------------------------

def demo_chakshu():
    separator("DEMO 1: Chakshu (Eye) -- FileReader")
    print("Reading this project's darshana_router.py to extract code structure.\n")

    eye = Chakshu()
    print(f"  Available: {eye.available()}")
    print()

    # Read a Python file with structure extraction
    target = os.path.join(os.path.dirname(__file__), "darshana_router.py")
    perception = eye.perceive(target, parse_structure=True)

    print_perception(perception)

    # Show the extracted structure
    if perception.success and "structure" in perception.metadata:
        structure = perception.metadata["structure"]
        print()
        print("  Extracted Python Structure:")
        print(f"    Imports:      {len(structure.get('imports', []))} lines")
        print(f"    Classes:      {[c['name'] for c in structure.get('classes', [])]}")
        print(f"    Functions:    {len(structure.get('functions', []))} total")
        print(f"    Global vars:  {structure.get('global_vars', [])}")

        # Show first few classes
        for cls in structure.get("classes", [])[:5]:
            print(f"      class {cls['name']}({cls['bases']})")

    # Also demonstrate reading a directory
    print()
    print("  --- Directory perception ---")
    dir_perception = eye.perceive(os.path.dirname(__file__))
    if dir_perception.success:
        content_lines = dir_perception.content.splitlines()
        for line in content_lines[:15]:
            print(f"    {line}")


# ---------------------------------------------------------------------------
# Demo 2: Ghrana (Nose) -- EnvironmentSniffer
# ---------------------------------------------------------------------------

def demo_ghrana():
    separator("DEMO 2: Ghrana (Nose) -- EnvironmentSniffer")
    print("Sniffing the om/ project to detect its structure.\n")

    nose = Ghrana()
    om_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    perception = nose.perceive(om_dir)

    print_perception(perception, verbose=True)

    if perception.success and isinstance(perception.content, dict):
        scent = perception.content
        print()
        print("  Project Analysis:")
        print(f"    Summary:    {scent.get('summary', 'N/A')}")
        print(f"    Languages:  {scent.get('languages', [])}")
        print(f"    Tools:      {scent.get('tools', [])}")
        print(f"    VCS:        {scent.get('vcs', [])}")

        markers = scent.get("markers_found", {})
        print(f"    Markers ({len(markers)}):")
        for name, signals in list(markers.items())[:10]:
            print(f"      {name}: {signals}")

        git_info = scent.get("git", {})
        if git_info:
            print(f"    Git branch: {git_info.get('branch', '?')}")
            print(f"    Git clean:  {git_info.get('clean', '?')}")
            print(f"    Last commit: {git_info.get('last_commit', '?')}")


# ---------------------------------------------------------------------------
# Demo 3: Tvak (Skin) -- ShellSensor
# ---------------------------------------------------------------------------

def demo_tvak():
    separator("DEMO 3: Tvak (Skin) -- ShellSensor")
    print("Getting git status through safe shell execution.\n")

    skin = Tvak()

    # Safe command: git status
    om_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    perception = skin.perceive("git status", cwd=om_dir)
    print("  --- git status ---")
    print_perception(perception)

    # Safe command: git log
    print()
    print("  --- git log (last 3 commits) ---")
    perception2 = skin.perceive("git log -3 --oneline", cwd=om_dir)
    print_perception(perception2)

    # Demonstrate safety: try a dangerous command
    print()
    print("  --- SAFETY TEST: attempting 'rm -rf /' ---")
    blocked = skin.perceive("rm -rf /")
    print(f"  Blocked:  {not blocked.success}")
    print(f"  Error:    {blocked.error}")

    print()
    print("  --- SAFETY TEST: attempting 'sudo ls' ---")
    blocked2 = skin.perceive("sudo ls")
    print(f"  Blocked:  {not blocked2.success}")
    print(f"  Error:    {blocked2.error}")

    print()
    print("  --- SAFETY TEST: attempting piped command 'ls | rm' ---")
    blocked3 = skin.perceive("ls | rm")
    print(f"  Blocked:  {not blocked3.success}")
    print(f"  Error:    {blocked3.error}")


# ---------------------------------------------------------------------------
# Demo 4: Manas (Mind) -- Perception Router
# ---------------------------------------------------------------------------

def demo_manas():
    separator("DEMO 4: Manas (Mind) -- Perception Router")
    print("Manas routes queries to the appropriate sense organs.\n")

    manas = Manas()
    om_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Query 1: File path -- should route to Chakshu
    print("  Query: 'Read /Users/harsh/om/THESIS.md'")
    thesis_path = os.path.join(om_dir, "THESIS.md")
    bundle = manas.perceive_all(f"Read {thesis_path}")
    print(f"  Indriyas activated: {bundle.indriyas_activated}")
    print(f"  Perceptions: {len(bundle.perceptions)}")
    print(f"  Successful:  {len(bundle.successful)}")
    print(f"  Time:        {bundle.total_time_ms:.1f}ms")
    print()

    # Query 2: Project analysis -- should route to Ghrana
    print(f"  Query: 'Analyze the project at {om_dir}'")
    bundle2 = manas.perceive_all(f"Analyze the project at {om_dir}")
    print(f"  Indriyas activated: {bundle2.indriyas_activated}")
    print(f"  Perceptions: {len(bundle2.perceptions)}")
    print(f"  Successful:  {len(bundle2.successful)}")
    print(f"  Time:        {bundle2.total_time_ms:.1f}ms")
    print()

    # Query 3: Shell command -- should route to Tvak
    print("  Query: 'git status of the repo'")
    bundle3 = manas.perceive_all("git status of the repo")
    print(f"  Indriyas activated: {bundle3.indriyas_activated}")
    print(f"  Perceptions: {len(bundle3.perceptions)}")
    print(f"  Successful:  {len(bundle3.successful)}")
    print(f"  Time:        {bundle3.total_time_ms:.1f}ms")


# ---------------------------------------------------------------------------
# Demo 5: PerceptionBundle as Context
# ---------------------------------------------------------------------------

def demo_bundle():
    separator("DEMO 5: PerceptionBundle -- Multi-Sense Context")
    print("Building a perception bundle from multiple senses,")
    print("then formatting it as context for the Darshana LLM.\n")

    manas = Manas()
    om_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Manually gather perceptions from multiple senses
    bundle = PerceptionBundle(query="Understand the om/ project")

    # Eye: read the THESIS.md
    thesis_path = os.path.join(om_dir, "THESIS.md")
    p1 = manas.chakshu.perceive(thesis_path, max_lines=20)
    bundle.perceptions.append(p1)

    # Nose: sniff the project
    p2 = manas.ghrana.perceive(om_dir)
    bundle.perceptions.append(p2)

    # Skin: git status
    p3 = manas.tvak.perceive("git status", cwd=om_dir)
    bundle.perceptions.append(p3)

    bundle.indriyas_activated = [
        p.source.value for p in bundle.perceptions
    ]

    # Show results
    print(f"  Bundle query:      {bundle.query}")
    print(f"  Indriyas used:     {bundle.indriyas_activated}")
    print(f"  Total perceptions: {len(bundle.perceptions)}")
    print(f"  Successful:        {len(bundle.successful)}")
    print(f"  Failed:            {len(bundle.failed)}")
    print()

    # Show the context string (what would be fed to the LLM)
    context = bundle.as_context()
    print("  --- Context for LLM (first 1500 chars) ---")
    print()
    for line in context[:1500].splitlines():
        print(f"    {line}")
    if len(context) > 1500:
        print(f"    ... ({len(context)} chars total)")


# ---------------------------------------------------------------------------
# Demo 6: Karmendriyas (Action Stubs)
# ---------------------------------------------------------------------------

def demo_karmendriyas():
    separator("DEMO 6: Karmendriyas (Action Organs) -- Future Stubs")
    print("The five action organs are defined but not yet implemented.\n")

    karmendriyas = [
        Vak(),      # Speech
        Pani(),     # Hands
        Pada(),     # Feet
        Payu(),     # Elimination
        Upastha(),  # Creation
    ]

    for k in karmendriyas:
        result = k.act("test action")
        print(f"  {k.sanskrit_name:8s} ({k.name:10s}): "
              f"available={k.available()}, "
              f"action={result['action']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  Pratyaksha (direct perception) -- The Perception Layer")
    print("  ======================================================")
    print()
    print("  In Samkhya philosophy, the Jnanendriyas (knowledge senses)")
    print("  are the five channels through which Purusha perceives Prakriti.")
    print("  This demo shows each sense organ in action.")
    print()
    print("  Every perception is tagged: pramana=pratyaksha, confidence=1.0")
    print("  (Direct perception is the highest epistemic source in Nyaya.)")

    demo_chakshu()
    demo_ghrana()
    demo_tvak()
    demo_manas()
    demo_bundle()
    demo_karmendriyas()

    separator("COMPLETE")
    print("  All five Jnanendriyas demonstrated.")
    print("  Manas (mind) routes queries to the right senses.")
    print("  PerceptionBundle formats multi-sense data as LLM context.")
    print("  Karmendriyas (action organs) are stubbed for future work.")
    print()
    print("  Next step: Feed PerceptionBundle.as_context() into")
    print("  DarshanaLLM.think(query, context=bundle.as_context())")
    print("  to give the reasoning engines grounded, direct perception.")
    print()


if __name__ == "__main__":
    main()
