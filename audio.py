# audio.py
"""Push-to-talk audio capture."""

import sounddevice as sd
import numpy as np
import keyboard

SAMPLE_RATE = 16000  # faster-whisper expects 16kHz mono
HOTKEY = "f8"


def record_while_held(hotkey: str = HOTKEY) -> np.ndarray:
    """Blocks until hotkey is pressed, records until released, returns audio."""
    print(f"Hold {hotkey.upper()} to talk...")
    keyboard.wait(hotkey)  # blocks until pressed

    print("Listening...")
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback
    )
    with stream:
        while keyboard.is_pressed(hotkey):
            sd.sleep(50)  # poll every 50ms rather than busy-waiting

    print("Stopped.")

    if not frames:
        return np.array([], dtype="float32")

    return np.concatenate(frames, axis=0).flatten()