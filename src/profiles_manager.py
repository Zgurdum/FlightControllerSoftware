"""
User Profiles Manager
Handles saving and loading pilot profiles with FC settings.
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'profiles')


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


class Profile:
    def __init__(
        self,
        name: str,
        callsign: str,
        bio: str = "",
        fc_type: str = "F722",
        avatar_color: str = "#7c3aed",
        pid: Optional[Dict] = None,
        rates: Optional[Dict] = None,
        notes: str = "",
        created: str = "",
        last_modified: str = "",
    ):
        self.name = name
        self.callsign = callsign.upper()
        self.bio = bio
        self.fc_type = fc_type
        self.avatar_color = avatar_color
        self.pid = pid or {
            "roll": {"p": 42, "i": 85, "d": 35},
            "pitch": {"p": 46, "i": 90, "d": 38},
            "yaw": {"p": 40, "i": 85, "d": 0},
        }
        self.rates = rates or {
            "rc_rate": 1.0,
            "super_rate": 0.7,
            "expo": 0.15,
        }
        self.notes = notes
        self.created = created or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.last_modified = last_modified or self.created

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "callsign": self.callsign,
            "bio": self.bio,
            "fc_type": self.fc_type,
            "avatar_color": self.avatar_color,
            "pid": self.pid,
            "rates": self.rates,
            "notes": self.notes,
            "created": self.created,
            "last_modified": self.last_modified,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Profile":
        return Profile(
            name=data.get("name", "Unknown"),
            callsign=data.get("callsign", "PILOT"),
            bio=data.get("bio", ""),
            fc_type=data.get("fc_type", "F722"),
            avatar_color=data.get("avatar_color", "#7c3aed"),
            pid=data.get("pid"),
            rates=data.get("rates"),
            notes=data.get("notes", ""),
            created=data.get("created", ""),
            last_modified=data.get("last_modified", ""),
        )

    def __repr__(self):
        return f"Profile({self.callsign} - {self.name})"


class ProfilesManager:
    """Manages saving and loading user profiles."""

    def __init__(self):
        _ensure_dir()
        self.active_profile: Optional[Profile] = None
        self._load_active()

    def _load_active(self):
        """Load the last active profile if one exists."""
        meta_path = os.path.join(DATA_DIR, ".active")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    callsign = f.read().strip()
                    self.active_profile = self.load(callsign)
            except Exception:
                pass

    def _save_active(self):
        """Remember which profile was last used."""
        if self.active_profile:
            meta_path = os.path.join(DATA_DIR, ".active")
            try:
                with open(meta_path, "w") as f:
                    f.write(self.active_profile.callsign)
            except Exception:
                pass

    def save(self, profile: Profile) -> bool:
        """Save a profile to disk."""
        _ensure_dir()
        try:
            profile.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M")
            path = os.path.join(DATA_DIR, f"{profile.callsign}.json")
            with open(path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
            if self.active_profile and self.active_profile.callsign == profile.callsign:
                self.active_profile = profile
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def load(self, callsign: str) -> Optional[Profile]:
        """Load a profile by callsign."""
        path = os.path.join(DATA_DIR, f"{callsign.upper()}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return Profile.from_dict(data)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def list_profiles(self) -> List[Profile]:
        """Return all saved profiles."""
        _ensure_dir()
        profiles = []
        for fn in sorted(os.listdir(DATA_DIR)):
            if fn.endswith(".json"):
                callsign = fn[:-5]
                p = self.load(callsign)
                if p:
                    profiles.append(p)
        return profiles

    def delete(self, callsign: str) -> bool:
        """Delete a profile."""
        path = os.path.join(DATA_DIR, f"{callsign.upper()}.json")
        if os.path.exists(path):
            try:
                os.remove(path)
                if self.active_profile and self.active_profile.callsign == callsign.upper():
                    self.active_profile = None
                return True
            except Exception:
                return False
        return False

    def set_active(self, profile: Profile):
        """Set the currently active/logged-in profile."""
        self.active_profile = profile
        self._save_active()

    def get_active(self) -> Optional[Profile]:
        return self.active_profile
