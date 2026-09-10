# core.py
"""Phase 0 entry point: hotkey -> record -> transcribe -> route -> execute."""

from audio import record_while_held
from stt import transcribe
from llm import get_tool_call
from tools import TOOL_REGISTRY
import keyboard
import os

def _handle_quit():
    print("\nExiting.")
    os._exit(0)  # abrupt but reliable — see note below

keyboard.add_hotkey("f9", _handle_quit)

FALLBACK_MESSAGE = "Sorry, I didn't understand that."


def handle_command():
    audio = record_while_held()
    if audio.size == 0:
        print("No audio captured.")
        return

    text = transcribe(audio)
    print(f"Heard: \"{text}\"")

    if not text:
        print(FALLBACK_MESSAGE)
        return

    call = get_tool_call(text)
    if call is None:
        # tool_calls: None is a failure state, not "nothing to do" — never
        # go silent here, per the rule your own testing established.
        print(FALLBACK_MESSAGE)
        return

    tool_fn = TOOL_REGISTRY.get(call["name"])
    if tool_fn is None:
        # Should never happen if TOOLS and TOOL_REGISTRY stay in sync,
        # but don't pretend success if it does.
        print(f"[core] LLM called unknown tool: {call['name']}")
        print(FALLBACK_MESSAGE)
        return

    result = tool_fn(**call["arguments"])
    print(result["message"])


def main():
    print("Assistant ready. Hold F8 to talk, F9 to quit.")
    while True:
        try:
            handle_command()
        except KeyboardInterrupt:
            print("\nExiting.")
            break