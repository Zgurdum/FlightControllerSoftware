"""
Tunes Manager
Handles saving, loading, importing and exporting PID/Rate tune profiles.
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

TUNES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'tunes')


def _ensure_dir():
    os.makedirs(TUNES_DIR, exist_ok=True)


DEFAULT_TUNES = [
    {
        "name": "Race Pro",
        "author": "ThrustMaster",
        "description": "Aggressive race setup for tight tracks. High P gains, low D. Very snappy response.",
        "fc_type": "F722",
        "version": "1.0",
        "tags": ["race", "aggressive", "fast"],
        "pid": {
            "roll": {"p": 52, "i": 95, "d": 28},
            "pitch": {"p": 56, "i": 100, "d": 30},
            "yaw": {"p": 45, "i": 90, "d": 0},
        },
        "rates": {"rc_rate": 1.40, "super_rate": 0.80, "expo": 0.10},
        "created": "2025-01-15 14:00",
        "builtin": True,
    },
    {
        "name": "Freestyle Smooth",
        "author": "AirBender",
        "description": "Balanced freestyle tune. Smooth throttle response, floaty feel for flow style flying.",
        "fc_type": "F722",
        "version": "2.1",
        "tags": ["freestyle", "smooth", "flow"],
        "pid": {
            "roll": {"p": 42, "i": 85, "d": 38},
            "pitch": {"p": 45, "i": 88, "d": 40},
            "yaw": {"p": 38, "i": 80, "d": 0},
        },
        "rates": {"rc_rate": 1.00, "super_rate": 0.70, "expo": 0.20},
        "created": "2025-02-20 09:30",
        "builtin": True,
    },
    {
        "name": "Cinematic Cruise",
        "author": "SkyDrifter",
        "description": "Ultra smooth cinematic tune. Low rates, gentle response perfect for cinematic footage.",
        "fc_type": "F722",
        "version": "1.3",
        "tags": ["cinematic", "smooth", "slow"],
        "pid": {
            "roll": {"p": 32, "i": 70, "d": 42},
            "pitch": {"p": 35, "i": 74, "d": 44},
            "yaw": {"p": 30, "i": 65, "d": 0},
        },
        "rates": {"rc_rate": 0.70, "super_rate": 0.50, "expo": 0.35},
        "created": "2025-03-05 16:20",
        "builtin": True,
    },
    {
        "name": "Beginner Safe",
        "author": "FPV_Academy",
        "description": "Gentle tune for beginners. Low sensitivity and high D dampening for stability.",
        "fc_type": "F722",
        "version": "1.5",
        "tags": ["beginner", "safe", "stable"],
        "pid": {
            "roll": {"p": 30, "i": 65, "d": 45},
            "pitch": {"p": 33, "i": 68, "d": 47},
            "yaw": {"p": 28, "i": 60, "d": 0},
        },
        "rates": {"rc_rate": 0.60, "super_rate": 0.40, "expo": 0.40},
        "created": "2025-01-01 12:00",
        "builtin": True,
    },
    {
        "name": "Velvet King",
        "author": "NightOwl",
        "description": "Night flying tune with very smooth transitions and minimal prop wash.",
        "fc_type": "F722",
        "version": "1.2",
        "tags": ["night", "smooth", "propwash"],
        "pid": {
            "roll": {"p": 38, "i": 80, "d": 40},
            "pitch": {"p": 41, "i": 84, "d": 42},
            "yaw": {"p": 35, "i": 75, "d": 0},
        },
        "rates": {"rc_rate": 0.90, "super_rate": 0.65, "expo": 0.25},
        "created": "2025-04-12 21:00",
        "builtin": True,
    },
    {
        "name": "Tiny Ripper",
        "author": "MicroMaster",
        "description": "Optimized for 3\" builds. Tighter PID loop for high kv motors.",
        "fc_type": "F722",
        "version": "1.0",
        "tags": ["3inch", "micro", "high-kv"],
        "pid": {
            "roll": {"p": 60, "i": 110, "d": 20},
            "pitch": {"p": 64, "i": 115, "d": 22},
            "yaw": {"p": 55, "i": 100, "d": 0},
        },
        "rates": {"rc_rate": 1.60, "super_rate": 0.85, "expo": 0.05},
        "created": "2025-05-01 08:00",
        "builtin": True,
    },
]


class Tune:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "Unnamed Tune")
        self.author: str = data.get("author", "Unknown")
        self.description: str = data.get("description", "")
        self.fc_type: str = data.get("fc_type", "F722")
        self.version: str = data.get("version", "1.0")
        self.tags: List[str] = data.get("tags", [])
        self.pid: Dict = data.get("pid", {
            "roll": {"p": 42, "i": 85, "d": 35},
            "pitch": {"p": 46, "i": 90, "d": 38},
            "yaw": {"p": 40, "i": 85, "d": 0},
        })
        self.rates: Dict = data.get("rates", {
            "rc_rate": 1.0,
            "super_rate": 0.7,
            "expo": 0.15,
        })
        self.created: str = data.get("created", datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.builtin: bool = data.get("builtin", False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "fc_type": self.fc_type,
            "version": self.version,
            "tags": self.tags,
            "pid": self.pid,
            "rates": self.rates,
            "created": self.created,
            "builtin": self.builtin,
        }

    def get_pid_summary(self) -> str:
        r = self.pid.get("roll", {})
        p = self.pid.get("pitch", {})
        y = self.pid.get("yaw", {})
        return (
            f"Roll   P:{r.get('p','-'):>3}  I:{r.get('i','-'):>3}  D:{r.get('d','-'):>3}\n"
            f"Pitch  P:{p.get('p','-'):>3}  I:{p.get('i','-'):>3}  D:{p.get('d','-'):>3}\n"
            f"Yaw    P:{y.get('p','-'):>3}  I:{y.get('i','-'):>3}  D:{y.get('d','-'):>3}"
        )

    def __repr__(self):
        return f"Tune({self.name} by {self.author})"


class TunesManager:
    """Manages built-in and user tunes."""

    def __init__(self):
        _ensure_dir()
        self._seed_builtin_tunes()

    def _seed_builtin_tunes(self):
        """Write built-in tunes to disk if not already there."""
        for tune_data in DEFAULT_TUNES:
            filename = self._safe_filename(tune_data["name"]) + ".json"
            path = os.path.join(TUNES_DIR, filename)
            if not os.path.exists(path):
                try:
                    with open(path, "w") as f:
                        json.dump(tune_data, f, indent=2)
                except Exception as e:
                    print(f"Could not seed tune {tune_data['name']}: {e}")

    def _safe_filename(self, name: str) -> str:
        return "".join(c if c.isalnum() or c in "_ -" else "_" for c in name).strip()

    def list_tunes(self) -> List[Tune]:
        """Return all available tunes sorted by built-in first, then user."""
        tunes = []
        for fn in sorted(os.listdir(TUNES_DIR)):
            if fn.endswith(".json"):
                path = os.path.join(TUNES_DIR, fn)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                    tunes.append(Tune(data))
                except Exception:
                    pass
        # Sort: built-ins first, then by name
        return sorted(tunes, key=lambda t: (not t.builtin, t.name.lower()))

    def save_tune(self, tune: Tune) -> bool:
        """Save a user tune."""
        _ensure_dir()
        try:
            filename = self._safe_filename(tune.name) + ".json"
            path = os.path.join(TUNES_DIR, filename)
            with open(path, "w") as f:
                json.dump(tune.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tune: {e}")
            return False

    def delete_tune(self, tune: Tune) -> bool:
        """Delete a user tune (built-ins cannot be deleted)."""
        if tune.builtin:
            return False
        filename = self._safe_filename(tune.name) + ".json"
        path = os.path.join(TUNES_DIR, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception:
                return False
        return False

    def import_from_file(self, filepath: str) -> Optional[Tune]:
        """Import a tune from a JSON file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            tune = Tune(data)
            tune.builtin = False
            self.save_tune(tune)
            return tune
        except Exception as e:
            print(f"Error importing tune: {e}")
            return None

    def export_to_file(self, tune: Tune, filepath: str) -> bool:
        """Export a tune to a JSON file."""
        try:
            with open(filepath, "w") as f:
                json.dump(tune.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting tune: {e}")
            return False
