import json
import os
import stat

from rich.console import Console

CONFIG_DIR = os.path.expanduser("~/.icrackU")
KEYS_FILE = os.path.join(CONFIG_DIR, "keys.json")
SKIP_SENTINEL = "__skip__"

console = Console()


def _load() -> dict[str, str]:
    if not os.path.exists(KEYS_FILE):
        return {}
    try:
        with open(KEYS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict[str, str]) -> None:
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(KEYS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        os.chmod(KEYS_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def get_key(name: str) -> str | None:
    """Return cached API key or None if missing or previously skipped."""
    val = _load().get(name)
    if val is None or val == SKIP_SENTINEL:
        return None
    return val


def prompt_and_save_key(name: str, prompt_text: str) -> str | None:
    """Prompt user for key, cache it, and return it. Returns None if user skips."""
    value = console.input(f"  [dim]{prompt_text}[/dim] ").strip()
    data = _load()
    if not value:
        data[name] = SKIP_SENTINEL
        _save(data)
        return None
    data[name] = value
    _save(data)
    return value


def require_key(name: str, prompt_text: str) -> str | None:
    """Return cached key, prompt once if missing, or return None if previously skipped."""
    raw = _load().get(name)
    if raw == SKIP_SENTINEL:
        return None
    if raw:
        return raw
    return prompt_and_save_key(name, prompt_text)
