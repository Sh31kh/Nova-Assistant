"""tts.py — text-to-speech via Piper (local neural TTS)."""

from pathlib import Path
import subprocess
import sounddevice as sd

VOICE_MODEL = Path(__file__).parent / "piper_voices" / "en_GB-northern_english_male-medium.onnx"


def speak(text: str):
    if not text:
        return

    result = subprocess.run(
        ["piper", "--model", str(VOICE_MODEL), "--output-raw", "--length-scale", "1.1"],
        input=text.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"[tts] Piper failed: {result.stderr.decode(errors='ignore')}")
        return

    # Piper's --output-raw is 16-bit PCM, 22050 Hz, mono
    import numpy as np
    audio = np.frombuffer(result.stdout, dtype=np.int16)
    audio = (audio * 0.35).astype(np.int16)

    sd.play(audio, samplerate=22050)
    sd.wait()