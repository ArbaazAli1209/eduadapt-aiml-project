"""Synthetic student simulator.

Used to (1) train/test the models when no real dataset is available and (2) create a demo class
for the teacher dashboard. Students answer questions according to the BKT generative process, with
engagement (how often they practise) and ability (how fast they learn) as hidden traits.
Replace with real data (ASSISTments, OULAD, your own pilot) for the final results; see README.
"""
from datetime import datetime, timedelta

import numpy as np

from . import config
from .content import TOPICS

WINDOW_DAYS = 30
FIRST_NAMES = ["Aarav", "Diya", "Rohan", "Ananya", "Vikram", "Priya", "Arjun", "Meera", "Kabir", "Sneha",
                "Rahul", "Isha", "Aditya", "Kavya", "Nikhil", "Pooja", "Siddharth", "Riya", "Manish", "Neha",
                "Karan", "Anjali", "Deepak", "Sunita", "Harsh", "Lata", "Imran", "Fatima", "Gurpreet", "Tanvi"]


def true_topic_params(topics=TOPICS, seed=7):
    """Hidden 'true' BKT parameters per topic that the model should recover."""
    rng = np.random.default_rng(seed)
    return {t: {"p_init": float(rng.uniform(0.15, 0.40)), "p_learn": float(rng.uniform(0.08, 0.30)),
                "p_guess": float(rng.uniform(0.15, 0.25)), "p_slip": float(rng.uniform(0.05, 0.12))}
            for t in topics}


def simulate_student(rng, true_params, ability, engagement, now, topics=TOPICS):
    """Return a list of attempt dicts (topic, difficulty, correct, ts) sorted by time."""
    n_days = max(1, int(round(1 + 22 * engagement)))
    days = rng.choice(WINDOW_DAYS, size=min(n_days, WINDOW_DAYS), replace=False)
    # Highly engaged students were active recently; disengaged ones stopped earlier.
    days = np.clip(days - int((1 - engagement) * 12), 0, WINDOW_DAYS - 1)
    stamps = []
    for d in days:
        n_q = 1 + rng.poisson(1 + 3.5 * engagement)
        day_start = now - timedelta(days=int(WINDOW_DAYS - 1 - d))
        for _ in range(int(n_q)):
            stamps.append(day_start.replace(hour=8, minute=0, second=0, microsecond=0)
                          + timedelta(minutes=int(rng.integers(0, 700))))
    stamps.sort()
    known = {}
    for t in topics:
        p0 = float(np.clip(true_params[t]["p_init"] * (0.6 + 0.8 * ability), 0.01, 0.95))
        known[t] = rng.random() < p0
    attempts = []
    for ts in stamps:
        t = topics[int(rng.integers(0, len(topics)))]
        prm = true_params[t]
        p_right = (1 - prm["p_slip"]) if known[t] else prm["p_guess"]
        correct = int(rng.random() < p_right)
        attempts.append({"topic": t, "difficulty": "medium", "correct": correct, "ts": ts})
        if not known[t]:
            p_l = float(np.clip(prm["p_learn"] * (0.6 + 0.8 * ability), 0.0, 0.9))
            known[t] = rng.random() < p_l
    return attempts


def generate_class(n, seed=42, now=None, topics=TOPICS):
    """Generate n students with attempts. Returns a list of dicts (name, ability, engagement, attempts)."""
    rng = np.random.default_rng(seed)
    now = now or datetime.now()
    true_params = true_topic_params(topics)
    students = []
    for i in range(n):
        ability = float(rng.beta(5, 3))
        engagement = float(rng.beta(4, 3))
        students.append({
            "name": f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {chr(65 + (i // len(FIRST_NAMES)) % 26)}.{i + 1:03d}",
            "ability": ability, "engagement": engagement,
            "attempts": simulate_student(rng, true_params, ability, engagement, now, topics),
        })
    # Ground-truth risk label: the 28% of students with the lowest ability + engagement combination.
    latent = np.array([0.5 * (1 - s["ability"]) + 0.5 * (1 - s["engagement"]) + rng.normal(0, 0.06) for s in students])
    cut = np.quantile(latent, 0.72)
    for s, v in zip(students, latent):
        s["at_risk"] = int(v > cut)
    return students
