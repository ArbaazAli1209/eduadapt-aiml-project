"""Topic recommendation (prerequisite-aware) and lesson retrieval (TF-IDF, works for English and Hindi)."""
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import config
from .content import LESSONS, PREREQS, TOPIC_HI, TOPICS


def recommend_next(mastery, prereqs=PREREQS, threshold=None):
    """Weakest topic whose prerequisites are already solid; if every weak topic is blocked, the weakest prerequisite."""
    threshold = config.MASTERY_THRESHOLD if threshold is None else threshold
    ranked = sorted(mastery.items(), key=lambda kv: kv[1])
    weak = [t for t, m in ranked if m < threshold]
    if not weak:
        return ranked[0][0]                      # everything is strong: revise the least-strong topic
    for t in weak:
        if all(mastery.get(p, 1.0) >= threshold for p in prereqs.get(t, [])):
            return t
    unmet = [p for p in prereqs.get(weak[0], []) if mastery.get(p, 1.0) < threshold]
    return min(unmet, key=lambda p: mastery[p]) if unmet else weak[0]


def difficulty_for(m):
    """Map a mastery estimate to a question difficulty."""
    if m < config.EASY_BELOW:
        return "easy"
    return "hard" if m > config.HARD_ABOVE else "medium"


@lru_cache(maxsize=1)
def _index():
    docs = [f"{t} {TOPIC_HI[t]} {LESSONS[t]['en']} {LESSONS[t]['hi']}" for t in TOPICS]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)
    return vec, vec.fit_transform(docs)


def retrieve(query):
    """Best matching topic for a free-text doubt. Returns (topic, similarity score)."""
    vec, mat = _index()
    sims = cosine_similarity(vec.transform([query]), mat)[0]
    i = int(sims.argmax())
    return TOPICS[i], float(sims[i])


def similar_topics(topic, k=2):
    """Topics whose lessons are most similar to the given one (content-based recommendation)."""
    _, mat = _index()
    i = TOPICS.index(topic)
    sims = cosine_similarity(mat[i], mat)[0]
    order = [j for j in sims.argsort()[::-1] if j != i][:k]
    return [TOPICS[j] for j in order]
