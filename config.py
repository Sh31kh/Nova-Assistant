"""config.py — loads config.yaml once at startup.

Deliberately simple for Phase 1: load once, pass the resulting object
around. No hot-reloading, no file watching, no schema versioning — none
of that is needed yet for a single-user, single-machine setup.
"""

from pathlib import Path
import sys
import yaml

CONFIG_PATH = Path(__file__).parent / "config.yaml"
EXAMPLE_PATH = Path(__file__).parent / "config.example.yaml"


class Config:
    """Thin wrapper around the loaded YAML dict with a couple of
    convenience accessors. Deliberately not a big abstraction — just
    enough to avoid repeating config["apps"][name]["open_path"] everywhere.
    """

    def __init__(self, data: dict):
        self._data = data

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
        app = self._data.get("apps", {}).get(name.lower())
        return app["open_path"] if app else None

    def app_close_process(self, name: str) -> str | None:
        app = self._data.get("apps", {}).get(name.lower())
        return app["close_process"] if app else None


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