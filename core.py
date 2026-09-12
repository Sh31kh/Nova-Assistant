from config import load_config
from audio import record_while_held
from stt import transcribe
from llm import get_tool_call
from tools import TOOL_REGISTRY, configure as configure_tools
from time_tools import check_deterministic
from tts import speak
import keyboard
import os

FALLBACK_MESSAGE = "Sorry, I didn't understand that."

cfg = load_config()
configure_tools(cfg)


def _handle_quit():
    print("\nExiting.")
    os._exit(0)


keyboard.add_hotkey("f9", _handle_quit)


def handle_command():
    audio = record_while_held(cfg.hotkey)
    if audio.size == 0:
        print("No audio captured.")
        return

    text = transcribe(audio)
    print(f"Heard: \"{text}\"")

    if not text:
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE)
        return

    # Deterministic bypass — skip the LLM entirely for trivial queries
    direct = check_deterministic(text)
    if direct is not None:
        print(direct)
        speak(direct)
        return

    call = get_tool_call(text, cfg)
    if call is None:
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE)
        return

    tool_fn = TOOL_REGISTRY.get(call["name"])
    if tool_fn is None:
        print(f"[core] LLM called unknown tool: {call['name']}")
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE)
        return

    result = tool_fn(**call["arguments"])
    print(result["message"])
    speak(result["message"])


def main():
    print(f"Assistant ready. Hold {cfg.hotkey.upper()} to talk, F9 to quit.")
    while True:
        try:
            handle_command()
        except KeyboardInterrupt:
            print("\nExiting.")
            break