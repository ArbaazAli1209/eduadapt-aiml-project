import random
from datetime import datetime

import numpy as np
import pandas as pd

from modules import analytics, bkt, db, dropout_model, quiz_generator, recommender, synthetic
from modules.content import PREREQS, QUESTION_BANK, TOPICS
from modules.features import FEATURES, compute_features, mastery_by_topic


def test_question_bank_is_valid():
    assert len(QUESTION_BANK) >= 36
    assert all(quiz_generator.validate_question(q) for q in QUESTION_BANK)
    assert len({q["id"] for q in QUESTION_BANK}) == len(QUESTION_BANK)


def test_bkt_update_direction():
    prm = bkt.DEFAULT_PARAMS
    p = 0.4
    assert bkt.update(p, 1, prm) > p            # a correct answer raises mastery
    assert bkt.update(p, 0, prm) < bkt.update(p, 1, prm)
    assert bkt.final_mastery([1, 1, 1, 1, 1], prm) > bkt.final_mastery([0, 0, 0, 0, 0], prm)
    assert 0 <= bkt.final_mastery([0, 1, 0, 1], prm) <= 1


def test_bkt_recovers_parameters_and_predicts():
    cls = synthetic.generate_class(400, seed=3)
    t = TOPICS[0]
    seqs = [[a["correct"] for a in s["attempts"] if a["topic"] == t] for s in cls]
    train, test = seqs[:320], seqs[320:]
    prm = bkt.fit_skill(train)
    assert set(prm) == set(bkt.PARAM_NAMES)
    assert bkt.evaluate_auc(test, prm) > 0.65


def test_quiz_validation_and_parsing():
    good = {"question": "2+2?", "options": ["3", "4", "5", "6"], "answer": "4", "explanation": "."}
    assert quiz_generator.validate_question(good)
    assert not quiz_generator.validate_question({**good, "answer": "7"})
    assert not quiz_generator.validate_question({**good, "options": ["3", "3", "5", "6"]})
    assert not quiz_generator.validate_question({"question": "x"})
    raw = 'Here you go:\n```json\n[{"question": "q"}]\n```'
    assert quiz_generator.parse_llm_json(raw) == [{"question": "q"}]


def test_generate_questions_adaptive_and_no_repeats():
    rng = random.Random(1)
    qs = quiz_generator.generate_questions("Percentages", "easy", 2, rng=rng)
    assert len(qs) == 2 and all(q["difficulty"] == "easy" for q in qs)
    seen = {q["id"] for q in qs}
    more = quiz_generator.generate_questions("Percentages", "easy", 2, exclude=seen, rng=rng)
    assert not seen & {q["id"] for q in more}
    assert all(quiz_generator.validate_question(q) for q in qs + more)
    diag = quiz_generator.diagnostic_questions(TOPICS, rng=rng)
    assert [q["topic"] for q in diag] == TOPICS


def test_recommender_respects_prerequisites():
    m = {t: 0.9 for t in TOPICS}
    m["Algebraic Expressions"], m["Linear Equations"] = 0.3, 0.2
    assert recommender.recommend_next(m) == "Algebraic Expressions"   # prerequisite first
    m2 = {t: 0.9 for t in TOPICS}
    m2["Percentages"] = 0.2
    assert recommender.recommend_next(m2) == "Percentages"
    assert recommender.difficulty_for(0.2) == "easy" and recommender.difficulty_for(0.9) == "hard"
    assert recommender.retrieve("how do I find the area of a circle?")[0] == "Mensuration"
    assert recommender.retrieve("square root of 144")[0] == "Squares and Square Roots"


def test_database_roundtrip():
    sid = db.get_or_create_student("Test Student")
    assert db.get_or_create_student("test student") == sid       # case-insensitive
    db.log_attempt(sid, "Percentages", "easy", "bank-001", True)
    db.log_attempt(sid, "Percentages", "easy", "bank-002", False)
    df = db.attempts_df(sid)
    assert len(df) == 2 and df["correct"].tolist() == [1, 0]
    assert "bank-001" in db.seen_question_ids(sid)


def test_features_and_dropout_pipeline():
    now = datetime.now()
    cls = synthetic.generate_class(500, seed=5, now=now)
    params = {t: bkt.DEFAULT_PARAMS for t in TOPICS}
    df = dropout_model.build_training_frame(cls, params, now=now)
    assert set(FEATURES) <= set(df.columns)
    model, metrics, x_test = dropout_model.train(df, seed=1)
    assert metrics["auc"] > 0.7
    risk = dropout_model.predict_risk(model, x_test)
    assert ((risk >= 0) & (risk <= 1)).all()
    shap_vals = dropout_model.explain(model, x_test.head(3))
    assert shap_vals.shape == (3, len(FEATURES))
    # an inactive, low-accuracy student must be riskier than an active, accurate one
    bad = {"accuracy": .2, "attempts": 8, "active_days": 2, "mean_mastery": .25, "weak_topics": 6,
           "recent_accuracy": .1, "trend": -.1, "days_since_last": 25}
    good = {"accuracy": .85, "attempts": 120, "active_days": 20, "mean_mastery": .85, "weak_topics": 0,
            "recent_accuracy": .9, "trend": .05, "days_since_last": 1}
    r = dropout_model.predict_risk(model, pd.DataFrame([bad, good]))
    assert r[0] > r[1]


def test_class_overview_for_dashboard():
    now = datetime.now()
    cls = synthetic.generate_class(6, seed=9, now=now)
    sids, rows = [], []
    for s in cls:
        sid = db.get_or_create_student("T-" + s["name"], is_demo=1)
        rows += [(sid, a["topic"], a["difficulty"], None, a["correct"], a["ts"]) for a in s["attempts"]]
    db.bulk_insert_attempts(rows)
    params = {t: bkt.DEFAULT_PARAMS for t in TOPICS}
    df = dropout_model.build_training_frame(synthetic.generate_class(300, seed=2, now=now), params, now=now)
    model, _, _ = dropout_model.train(df)
    ov = analytics.class_overview(db.attempts_df(), db.students_df(), params, model, now=now)
    assert {"risk", "risk_level"} <= set(ov.columns)
    assert analytics.mastery_matrix(ov).shape[1] == len(TOPICS)
    reasons = analytics.top_reasons(model, ov.head(1))
    assert len(reasons) == 3
