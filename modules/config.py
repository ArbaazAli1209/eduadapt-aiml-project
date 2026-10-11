"""Central configuration. Every value can be overridden with an environment variable or a .env file."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # python-dotenv is optional at runtime
    pass

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
DB_PATH = Path(os.getenv("EDUADAPT_DB", str(ROOT / "eduadapt.db")))

# Generative AI (quiz generation, doubt answering)
LLM_BACKEND = os.getenv("EDUADAPT_LLM", "none").lower()          # none | hf | ollama
HF_MODEL = os.getenv("EDUADAPT_HF_MODEL", "ibm-granite/granite-3.3-2b-instruct")
OLLAMA_URL = os.getenv("EDUADAPT_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("EDUADAPT_OLLAMA_MODEL", "granite3.3:2b")

# Language and speech
TRANSLATE_BACKEND = os.getenv("EDUADAPT_TRANSLATE", "none").lower()  # none | hf
TRANSLATE_MODEL = os.getenv("EDUADAPT_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-hi")
STT_BACKEND = os.getenv("EDUADAPT_STT", "none").lower()              # none | whisper
WHISPER_MODEL = os.getenv("EDUADAPT_WHISPER_MODEL", "base")
TTS_BACKEND = os.getenv("EDUADAPT_TTS", "gtts").lower()              # gtts | none

# Learning rules
MASTERY_THRESHOLD = 0.6      # below this a topic counts as a weak area
EASY_BELOW = 0.4             # mastery < 0.4  -> easy questions
HARD_ABOVE = 0.7             # mastery > 0.7  -> hard questions
QUIZ_SIZE = 3
