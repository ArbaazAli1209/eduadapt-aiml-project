"""Adaptive quiz generation.

Backends (EDUADAPT_LLM):
  none    -> curated question bank (default, fully offline)
  hf      -> IBM Granite (open weights) via Hugging Face Transformers, grounded on the lesson text
  ollama  -> any model served locally by Ollama
LLM output is validated; invalid or failed generations silently fall back to the question bank.
"""
import hashlib
import json
import random
from functools import lru_cache

import requests

from . import config
from .content import LESSONS, QUESTION_BANK

DIFFICULTIES = ["easy", "medium", "hard"]


def validate_question(q):
    """A question is valid if it has text, four distinct options, and the answer is one of them."""
    try:
        opts = q["options"]
        return (isinstance(q["question"], str) and q["question"].strip() != ""
                and isinstance(opts, list) and len(opts) == 4
                and all(isinstance(o, str) and o.strip() for o in opts)
                and len({o.strip().lower() for o in opts}) == 4
                and q["answer"] in opts
                and isinstance(q.get("explanation", ""), str))
    except (KeyError, TypeError):
        return False


def _prompt(topic, difficulty, n):
    return f"""You are a Class 8 mathematics teacher (NCERT syllabus).
Reference lesson: {LESSONS[topic]['en']}
Write {n} multiple-choice questions on "{topic}" at {difficulty} difficulty.
Return ONLY a JSON list. Each item must have the keys:
"question" (string), "options" (list of exactly 4 different strings), "answer" (must be exactly one of the options), "explanation" (one short sentence).
Make sure the answer is mathematically correct."""


@lru_cache(maxsize=1)
def _hf_pipeline():
    from transformers import pipeline
    return pipeline("text-generation", model=config.HF_MODEL)


def _call_llm(prompt):
    if config.LLM_BACKEND == "hf":
        out = _hf_pipeline()([{"role": "user", "content": prompt}], max_new_tokens=700, do_sample=True,
                             temperature=0.3, return_full_text=False)
        text = out[0]["generated_text"]
        if isinstance(text, list):
            text = text[-1]["content"]
        return text
    if config.LLM_BACKEND == "ollama":
        r = requests.post(f"{config.OLLAMA_URL}/api/generate", timeout=120,
                          json={"model": config.OLLAMA_MODEL, "prompt": prompt, "stream": False})
        r.raise_for_status()
        return r.json()["response"]
    raise RuntimeError("LLM backend disabled")


def parse_llm_json(raw):
    """Extract the JSON list from a model response (ignores text around it and markdown fences)."""
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON list found")
    return json.loads(raw[start:end + 1])


def _llm_questions(topic, difficulty, n):
    items = parse_llm_json(_call_llm(_prompt(topic, difficulty, n)))
    out = []
    for i, q in enumerate(items):
        q = {"id": "llm-" + hashlib.md5(str(q.get("question", "")).encode()).hexdigest()[:10], "topic": topic, "difficulty": difficulty,
             "question": q.get("question", ""), "options": q.get("options", []), "answer": q.get("answer", ""),
             "explanation": q.get("explanation", ""), "source": "llm"}
        if validate_question(q):
            out.append(q)
    return out


def generate_questions(topic, difficulty, n=3, exclude=(), rng=None):
    """Return up to n validated questions for a topic, preferring the requested difficulty."""
    rng = rng or random
    chosen = []
    if config.LLM_BACKEND != "none":
        try:
            chosen += _llm_questions(topic, difficulty, n)[:n]
        except Exception:
            pass
    ids = {q["id"] for q in chosen} | set(exclude)
    pool = [q for q in QUESTION_BANK if q["topic"] == topic]
    order = [difficulty] + [d for d in DIFFICULTIES if d != difficulty]
    for d in order:                                   # requested difficulty first, then neighbours
        cands = [q for q in pool if q["difficulty"] == d and q["id"] not in ids]
        rng.shuffle(cands)
        for q in cands:
            if len(chosen) >= n:
                break
            chosen.append(q)
            ids.add(q["id"])
    if len(chosen) < n:                               # student has seen everything: allow repeats
        cands = [q for q in pool if q["id"] not in {c["id"] for c in chosen}]
        rng.shuffle(cands)
        chosen += cands[:n - len(chosen)]
    return [_shuffled(q, rng) for q in chosen[:n]]


def diagnostic_questions(topics, exclude=(), rng=None):
    """One easy/medium question per topic for the first-time diagnostic quiz."""
    rng = rng or random
    out = []
    for t in topics:
        cands = [q for q in QUESTION_BANK if q["topic"] == t and q["difficulty"] in ("easy", "medium")
                 and q["id"] not in set(exclude)] or [q for q in QUESTION_BANK if q["topic"] == t]
        out.append(_shuffled(rng.choice(cands), rng))
    return out


def _shuffled(q, rng):
    q = dict(q)
    opts = list(q["options"])
    rng.shuffle(opts)
    q["options"] = opts
    return q


def answer_doubt(text):
    """Answer a free-text doubt. Retrieval picks the best lesson; an LLM (if enabled) explains it in context."""
    from .recommender import retrieve
    topic, score = retrieve(text)
    lesson = LESSONS[topic]["en"]
    if config.LLM_BACKEND != "none":
        try:
            prompt = (f"You are a friendly Class 8 maths teacher. Use this lesson as reference: {lesson}\n"
                      f"Answer the student's doubt simply in 3 sentences or fewer.\nDoubt: {text}")
            return {"topic": topic, "score": score, "answer": _call_llm(prompt).strip(), "source": "llm"}
        except Exception:
            pass
    return {"topic": topic, "score": score, "answer": lesson, "source": "lesson"}
