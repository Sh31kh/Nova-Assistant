import keyboard

def on_press():
    print("LISTENING (F8 held)")

def on_release():
    print("STOPPED")

keyboard.on_press_key("F8", lambda _: on_press())
keyboard.on_release_key("F8", lambda _: on_release())

print("Hold F8. Press F9 to quit.")

keyboard.wait("F9")