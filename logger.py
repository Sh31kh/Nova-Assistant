# logger.py
"""logger.py — structured file logging with automatic rotation.

Rotation caps total log storage regardless of usage duration/volume —
see DECISIONS.md for the storage-size reasoning behind this choice.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_PATH = Path(__file__).parent / "nova.log"

logger = logging.getLogger("nova")
logger.setLevel(logging.INFO)

_handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=1_000_000,   # 1MB per file
    backupCount=5,        # keep 5 old files, then delete oldest
    encoding="utf-8",
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
logger.addHandler(_handler)