"""Bayesian Knowledge Tracing (BKT), implemented from scratch with NumPy.

BKT models a hidden state "student knows the skill" with four parameters:
  p_init  : probability the skill is already known before practice
  p_learn : probability of learning the skill after each attempt
  p_guess : probability of answering correctly without knowing
  p_slip  : probability of answering wrongly despite knowing
After every answer the posterior P(known) is updated with Bayes' rule.
"""
from itertools import product

import numpy as np
from sklearn.metrics import roc_auc_score

DEFAULT_PARAMS = {"p_init": 0.3, "p_learn": 0.15, "p_guess": 0.2, "p_slip": 0.1}
PARAM_NAMES = list(DEFAULT_PARAMS)

# Search grid for parameter fitting (kept with guess <= 0.3 and slip <= 0.2 to avoid degenerate fits)
GRID = {
    "p_init": [0.05, 0.15, 0.30, 0.45, 0.60],
    "p_learn": [0.03, 0.08, 0.15, 0.25, 0.40],
    "p_guess": [0.05, 0.10, 0.20, 0.30],
    "p_slip": [0.03, 0.08, 0.15, 0.20],
}
_EPS = 1e-9


def p_correct(p_know, prm):
    """Probability that the next answer is correct."""
    return p_know * (1 - prm["p_slip"]) + (1 - p_know) * prm["p_guess"]


def update(p_know, correct, prm):
    """One Bayesian update after observing an answer, then the learning transition."""
    pc = p_correct(p_know, prm)
    if correct:
        posterior = p_know * (1 - prm["p_slip"]) / max(pc, _EPS)
    else:
        posterior = p_know * prm["p_slip"] / max(1 - pc, _EPS)
    return posterior + (1 - posterior) * prm["p_learn"]


def final_mastery(sequence, prm):
    """Mastery estimate P(known) after a whole sequence of 0/1 answers."""
    p = prm["p_init"]
    for y in sequence:
        p = update(p, int(y), prm)
    return float(p)


def mastery_curve(sequence, prm):
    """P(known) before the first answer and after each answer."""
    p = prm["p_init"]
    out = [p]
    for y in sequence:
        p = update(p, int(y), prm)
        out.append(p)
    return out


def _pad(seqs):
    t_max = max(len(s) for s in seqs)
    x = -np.ones((len(seqs), t_max), dtype=int)
    for i, s in enumerate(seqs):
        x[i, :len(s)] = s
    return x


def _run(x, prm):
    """Vectorised forward pass over padded sequences. Returns (log-likelihood, predictions)."""
    g, s, lrn = prm["p_guess"], prm["p_slip"], prm["p_learn"]
    p = np.full(x.shape[0], prm["p_init"], dtype=float)
    preds = np.full(x.shape, np.nan)
    ll = 0.0
    for t in range(x.shape[1]):
        y = x[:, t]
        mask = y >= 0
        pc = p * (1 - s) + (1 - p) * g
        preds[:, t] = np.where(mask, pc, np.nan)
        lik = np.where(y == 1, pc, 1 - pc)
        ll += np.log(np.clip(lik[mask], _EPS, None)).sum()
        post = np.where(y == 1, p * (1 - s) / np.clip(pc, _EPS, None), p * s / np.clip(1 - pc, _EPS, None))
        p = np.where(mask, post + (1 - post) * lrn, p)
    return ll, preds


def fit_skill(sequences, grid=GRID):
    """Fit the four BKT parameters of one skill by grid search on the log-likelihood."""
    sequences = [s for s in sequences if len(s) > 0]
    if len(sequences) < 5:
        return dict(DEFAULT_PARAMS)
    x = _pad(sequences)
    best, best_ll = None, -np.inf
    for vals in product(*(grid[k] for k in PARAM_NAMES)):
        prm = dict(zip(PARAM_NAMES, vals))
        ll, _ = _run(x, prm)
        if ll > best_ll:
            best, best_ll = prm, ll
    return best


def evaluate_auc(sequences, prm):
    """AUC of the model's P(correct) predictions on held-out sequences (None if undefined)."""
    sequences = [s for s in sequences if len(s) > 0]
    if not sequences:
        return None
    x = _pad(sequences)
    _, preds = _run(x, prm)
    mask = x >= 0
    y, p = x[mask], preds[mask]
    if len(set(y.tolist())) < 2:
        return None
    return float(roc_auc_score(y, p))
