"""KI-Einführung / AI Adoption: Plattform, die den Arbeitsablauf eines AI Solutions Managers abbildet.

Idee aus dem Fachbereich → KI-Steckbrief → Prozessaufnahme → Datenschutz- und IT-Check → Bewertung → Entscheidung
→ Prüfstand → Pilot → Schulung, mit Projekt-Board und Entscheidungsprotokoll. Deutsch ist Standard, Englisch wählbar.
"""
import os

import streamlit as st

st.set_page_config(page_title="KI-Einführung", page_icon="🧭", layout="wide")

try:
    key = st.secrets.get("OPENAI_API_KEY")
except FileNotFoundError:  # keine Secrets: Offline-Modus mit Regeln statt Sprachmodell
    key = None
if key:
    os.environ["OPENAI_API_KEY"] = key

from kie import llm, state, ui  # noqa: E402
from kie.i18n import LANGS, T, role  # noqa: E402
from kie.views import about, idee, lernen, plan, protokoll, radar, uebersicht, usecase  # noqa: E402

st.session_state.setdefault("lang", "de")
with st.sidebar:
    st.segmented_control("Sprache / Language", list(LANGS), format_func=LANGS.get, key="lang",
                         help="Beim Wechsel werden die Beispieldaten in der gewählten Sprache neu geladen. / "
                              "Switching reloads the sample data in the selected language.")
if not st.session_state.get("lang"):  # segmented control can be cleared by a second click
    st.session_state.lang = "de"
state.init()
st.markdown(ui.CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧭 " + T("KI-Einführung", "AI Adoption"))
    st.selectbox(T("Ich arbeite als …", "I work as …"), state.ROLES, key="role", format_func=role,
                 help=T("Jede Rolle sieht dieselben Daten, darf aber unterschiedliche Schritte ausführen.",
                        "Every role sees the same data but may perform different steps."))
    st.caption(T("KI-Aufrufe übrig", "AI calls left") + f": **{state.MAX_LLM_CALLS - st.session_state.llm_calls}**"
               + ("" if llm.available() else T(" · Offline-Modus (Regeln statt Sprachmodell)", " · Offline mode (rules instead of a language model)")))
    st.caption(T("Beispieldaten aus der Logistikbranche. Ihre Eingaben bleiben in Ihrer Sitzung.",
                 "Sample data from the logistics sector. Your inputs stay in your session."))

pages = st.navigation({
    T("Steuerung", "Overview"): [
        st.Page(uebersicht.render, title=T("Übersicht", "Dashboard"), icon="📊", url_path="uebersicht", default=True),
        st.Page(plan.render, title=T("90-Tage-Plan", "90-day plan"), icon="🗓️", url_path="plan")],
    T("Anwendungsfälle", "Use cases"): [
        st.Page(idee.render, title=T("Idee einreichen", "Submit an idea"), icon="💡", url_path="idee"),
        st.Page(usecase.render, title=T("Anwendungsfall bearbeiten", "Work on a use case"), icon="🧩", url_path="anwendungsfall")],
    T("Befähigung", "Enablement"): [
        st.Page(lernen.render, title=T("KI-Führerschein", "AI licence"), icon="🎓", url_path="lernen"),
        st.Page(radar.render, title=T("KI-Radar", "AI radar"), icon="📡", url_path="radar")],
    T("Nachvollziehbarkeit", "Traceability"): [
        st.Page(protokoll.render, title=T("Protokoll und Rechte", "Log and rights"), icon="📜", url_path="protokoll"),
        st.Page(about.render, title=T("Über das Projekt", "About the project"), icon="ℹ️", url_path="info")],
})
pages.run()
