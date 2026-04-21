"""Persistent training state for model training jobs.

This keeps training progress available even when the training job runs
outside the API worker process.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict


STATE_PATH = Path(tempfile.gettempdir()) / "quantfin_training_state.json"


def load_training_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {
            "status": "idle",
            "progress": 0,
            "current_model": None,
            "models_completed": [],
            "error": None,
            "started_at": None,
            "completed_at": None,
        }

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {
            "status": "idle",
            "progress": 0,
            "current_model": None,
            "models_completed": [],
            "error": None,
            "started_at": None,
            "completed_at": None,
        }


def save_training_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
