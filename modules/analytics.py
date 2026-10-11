"""Class-level analytics for the teacher dashboard."""
from datetime import datetime

import pandas as pd

from . import dropout_model
from .content import TOPICS
from .features import FEATURES, compute_features, mastery_by_topic


def class_overview(attempts, students, bkt_params, model=None, now=None):
    """One row per student: features, per-topic mastery and (if a model is given) risk probability and level."""
    now = now or datetime.now()
    rows = []
    for _, st in students.iterrows():
        att = attempts[attempts["student_id"] == st["id"]].sort_values("ts")
        mastery = mastery_by_topic(att, bkt_params, TOPICS)
        row = {"student_id": int(st["id"]), "name": st["name"]}
        row.update(compute_features(att, mastery, now=now))
        row.update({f"m:{t}": v for t, v in mastery.items()})
        rows.append(row)
    df = pd.DataFrame(rows)
    if model is not None and len(df):
        df["risk"] = dropout_model.predict_risk(model, df)
        df["risk_level"] = df["risk"].map(dropout_model.risk_level)
    return df


def mastery_matrix(overview):
    cols = [f"m:{t}" for t in TOPICS]
    m = overview.set_index("name")[cols]
    m.columns = TOPICS
    return m


def top_reasons(model, overview_row_df, k=3):
    """The k features pushing a student's risk up the most (SHAP). Returns [(feature, shap_value, feature_value)]."""
    vals = dropout_model.explain(model, overview_row_df)[0]
    order = sorted(range(len(FEATURES)), key=lambda i: -vals[i])[:k]
    return [(FEATURES[i], float(vals[i]), float(overview_row_df.iloc[0][FEATURES[i]])) for i in order]
