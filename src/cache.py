"""Metadata persistence logic for the bash-stdlib linter."""

import json
import os
import sys
from typing import Any, Optional

from constants import CACHE_FILE


def save_cache(metadata: "Dict[str, Any]") -> None:
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(metadata, f, indent=4)
        print("Cache saved to {}".format(CACHE_FILE), file=sys.stderr)
    except Exception as e:
        print("Error: Failed to save cache: {}".format(e), file=sys.stderr)


def load_cache() -> "Optional[Dict[str, Any]]":
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else None
    except Exception as e:
        print("Warning: Failed to load cache: {}".format(e), file=sys.stderr)
        return None
