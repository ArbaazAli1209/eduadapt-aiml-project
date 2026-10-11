"""End-to-end UI tests with Streamlit's AppTest (no browser needed)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT_APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(at):
    at.run(timeout=60)
    assert not at.exception, at.exception


def test_student_flow_english_and_hindi():
    at = AppTest.from_file(ROOT_APP, default_timeout=60)
    _run(at)
    assert any("Enter your name" in i.value for i in at.info)       # asks for a name first

    at.sidebar.text_input(key="name").set_value("Asha Test")
    _run(at)
    at.button[0].click()                                            # start diagnostic quiz
    _run(at)
    radios = [r for r in at.radio if r.key.startswith('q')]
    assert len(radios) == 6                                         # one question per topic
    for r in radios:
        r.set_value(r.options[0])
    [b for b in at.button if "Submit" in b.label][0].click()
    _run(at)
    assert len(at.success) + len(at.error) == 6                     # feedback for every question

    [b for b in at.button if "Next quiz" in b.label][0].click()     # next: adaptive practice quiz
    _run(at)
    assert any("Today's focus" in m.value for m in at.markdown)
    [b for b in at.button if "Start practice quiz" in b.label][0].click()
    _run(at)
    assert len([r for r in at.radio if r.key.startswith('q')]) == 3

    at.sidebar.radio(key="lang").set_value("हिन्दी")               # Hindi UI
    _run(at)
    assert at.sidebar.text_input(key="name").label == "आपका नाम"      # interface switched to Hindi


def test_teacher_dashboard_with_demo_class():
    page = str(Path(__file__).resolve().parent.parent / "pages" / "1_Teacher_Dashboard.py")
    at = AppTest.from_file(page, default_timeout=90)
    at.run()
    assert not at.exception, at.exception
    [b for b in at.sidebar.button if "Load demo class" in b.label][0].click()
    at.run()
    assert not at.exception, at.exception
    labels = [m.label for m in at.metric]
    assert "Students" in labels and "High-risk students" in labels
    assert len(at.selectbox) >= 1                                   # student drill-down present
