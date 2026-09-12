# audio.py
"""Push-to-talk audio capture."""

import sounddevice as sd
import numpy as np
import keyboard

SAMPLE_RATE = 16000


def wait_for_press(hotkey: str):
    """Blocks until the hotkey is pressed. Nothing recorded yet."""
    keyboard.wait(hotkey)


def record_until_release(hotkey: str) -> np.ndarray:
    """Assumes the hotkey is currently held. Records until released."""
    print("Listening...")
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback
    )
    with stream:
        while keyboard.is_pressed(hotkey):
            sd.sleep(50)

    print("Stopped.")

    if not frames:
        return np.array([], dtype="float32")

    return np.concatenate(frames, axis=0).flatten()