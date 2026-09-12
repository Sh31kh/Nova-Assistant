from config import load_config
from audio import wait_for_press, record_until_release
from stt import transcribe
from llm import get_tool_call
from tools import TOOL_REGISTRY, configure as configure_tools
from time_tools import check_deterministic
from tts import speak
from app_state import state
from tray import run_tray, set_state
from logger import logger
import keyboard
import threading
import os
import time

FALLBACK_MESSAGE = "Sorry, I didn't understand that."

cfg = load_config()
configure_tools(cfg)


def _handle_quit():
    print("\nExiting.")
    os._exit(0)


keyboard.add_hotkey("f9", _handle_quit)

from logger import logger

def handle_command():
    print(f"Hold {cfg.hotkey.upper()} to talk...")
    wait_for_press(cfg.hotkey)

    if not state.enabled:
        print("Nova is disabled — ignoring.")
        while keyboard.is_pressed(cfg.hotkey):
            time.sleep(0.05)
        return

    set_state("listening")
    audio = record_until_release(cfg.hotkey)
    set_state("idle")

    if audio.size == 0:
        print("No audio captured.")
        logger.info("No audio captured.")
        return

    text = transcribe(audio)
    print(f"Heard: \"{text}\"")
    logger.info(f"Heard: \"{text}\"")

    if not text:
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE, cfg)
        logger.info("Empty transcript — fallback given.")
        return

    direct = check_deterministic(text)
    if direct is not None:
        print(direct)
        speak(direct, cfg)
        logger.info(f"Deterministic bypass -> {direct}")
        return

    call = get_tool_call(text, cfg)
    if call is None:
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE, cfg)
        logger.info("LLM returned no tool call — fallback given.")
        return

    tool_fn = TOOL_REGISTRY.get(call["name"])
    if tool_fn is None:
        print(f"[core] LLM called unknown tool: {call['name']}")
        print(FALLBACK_MESSAGE)
        speak(FALLBACK_MESSAGE, cfg)
        logger.warning(f"LLM called unknown tool: {call['name']}")
        return

    result = tool_fn(**call["arguments"])
    print(result["message"])
    speak(result["message"], cfg)
    logger.info(f"Tool: {call['name']} | Args: {call['arguments']} | Success: {result['success']} | Message: {result['message']}")


def main():
    print(f"Assistant ready. Hold {cfg.hotkey.upper()} to talk, F9 to quit.")

    tray_thread = threading.Thread(target=run_tray, args=(cfg,), daemon=True)
    tray_thread.start()

    while True:
        try:
            handle_command()
        except KeyboardInterrupt:
            print("\nExiting.")
            break