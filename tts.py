"""tts.py — text-to-speech via Piper (local neural TTS)."""

from pathlib import Path
import subprocess
import numpy as np
import sounddevice as sd

VOICE_DIR = Path(__file__).parent / "piper_voices"


def speak(text: str, cfg):
    if not text:
        return

    voice_path = VOICE_DIR / cfg.tts_voice_model

    result = subprocess.run(
        ["piper", "--model", str(voice_path),
         "--output-raw", "--length-scale", str(cfg.tts_length_scale)],
        input=text.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"[tts] Piper failed: {result.stderr.decode(errors='ignore')}")
        return

    # Piper's --output-raw is 16-bit PCM, 22050 Hz, mono
    audio = np.frombuffer(result.stdout, dtype=np.int16)
    audio = (audio * cfg.tts_volume).astype(np.int16)

    sd.play(audio, samplerate=22050)
    sd.wait()