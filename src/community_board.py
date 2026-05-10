"""
Community Board
Local message board for pilot notes, tips, and tune sharing.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
BOARD_FILE = os.path.join(DATA_DIR, 'community.json')

SEED_MESSAGES = [
    {
        "id": 1,
        "author": "ThrustMaster",
        "callsign": "THRUST",
        "content": "Welcome to the Community Board! Share your tunes, tips, and flights here. Happy flying! 🚁",
        "timestamp": "2025-01-01 00:00",
        "msg_type": "welcome",
        "avatar_color": "#7c3aed",
    },
    {
        "id": 2,
        "author": "AirBender",
        "callsign": "AIRB",
        "content": "Pro tip: Always calibrate your accelerometer on a flat surface BEFORE your first flight. Makes a big difference in angle mode!",
        "timestamp": "2025-01-02 14:30",
        "msg_type": "tip",
        "avatar_color": "#0ea5e9",
    },
    {
        "id": 3,
        "author": "FPV_Academy",
        "callsign": "ACAD",
        "content": "Beginners: Start with low rates (rc_rate ~0.6) and work your way up as you get more comfortable. Don't rush it!",
        "timestamp": "2025-01-05 10:15",
        "msg_type": "tip",
        "avatar_color": "#22c55e",
    },
    {
        "id": 4,
        "author": "NightOwl",
        "callsign": "NITE",
        "content": "My Velvet King tune is now in the library. Perfect for smooth cinematic passes at dusk. Let me know what you think!",
        "timestamp": "2025-04-12 21:05",
        "msg_type": "tune_share",
        "avatar_color": "#f59e0b",
    },
]


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


class Message:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data.get("id", 0)
        self.author: str = data.get("author", "Anonymous")
        self.callsign: str = data.get("callsign", "ANON")
        self.content: str = data.get("content", "")
        self.timestamp: str = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.msg_type: str = data.get("msg_type", "text")  # text | tip | tune_share | welcome
        self.avatar_color: str = data.get("avatar_color", "#7c3aed")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "author": self.author,
            "callsign": self.callsign,
            "content": self.content,
            "timestamp": self.timestamp,
            "msg_type": self.msg_type,
            "avatar_color": self.avatar_color,
        }

    def get_formatted_header(self) -> str:
        type_badge = {"text": "", "tip": " [TIP]", "tune_share": " [TUNE]", "welcome": " [SYS]"}.get(
            self.msg_type, ""
        )
        return f"[{self.callsign}]{type_badge}  {self.timestamp}"


class CommunityBoard:
    """Local message board for sharing between pilots."""

    def __init__(self):
        _ensure_dir()
        self._messages: List[Message] = []
        self._load()

    def _load(self):
        if os.path.exists(BOARD_FILE):
            try:
                with open(BOARD_FILE, "r") as f:
                    data = json.load(f)
                self._messages = [Message(m) for m in data.get("messages", [])]
            except Exception:
                self._messages = []
        else:
            # Seed with welcome messages
            self._messages = [Message(m) for m in SEED_MESSAGES]
            self._save()

    def _save(self):
        _ensure_dir()
        try:
            with open(BOARD_FILE, "w") as f:
                json.dump({"messages": [m.to_dict() for m in self._messages]}, f, indent=2)
        except Exception as e:
            print(f"Error saving community board: {e}")

    def _next_id(self) -> int:
        if not self._messages:
            return 1
        return max(m.id for m in self._messages) + 1

    def post(self, author: str, callsign: str, content: str,
             msg_type: str = "text", avatar_color: str = "#7c3aed") -> Optional[Message]:
        """Post a new message to the board."""
        if not content.strip():
            return None
        msg = Message({
            "id": self._next_id(),
            "author": author,
            "callsign": callsign.upper(),
            "content": content.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "msg_type": msg_type,
            "avatar_color": avatar_color,
        })
        self._messages.append(msg)
        self._save()
        return msg

    def delete(self, msg_id: int) -> bool:
        """Delete a message by ID."""
        before = len(self._messages)
        self._messages = [m for m in self._messages if m.id != msg_id]
        if len(self._messages) < before:
            self._save()
            return True
        return False

    def get_all(self) -> List[Message]:
        return list(self._messages)

    def get_recent(self, limit: int = 50) -> List[Message]:
        return list(self._messages[-limit:])

    def search(self, query: str) -> List[Message]:
        q = query.lower()
        return [m for m in self._messages if q in m.content.lower() or q in m.callsign.lower()]
