# Nova Assistant

Work in progress — local voice assistant for Windows. Not yet ready for
general use.

## Setup (partial, expanding as the project develops)
1. `pip install -r requirements.txt`
2. `pip install piper-tts`
3. Copy `config.example.yaml` to `config.yaml` and fill in your paths.
4. Download a Piper voice model (e.g. `en_GB-northern_english_male-medium`)
   from https://huggingface.co/rhasspy/piper-voices and place both the
   `.onnx` and `.onnx.json` files in `piper_voices/`.
5. Run `ollama pull qwen2.5:14b` and make sure Ollama is running.
6. `python main.py`
