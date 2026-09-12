# tray.py
"""tray.py — system tray icon with three states: idle, listening, disabled."""

import os
from pathlib import Path
import pystray
from PIL import Image
from app_state import state
from tts import speak

_icons = {}
_icon_ref = None
_cfg = None


def _load_icons(cfg):
    global _icons
    base = Path(__file__).parent
    _icons = {
        "idle": Image.open(base / cfg.tray_icon_idle),
        "listening": Image.open(base / cfg.tray_icon_listening),
        "disabled": Image.open(base / cfg.tray_icon_disabled),
    }


def set_state(name: str):
    if _icon_ref is not None and name in _icons:
        _icon_ref.icon = _icons[name]


def _toggle_enabled(icon, item):
    state.enabled = not state.enabled
    icon.icon = _icons["disabled"] if not state.enabled else _icons["idle"]
    icon.update_menu()

    if state.enabled:
        speak("Nova is back online.", _cfg)
    else:
        speak("Nova is disabled for now.", _cfg)


def _quit(icon, item):
    icon.stop()
    os._exit(0)


def run_tray(cfg):
    global _icon_ref, _cfg
    _cfg = cfg
    _load_icons(cfg)

    icon = pystray.Icon(
        "Nova",
        _icons["idle"],
        "Nova Assistant",
        menu=pystray.Menu(
            pystray.MenuItem(
                lambda item: "Disable" if state.enabled else "Enable",
                _toggle_enabled,
            ),
            pystray.MenuItem("Exit", _quit),
        ),
    )
    _icon_ref = icon
    icon.run()