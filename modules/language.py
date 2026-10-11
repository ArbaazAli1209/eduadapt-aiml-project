"""Language and speech helpers: translation (Hugging Face), text-to-speech (gTTS), speech-to-text (Whisper).

Everything is optional and lazy: if a backend or model is unavailable the functions degrade gracefully
(return the original text / None) so the app never crashes.
"""
import io
import os
import tempfile
from functools import lru_cache

from . import config

LANG_CODES = {"English": "en", "हिन्दी": "hi"}


@lru_cache(maxsize=1)
def _translator():
    from transformers import pipeline
    return pipeline("translation", model=config.TRANSLATE_MODEL)


@lru_cache(maxsize=512)
def translate(text, target="hi"):
    """English -> Hindi using a free Hugging Face model (set EDUADAPT_TRANSLATE=hf). Otherwise returns text unchanged."""
    if not text or target == "en" or config.TRANSLATE_BACKEND != "hf":
        return text
    try:
        return _translator()(text, max_length=400)[0]["translation_text"]
    except Exception:
        return text


def tts_available():
    if config.TTS_BACKEND != "gtts":
        return False
    try:
        import gtts  # noqa: F401
        return True
    except Exception:
        return False


def text_to_speech(text, lang="en"):
    """Return MP3 bytes for the text, or None if TTS is unavailable (gTTS needs an internet connection)."""
    if not text or not tts_available():
        return None
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


@lru_cache(maxsize=1)
def _whisper():
    import whisper
    return whisper.load_model(config.WHISPER_MODEL)


def stt_available():
    if config.STT_BACKEND != "whisper":
        return False
    try:
        import whisper  # noqa: F401
        return True
    except Exception:
        return False


def speech_to_text(audio_bytes, lang="en"):
    """Transcribe recorded audio with Whisper (needs ffmpeg installed). Returns text or ''."""
    if not audio_bytes or not stt_available():
        return ""
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            path = f.name
        return _whisper().transcribe(path, language=lang)["text"].strip()
    except Exception:
        return ""
    finally:
        if path and os.path.exists(path):
            os.remove(path)
