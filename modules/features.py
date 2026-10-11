"""Turn a student's attempt log into the features used by the dropout-risk model."""
from datetime import datetime

import numpy as np
import pandas as pd

from . import bkt, config
from .content import TOPICS

FEATURES = ["accuracy", "attempts", "active_days", "mean_mastery", "weak_topics",
            "recent_accuracy", "trend", "days_since_last"]

FEATURE_LABELS = {
    "accuracy": "Overall accuracy",
    "attempts": "Questions answered",
    "active_days": "Days active",
    "mean_mastery": "Average mastery",
    "weak_topics": "Number of weak topics",
    "recent_accuracy": "Accuracy on last 10 answers",
    "trend": "Recent accuracy minus overall accuracy",
    "days_since_last": "Days since last activity",
}


def mastery_by_topic(attempts, bkt_params, topics=TOPICS):
    """BKT mastery estimate for every topic from one student's attempts (a DataFrame)."""
    out = {}
    for t in topics:
        prm = bkt_params.get(t) or bkt_params.get("default") or bkt.DEFAULT_PARAMS
        seq = attempts.loc[attempts["topic"] == t, "correct"].tolist() if len(attempts) else []
        out[t] = bkt.final_mastery(seq, prm)
    return out


def compute_features(attempts, mastery, now=None):
    """attempts: DataFrame with topic, correct, ts (sorted by ts). Returns a dict keyed by FEATURES."""
    now = now or datetime.now()
    n = len(attempts)
    weak = sum(1 for v in mastery.values() if v < config.MASTERY_THRESHOLD)
    mean_m = float(np.mean(list(mastery.values()))) if mastery else 0.0
    if n == 0:
        return {"accuracy": 0.0, "attempts": 0, "active_days": 0, "mean_mastery": mean_m,
                "weak_topics": weak, "recent_accuracy": 0.0, "trend": 0.0, "days_since_last": 30.0}
    acc = float(attempts["correct"].mean())
    recent = float(attempts["correct"].tail(10).mean())
    last = pd.to_datetime(attempts["ts"]).max()
    return {
        "accuracy": acc, "attempts": int(n),
        "active_days": int(pd.to_datetime(attempts["ts"]).dt.date.nunique()),
        "mean_mastery": mean_m, "weak_topics": int(weak),
        "recent_accuracy": recent, "trend": recent - acc,
        "days_since_last": float(max((now - last.to_pydatetime()).total_seconds() / 86400, 0.0)),
    }
