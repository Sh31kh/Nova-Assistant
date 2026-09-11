# config.py
"""config.py — loads config.yaml once at startup."""

from pathlib import Path
import sys
import yaml

CONFIG_PATH = Path(__file__).parent / "config.yaml"
EXAMPLE_PATH = Path(__file__).parent / "config.example.yaml"


class Config:
    def __init__(self, data: dict):
        self._data = data
        self._aliases = {k.lower(): v.lower() for k, v in data.get("aliases", {}).items()}

    def _resolve(self, name: str) -> str:
        """Resolve an alias to its canonical app/site key, or return the
        name unchanged if it's not an alias. Also normalizes spaces to
        underscores as a fallback, since config keys use underscores but
        natural speech uses spaces — this covers the common case (e.g.
        "google sheets" -> "google_sheets") without needing an explicit
        alias for every multi-word key."""
        key = name.strip().lower()
        if key in self._aliases:
            return self._aliases[key]
        normalized = key.replace(" ", "_")
        return self._aliases.get(normalized, normalized)

    @property
    def hotkey(self) -> str:
        return self._data["hotkey"]

    @property
    def ollama_model(self) -> str:
        return self._data["ollama"]["model"]

    @property
    def ollama_url(self) -> str:
        return self._data["ollama"]["url"]

    @property
    def ollama_timeout(self) -> int:
        return self._data["ollama"]["timeout"]

    def app_open_path(self, name: str) -> str | None:
        app = self._data.get("apps", {}).get(self._resolve(name))
        return app["open_path"] if app else None

    def app_open_args(self, name: str) -> list[str]:
        app = self._data.get("apps", {}).get(self._resolve(name))
        if not app:
            return []
        return app.get("launch_args", [])

    def app_close_process(self, name: str) -> str | None:
        app = self._data.get("apps", {}).get(self._resolve(name))
        return app["close_process"] if app else None
    
    def site_url(self, name: str) -> str | None:
        site = self._data.get("sites", {}).get(self._resolve(name))
        return site["url"] if site else None


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        print(
            f"[config] {CONFIG_PATH.name} not found.\n"
            f"  Copy {EXAMPLE_PATH.name} to {CONFIG_PATH.name} and fill in "
            f"your own values before running the assistant."
        )
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Config(data)