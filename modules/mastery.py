"""Glue between the database and the BKT model: loads parameters and computes live mastery."""
import json
from functools import lru_cache

from . import bkt, config, db
from .content import TOPICS
from .features import mastery_by_topic

PARAMS_PATH = config.MODELS_DIR / "bkt_params.json"


@lru_cache(maxsize=1)
def _load_cached(mtime):
    return json.loads(PARAMS_PATH.read_text())


def load_params():
    """Per-topic BKT parameters (+ 'default'). Uses library defaults if the model is not trained yet."""
    if PARAMS_PATH.exists():
        stored = _load_cached(PARAMS_PATH.stat().st_mtime)
        params = dict(stored.get("skills", {}))
        params["default"] = stored.get("default", bkt.DEFAULT_PARAMS)
        return params
    return {"default": bkt.DEFAULT_PARAMS}


def student_mastery(student_id):
    """Returns (mastery dict, attempts DataFrame) for one student."""
    att = db.attempts_df(student_id)
    return mastery_by_topic(att, load_params(), TOPICS), att
