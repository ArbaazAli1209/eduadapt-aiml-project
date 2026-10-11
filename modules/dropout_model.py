"""Dropout / at-risk predictor: XGBoost classifier + SHAP explanations."""
import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from . import config
from .features import FEATURES, compute_features, mastery_by_topic

MODEL_PATH = config.MODELS_DIR / "dropout_xgb.pkl"
META_PATH = config.MODELS_DIR / "dropout_meta.json"


def build_training_frame(students, bkt_params, now=None):
    """students: output of synthetic.generate_class(). Returns DataFrame of FEATURES + at_risk."""
    now = now or datetime.now()
    rows = []
    for s in students:
        att = pd.DataFrame(s["attempts"], columns=["topic", "difficulty", "correct", "ts"])
        mastery = mastery_by_topic(att, bkt_params)
        feats = compute_features(att, mastery, now=now)
        feats["at_risk"] = s["at_risk"]
        rows.append(feats)
    return pd.DataFrame(rows)


def train(df, seed=42):
    """Train and evaluate. Returns (model, metrics dict, X_test)."""
    x, y = df[FEATURES], df["at_risk"]
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.2, stratify=y, random_state=seed)
    pos_weight = float((ytr == 0).sum() / max((ytr == 1).sum(), 1))
    model = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.08, subsample=0.9,
                          colsample_bytree=0.9, scale_pos_weight=pos_weight, eval_metric="logloss",
                          random_state=seed)
    model.fit(xtr, ytr)
    proba = model.predict_proba(xte)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "auc": float(roc_auc_score(yte, proba)),
        "precision": float(precision_score(yte, pred, zero_division=0)),
        "recall": float(recall_score(yte, pred, zero_division=0)),
        "f1": float(f1_score(yte, pred, zero_division=0)),
        "n_train": int(len(xtr)), "n_test": int(len(xte)), "positive_rate": float(y.mean()),
    }
    return model, metrics, xte


def save(model, metrics):
    config.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    META_PATH.write_text(json.dumps(metrics, indent=2))


def load():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def predict_risk(model, feature_rows):
    """feature_rows: DataFrame with FEATURES columns. Returns array of risk probabilities."""
    return model.predict_proba(feature_rows[FEATURES])[:, 1]


def risk_level(p):
    return "High" if p >= 0.6 else "Medium" if p >= 0.3 else "Low"


def explain(model, feature_rows):
    """SHAP values (rows x features). Falls back to global feature importance if SHAP is unavailable."""
    try:
        import shap
        values = shap.TreeExplainer(model).shap_values(feature_rows[FEATURES])
        return np.asarray(values)
    except Exception:
        imp = model.feature_importances_
        return np.tile(imp, (len(feature_rows), 1))
