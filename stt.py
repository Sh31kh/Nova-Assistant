# stt.py
"""Local speech-to-text via faster-whisper."""

from faster_whisper import WhisperModel
import numpy as np

_model = None  # lazy-loaded, not at import time — matches the "don't keep
                # heavy stuff loaded when idle" principle from the spec


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe(audio: np.ndarray, sample_rate: int = 16000) -> str:
    if audio.size == 0:
        return ""

    model = get_model()
    segments, _ = model.transcribe(audio, language="en")
    return " ".join(seg.text.strip() for seg in segments).strip()