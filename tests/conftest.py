import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Use a throw-away database for tests (must be set before modules.config is imported)
os.environ["EDUADAPT_DB"] = str(Path(tempfile.mkdtemp()) / "test.db")
os.environ["EDUADAPT_TTS"] = "none"
