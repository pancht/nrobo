# src/nrobo/services/nginx_service_state.py
import json
import os
from pathlib import Path
from typing import Optional, TypedDict

try:
    from platformdirs import user_cache_dir  # pip install platformdirs
except Exception:
    # fallback without extra dep
    def user_cache_dir(appname: str, appauthor: str = "") -> str:
        if os.name == "nt":
            base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            return os.path.join(base, appname)
        # posix
        return os.path.join(os.path.expanduser("~/.cache"), appname)


class NginxState(TypedDict):
    url: str
    port: int
    host: str
    served_dir: str
    runtime_dir: str
    nginx_path: str
    mode: str  # "user-local" | "system"


def state_path() -> Path:
    cache_dir = Path(user_cache_dir("nrobo"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "nginx_state.json"


def save_state(state: NginxState) -> None:
    state_path().write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_state() -> Optional[NginxState]:
    p = state_path()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def clear_state() -> None:
    p = state_path()
    if p.exists():
        p.unlink(missing_ok=True)
