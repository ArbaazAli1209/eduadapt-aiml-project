"""Train the BKT and dropout models. Used by train_models.py and by the apps if models are missing."""
import json
from datetime import datetime

import numpy as np
import pandas as pd

from . import bkt, config, dropout_model, synthetic
from .content import TOPICS
from .features import FEATURES


def load_assistments(path, max_skills=20, min_students=100):
    """Read an ASSISTments skill-builder CSV into {skill: [sequence per student]}."""
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    df = df.dropna(subset=["skill_name"])
    df = df[df["correct"].isin([0, 1])]
    if "order_id" in df.columns:
        df = df.sort_values("order_id")
    out = {}
    for skill, sub in df.groupby("skill_name"):
        seqs = [g["correct"].astype(int).tolist() for _, g in sub.groupby("user_id")]
        if len(seqs) >= min_students:
            out[skill] = seqs
    top = sorted(out, key=lambda s: -len(out[s]))[:max_skills]
    return {s: out[s] for s in top}


def _fit_all(seqs_by_skill, seed):
    rng = np.random.default_rng(seed)
    fitted, aucs = {}, {}
    for skill, seqs in seqs_by_skill.items():
        idx = rng.permutation(len(seqs))
        cut = int(0.8 * len(seqs))
        train = [seqs[i] for i in idx[:cut]]
        test = [seqs[i] for i in idx[cut:]]
        prm = bkt.fit_skill(train)
        fitted[skill] = prm
        aucs[skill] = bkt.evaluate_auc(test, prm)
    return fitted, aucs


def train_bkt(students=None, assistments_csv=None, seed=42):
    if assistments_csv:
        seqs = load_assistments(assistments_csv)
        mode = "assistments"
    else:
        seqs = {t: [[a["correct"] for a in s["attempts"] if a["topic"] == t] for s in students] for t in TOPICS}
        mode = "synthetic"
    fitted, aucs = _fit_all(seqs, seed)
    default = {k: float(np.mean([p[k] for p in fitted.values()])) for k in bkt.PARAM_NAMES}
    valid = [v for v in aucs.values() if v is not None]
    metrics = {"mode": mode, "mean_auc": float(np.mean(valid)) if valid else None,
               "auc_per_skill": aucs, "n_skills": len(fitted)}
    config.MODELS_DIR.mkdir(exist_ok=True)
    (config.MODELS_DIR / "bkt_params.json").write_text(json.dumps(
        {"mode": mode, "skills": fitted, "default": default, "metrics": metrics}, indent=2))
    from . import mastery
    mastery._load_cached.cache_clear()
    return fitted, default, metrics


def make_plots(model, x_test):
    """Save SHAP summary and feature-importance plots for the report."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import shap
        config.REPORTS_DIR.mkdir(exist_ok=True)
        vals = shap.TreeExplainer(model).shap_values(x_test[FEATURES])
        shap.summary_plot(vals, x_test[FEATURES], show=False)
        plt.tight_layout()
        plt.savefig(config.REPORTS_DIR / "shap_summary.png", dpi=150)
        plt.close()
        return True
    except Exception:
        return False


def train_all(n_students=1500, seed=42, assistments_csv=None, dropout_csv=None, plots=True, verbose=True):
    now = datetime.now()
    students = synthetic.generate_class(n_students, seed=seed, now=now)
    if verbose:
        print(f"[1/3] Simulated {n_students} students ({sum(len(s['attempts']) for s in students)} attempts)")
    fitted, default, bkt_metrics = train_bkt(students, assistments_csv, seed)
    if verbose:
        print(f"[2/3] BKT trained ({bkt_metrics['mode']} data): mean held-out AUC = {bkt_metrics['mean_auc']:.3f}")
    params = dict(fitted)
    params["default"] = default
    if dropout_csv:
        df = pd.read_csv(dropout_csv)
        missing = [c for c in FEATURES + ["at_risk"] if c not in df.columns]
        if missing:
            raise ValueError(f"{dropout_csv} is missing columns: {missing}")
    else:
        df = dropout_model.build_training_frame(students, params, now=now)
    model, drop_metrics, x_test = dropout_model.train(df, seed)
    dropout_model.save(model, drop_metrics)
    if verbose:
        print("[3/3] Dropout model: " + ", ".join(f"{k}={v:.3f}" for k, v in drop_metrics.items()
                                                   if isinstance(v, float)))
    shap_ok = make_plots(model, x_test) if plots else False
    config.REPORTS_DIR.mkdir(exist_ok=True)
    report = {"trained_at": now.isoformat(timespec="seconds"), "bkt": bkt_metrics, "dropout": drop_metrics,
              "note": "Synthetic data unless --assistments / --dropout-csv were given."}
    (config.REPORTS_DIR / "metrics.json").write_text(json.dumps(report, indent=2))
    if verbose:
        print(f"Saved models to {config.MODELS_DIR} and report to {config.REPORTS_DIR}"
              + (" (with SHAP plot)" if shap_ok else ""))
    return report


def ensure_models():
    """Train quickly on synthetic data if no trained models exist yet (so the app works out of the box)."""
    if not (config.MODELS_DIR / "bkt_params.json").exists() or not dropout_model.MODEL_PATH.exists():
        train_all(n_students=800, plots=False, verbose=False)
