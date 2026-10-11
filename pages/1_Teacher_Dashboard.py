"""Teacher dashboard: class mastery heatmap, at-risk students and the reasons behind each flag."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import plotly.express as px
import streamlit as st

from modules import analytics, db, dropout_model, mastery as mastery_svc, synthetic, training
from modules.content import TOPICS
from modules.features import FEATURE_LABELS, FEATURES

st.set_page_config(page_title="EduAdapt · Teacher", page_icon="📊", layout="wide")
st.title("📊 Teacher dashboard")
training.ensure_models()
model = dropout_model.load()
params = mastery_svc.load_params()

students = db.students_df()
with st.sidebar:
    st.subheader("Demo data")
    st.caption("Adds 30 simulated students so you can explore the dashboard.")
    if st.button("Load demo class (30 students)"):
        cls = synthetic.generate_class(30, seed=int(datetime.now().timestamp()) % 10000, now=datetime.now())
        rows = []
        for s in cls:
            sid = db.get_or_create_student(s["name"], is_demo=1)
            rows += [(sid, a["topic"], a["difficulty"], None, a["correct"], a["ts"]) for a in s["attempts"]]
        db.bulk_insert_attempts(rows)
        st.rerun()
    if st.button("Remove demo students"):
        db.clear_demo()
        st.rerun()

if students.empty:
    st.info("No students yet. Students appear here after they take quizzes in the student app, "
            "or load the demo class from the sidebar.")
    st.stop()

attempts = db.attempts_df()
overview = analytics.class_overview(attempts, students, params, model)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", len(overview))
c2.metric("High-risk students", int((overview["risk_level"] == "High").sum()))
c3.metric("Average accuracy", f"{overview['accuracy'].mean():.0%}")
c4.metric("Average mastery", f"{overview['mean_mastery'].mean():.2f}")

st.subheader("Class mastery by topic")
matrix = analytics.mastery_matrix(overview)
fig = px.imshow(matrix, zmin=0, zmax=1, color_continuous_scale="RdYlGn", aspect="auto",
                labels=dict(color="Mastery"))
fig.update_layout(height=max(300, 22 * len(matrix)), margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, width="stretch")
weak_topics = matrix.mean().sort_values().head(2)
st.caption("Weakest topics across the class: " + ", ".join(f"{t} ({v:.2f})" for t, v in weak_topics.items()))

st.subheader("Students at risk")
table = overview[["name", "attempts", "accuracy", "active_days", "days_since_last", "mean_mastery", "risk", "risk_level"]]
table = table.sort_values("risk", ascending=False).rename(columns={
    "name": "Student", "attempts": "Answers", "accuracy": "Accuracy", "active_days": "Active days",
    "days_since_last": "Days inactive", "mean_mastery": "Avg mastery", "risk": "Risk score", "risk_level": "Level"})
st.dataframe(table.style.format({"Accuracy": "{:.0%}", "Days inactive": "{:.0f}", "Avg mastery": "{:.2f}",
                                  "Risk score": "{:.2f}"}), width="stretch", hide_index=True)

st.subheader("Why is a student flagged?")
choice = st.selectbox("Student", overview.sort_values("risk", ascending=False)["name"])
row = overview[overview["name"] == choice]
reasons = analytics.top_reasons(model, row, k=3)
st.write(f"**Risk score {row.iloc[0]['risk']:.2f} ({row.iloc[0]['risk_level']})**. Main factors raising the risk:")
for feat, shap_v, val in reasons:
    if shap_v > 0:
        st.write(f"- {FEATURE_LABELS[feat]}: {val:.2f} (adds {shap_v:.2f} to the risk)")
shap_vals = dropout_model.explain(model, row)[0]
bars = px.bar(x=shap_vals, y=[FEATURE_LABELS[f] for f in FEATURES], orientation="h",
              labels={"x": "Effect on risk (SHAP)", "y": ""})
bars.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(bars, width="stretch")
st.caption("The model supports the teacher's judgement; it does not replace it.")
