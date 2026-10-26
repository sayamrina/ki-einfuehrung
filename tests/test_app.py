"""Smoke and interaction tests for every page in offline mode (no API key)."""
import pytest
from streamlit.testing.v1 import AppTest

RUNNER = "page_runner.py"  # resolved relative to this test file


def page(name: str, role: str = "AI Manager", lang: str = "de") -> AppTest:
    at = AppTest.from_file(RUNNER, default_timeout=60)
    at.session_state["page"] = name
    at.session_state["lang"] = lang
    at.run()
    at.session_state["role"] = role
    return at.run()


@pytest.mark.parametrize("name", ["uebersicht", "plan", "idee", "usecase", "sop", "lernen", "radar", "protokoll", "about"])
@pytest.mark.parametrize("lang", ["de", "en"])
def test_page_renders(name, lang, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page(name, lang=lang)
    assert not at.exception


def test_submit_idea_creates_usecase_and_log(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("idee", "Fachbereich")
    at.button[0].click().run()  # form submit: "Mit KI strukturieren"
    assert not at.exception
    assert len(at.session_state["usecases"]) == 8
    assert at.session_state["log"][-1]["aktion"] == "Idee eingereicht"
    assert "KENNZEICHEN" in at.code[0].value  # text sent to the model is pseudonymised


def test_decision_requires_management_role(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("usecase", "Fachbereich")
    assert not any(b.label == "Entscheidung festhalten" for b in at.button)
    at = page("usecase", "Geschäftsführung")
    assert any(b.label == "Entscheidung festhalten" for b in at.button)


def test_quiz_pass_gives_certificate(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from kie.course import content

    at = page("lernen")
    for q in content("de")[2]:
        at.radio(key=f"quiz_de_{q['id']}").set_value(q["optionen"][q["richtig"]])
    [b for b in at.button if b.label == "Test auswerten"][0].click().run()
    assert not at.exception
    assert at.session_state["quiz_result"][1] == 1.0
    assert at.session_state["course_stats"]["teilnehmende"] == 47


def test_english_sample_data_and_labels(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("usecase", "Geschäftsführung", lang="en")
    assert not at.exception
    assert at.session_state["data_lang"] == "en"
    assert any(b.label == "Record decision" for b in at.button)


def test_it_check_needed_before_approval(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("usecase", "IT")
    assert not at.exception
    assert any(b.label == "IT freigeben" for b in at.button)
    at = page("usecase", "Datenschutz")
    assert not any(b.label == "IT freigeben" for b in at.button)
    # C: data protection approved, IT still open -> management cannot approve it
    at = page("usecase", "Geschäftsführung")
    at.selectbox(key="uc_select").set_value("C").run()
    assert any("IT" in w.value for w in at.warning)


def test_ai_act_confirmation_is_needed_before_approval(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("usecase", "Compliance")
    assert not at.exception
    assert any(b.label == "Einstufung bestätigen" for b in at.button)
    at = page("usecase", "IT")
    assert not any(b.label == "Einstufung bestätigen" for b in at.button)
    # G: CV pre-screening is high risk and not confirmed -> management sees Compliance as missing
    at = page("usecase", "Geschäftsführung")
    at.selectbox(key="uc_select").set_value("G").run()
    assert not at.exception
    assert any("Compliance" in w.value for w in at.warning)
    assert any("Hochrisiko" in e.value for e in at.error)


def test_sop_assistant_refuses_release_and_logs_it(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = page("sop", "Fachbereich", lang="en")
    at.selectbox(key="sop_pick_en").set_value("Can we release batch 2611 today? All checks look fine.").run()
    [b for b in at.button if b.label == "Ask the assistant"][0].click().run()
    assert not at.exception
    assert any("escalated to QA" in e.value for e in at.error)
    assert at.session_state["sop_log"][-1]["ergebnis"].startswith("🛑")
    [b for b in at.button if b.label == "Run all test cases"][0].click().run()
    assert any(m.value == "11 / 11" for m in at.metric)
