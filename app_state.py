# app_state.py
"""Small shared mutable state between core.py's hotkey loop (main thread)
and tray.py's tray icon (its own thread). Kept deliberately minimal —
one flag, no locking needed for a single bool toggle at this scale."""

class AppState:
    def __init__(self):
        self.enabled = True

state = AppState()