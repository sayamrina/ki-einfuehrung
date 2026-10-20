"""Sitzungszustand, Sprache, Rollen und Rechte sowie das Entscheidungsprotokoll."""
import copy
from datetime import date

import streamlit as st

from . import seed, seed_en
from .i18n import T, role

ROLES = ["Fachbereich", "AI Manager", "Datenschutz", "Geschäftsführung"]

# Wer darf was? (wird in der Oberfläche durchgesetzt und auf der Seite „Protokoll und Rechte“ angezeigt)
RIGHTS = {
    "idee_einreichen": {"Fachbereich", "AI Manager"},
    "steckbrief_bearbeiten": {"AI Manager"},
    "prozess_bearbeiten": {"Fachbereich", "AI Manager"},
    "bewerten": {"AI Manager"},
    "datenschutz_freigeben": {"Datenschutz"},
    "entscheiden": {"Geschäftsführung"},
    "testen": {"AI Manager", "Fachbereich"},
    "status_aendern": {"AI Manager"},
    "radar_bearbeiten": {"AI Manager"},
}
RIGHT_LABELS = {
    "idee_einreichen": ("Idee einreichen", "Submit an idea"),
    "steckbrief_bearbeiten": ("Steckbrief bearbeiten", "Edit the brief"),
    "prozess_bearbeiten": ("Prozess aufnehmen", "Map the process"),
    "bewerten": ("Anwendungsfall bewerten", "Assess the use case"),
    "datenschutz_freigeben": ("Datenschutz freigeben", "Approve data protection"),
    "entscheiden": ("Über Umsetzung entscheiden", "Decide on implementation"),
    "testen": ("Prüfstand: Tests ausführen", "Test bench: run tests"),
    "status_aendern": ("Projektstatus ändern", "Change project status"),
    "radar_bearbeiten": ("KI-Radar pflegen", "Maintain the AI radar"),
}
MAX_LLM_CALLS = 20


def load_sample_data(lang: str) -> None:
    s = st.session_state
    src = seed if lang == "de" else seed_en
    s.usecases = copy.deepcopy(src.usecases())
    s.log = copy.deepcopy(src.log())
    s.radar = copy.deepcopy(src.radar())
    s.course_stats = copy.deepcopy(seed.course_stats())
    s.quiz_result = None
    s.data_lang = lang


def init() -> None:
    s = st.session_state
    s.setdefault("lang", "de")
    s.setdefault("role", "AI Manager")
    s.setdefault("llm_calls", 0)
    if s.get("data_lang") != s.lang:  # erster Aufruf oder Sprache gewechselt: Beispieldaten in der gewählten Sprache
        load_sample_data(s.lang)


def can(right: str) -> bool:
    return st.session_state.role in RIGHTS[right]


def right_label(right: str) -> str:
    de, en = RIGHT_LABELS[right]
    return T(de, en)


def deny_hint(right: str) -> None:
    allowed = T(" oder ", " or ").join(role(r) for r in sorted(RIGHTS[right]))
    st.caption(T(f"🔒 Nur für die Rolle {allowed}. Rolle links in der Seitenleiste wechseln.",
                 f"🔒 Only for the role {allowed}. Switch the role in the sidebar."))


def log(usecase: str, action: str, details: str = "") -> None:
    st.session_state.log.append({"datum": date.today().isoformat(), "rolle": st.session_state.role,
                                 "usecase": usecase, "aktion": action, "details": details})


def llm_budget_ok() -> bool:
    if st.session_state.llm_calls >= MAX_LLM_CALLS:
        st.warning(T("Die Demo erlaubt pro Besuch eine begrenzte Zahl von KI-Aufrufen. Bitte später erneut laden.",
                     "This demo allows a limited number of AI calls per visit. Please reload later."))
        return False
    st.session_state.llm_calls += 1
    return True


def usecase(uid: str) -> dict:
    return next(u for u in st.session_state.usecases if u["id"] == uid)


def next_id() -> str:
    used = {u["id"] for u in st.session_state.usecases}
    return next(chr(c) for c in range(ord("A"), ord("Z") + 1) if chr(c) not in used)
