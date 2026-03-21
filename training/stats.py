#!/usr/bin/env python3
"""Print statistics about generated training data."""

import sys
from pathlib import Path

# Reuse the stats function from the main script
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from generate_data import print_stats

if __name__ == "__main__":
    print_stats()
