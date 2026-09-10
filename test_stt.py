from audio import record_while_held
from stt import transcribe

audio = record_while_held()
text = transcribe(audio)
print(f"Transcribed: \"{text}\"")