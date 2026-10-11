"""EduAdapt student app.  Run:  streamlit run app.py"""
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from modules import config, db, language, mastery as mastery_svc, quiz_generator, recommender, training
from modules.content import DIFF_HI, LESSONS, TOPIC_HI, TOPICS, UI

st.set_page_config(page_title="EduAdapt", page_icon="📚", layout="wide")
training.ensure_models()

# ---------------------------------------------------------------- sidebar
lang_label = st.sidebar.radio("Language / भाषा", list(UI), horizontal=True, key="lang")
T = UI[lang_label]
code = language.LANG_CODES[lang_label]
hi = code == "hi"
name = st.sidebar.text_input(T["your_name"], key="name").strip()
st.sidebar.caption("Class 8 Mathematics (NCERT)")
st.sidebar.page_link("pages/1_Teacher_Dashboard.py", label="Teacher dashboard")


def topic_name(t):
    return TOPIC_HI[t] if hi else t


def q_text(q):
    if hi:
        return q.get("question_hi") or language.translate(q["question"], "hi")
    return q["question"]


def e_text(q):
    if hi:
        return q.get("explanation_hi") or language.translate(q["explanation"], "hi")
    return q["explanation"]


st.title(f"📚 {T['title']}")
st.caption(T["tagline"])

if not name:
    st.info(T["enter_name"])
    st.stop()

# ---------------------------------------------------------------- student state
sid = db.get_or_create_student(name, lang=lang_label)
if st.session_state.get("sid") != sid:           # a different student logged in: reset quiz state
    for k in ("quiz", "quiz_topic", "quiz_diff", "results", "quiz_nonce", "diagnostic"):
        st.session_state.pop(k, None)
    st.session_state["sid"] = sid
mastery_now, att = mastery_svc.student_mastery(sid)
n_att = len(att)
focus = recommender.recommend_next(mastery_now) if n_att else None

# ---------------------------------------------------------------- overview
left, right = st.columns([3, 2])
with left:
    st.subheader(T["mastery"])
    dfm = pd.DataFrame({T["topic"]: [topic_name(t) for t in TOPICS], T["mastery_axis"]: [mastery_now[t] for t in TOPICS]})
    fig = px.bar(dfm, x=T["mastery_axis"], y=T["topic"], orientation="h", range_x=[0, 1])
    fig.add_vline(x=config.MASTERY_THRESHOLD, line_dash="dash", line_color="#C5192D")
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_traces(marker_color="#16324F")
    st.plotly_chart(fig, width="stretch")
with right:
    c1, c2 = st.columns(2)
    c1.metric(T["attempts"], n_att)
    c2.metric(T["accuracy"], f"{att['correct'].mean():.0%}" if n_att else "-")
    if focus:
        st.markdown(f"**{T['recommended']}:** {topic_name(focus)}")
        st.caption(f"{T['weak'] if mastery_now[focus] < config.MASTERY_THRESHOLD else T['strong']} "
                   f"({mastery_now[focus]:.2f})")
        related = recommender.similar_topics(focus)
        st.caption(f"{T['related']}: " + ", ".join(topic_name(t) for t in related))
    else:
        st.warning(T["new_student"])

# ---------------------------------------------------------------- quiz
st.divider()
seen = db.seen_question_ids(sid)
starting = st.session_state.get("quiz") is None and st.session_state.get("results") is None

if starting:
    if n_att == 0:
        if st.button(T["start_diag"], type="primary"):
            st.session_state.quiz = quiz_generator.diagnostic_questions(TOPICS, exclude=seen)
            st.session_state.quiz_topic = None
            st.session_state.diagnostic = True
            st.session_state.quiz_nonce = random.random()
            st.rerun()
    else:
        diff = recommender.difficulty_for(mastery_now[focus])
        st.markdown(f"**{T['start_quiz']}**: {topic_name(focus)} · {T['difficulty']}: {DIFF_HI[diff] if hi else diff}")
        if st.button(T["start_quiz"], type="primary"):
            st.session_state.quiz = quiz_generator.generate_questions(focus, diff, config.QUIZ_SIZE, exclude=seen)
            st.session_state.quiz_topic, st.session_state.quiz_diff = focus, diff
            st.session_state.diagnostic = False
            st.session_state.quiz_nonce = random.random()
            st.rerun()

if st.session_state.get("quiz") is not None:
    quiz = st.session_state.quiz
    with st.form("quiz_form"):
        picks = []
        for i, q in enumerate(quiz):
            label = f"{i + 1}. [{topic_name(q['topic'])}] {q_text(q)}"
            picks.append(st.radio(label, q["options"], index=None, key=f"q{st.session_state.quiz_nonce}_{i}"))
        submitted = st.form_submit_button(T["submit"])
    if submitted:
        if any(p is None for p in picks):
            st.warning(T["select_all"])
        else:
            results = []
            for q, pick in zip(quiz, picks):
                ok = pick == q["answer"]
                db.log_attempt(sid, q["topic"], q["difficulty"], q["id"], ok)
                results.append({"q": q, "pick": pick, "ok": ok})
            st.session_state.results = results
            st.session_state.quiz = None
            st.rerun()

if st.session_state.get("results") is not None:
    for i, r in enumerate(st.session_state.results):
        q = r["q"]
        (st.success if r["ok"] else st.error)(
            f"{i + 1}. {T['correct'] if r['ok'] else T['incorrect']} {T['answer']}: {q['answer']}")
        st.caption(f"{T['explanation']}: {e_text(q)}")
    if st.button(T["next_quiz"], type="primary"):
        st.session_state.results = None
        st.rerun()

# ---------------------------------------------------------------- lesson + doubts
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    lesson_topic = st.selectbox(T["lesson"], TOPICS, index=TOPICS.index(focus) if focus else 0, format_func=topic_name)
    lesson = LESSONS[lesson_topic][code]
    st.write(lesson)
    if language.tts_available() and st.button(f"🔊 {T['listen']}", key="listen_lesson"):
        audio = language.text_to_speech(lesson, code)
        if audio:
            st.audio(audio, format="audio/mp3")
        else:
            st.caption("Audio needs an internet connection (gTTS).")
with col_b:
    st.markdown(f"**{T['ask_doubt']}**")
    doubt = st.text_input(T["ask_doubt"], placeholder=T["doubt_hint"], label_visibility="collapsed", key="doubt")
    if language.stt_available() and hasattr(st, "audio_input"):
        clip = st.audio_input(T["voice_doubt"])
        if clip is not None:
            heard = language.speech_to_text(clip.getvalue(), code)
            if heard:
                st.caption(f"🎙 {heard}")
                doubt = heard
    if doubt:
        res = quiz_generator.answer_doubt(doubt)
        st.markdown(f"**{topic_name(res['topic'])}**")
        st.write(LESSONS[res["topic"]][code] if (hi and res["source"] == "lesson") else res["answer"])
