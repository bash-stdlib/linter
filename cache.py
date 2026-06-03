"""Metadata persistence logic for the bash-stdlib linter."""

import os
import json
import sys
from constants import CACHE_FILE

def save_cache(metadata):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Cache saved to {CACHE_FILE}", file=sys.stderr)
    except Exception as e:
        print(f"Error: Failed to save cache: {e}", file=sys.stderr)

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load cache: {e}", file=sys.stderr)
        return None
