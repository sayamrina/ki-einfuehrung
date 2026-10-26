"""Sitzungszustand, Sprache, Rollen und Rechte sowie das Entscheidungsprotokoll."""
import copy
from datetime import date

import streamlit as st

from . import seed, seed_en
from .i18n import T, role

ROLES = ["Fachbereich", "AI Manager", "Datenschutz", "IT", "Compliance", "Geschäftsführung"]

# Wer darf was? (wird in der Oberfläche durchgesetzt und auf der Seite „Protokoll und Rechte“ angezeigt)
RIGHTS = {
    "idee_einreichen": {"Fachbereich", "AI Manager"},
    "steckbrief_bearbeiten": {"AI Manager"},
    "prozess_bearbeiten": {"Fachbereich", "AI Manager"},
    "bewerten": {"AI Manager"},
    "datenschutz_freigeben": {"Datenschutz"},
    "it_freigeben": {"IT"},
    "aiact_einstufen": {"AI Manager", "Compliance"},
    "aiact_freigeben": {"Compliance"},
    "entscheiden": {"Geschäftsführung"},
    "testen": {"AI Manager", "Fachbereich", "IT"},
    "status_aendern": {"AI Manager"},
    "radar_bearbeiten": {"AI Manager", "IT"},
}
RIGHT_LABELS = {
    "idee_einreichen": ("Idee einreichen", "Submit an idea"),
    "steckbrief_bearbeiten": ("Steckbrief bearbeiten", "Edit the brief"),
    "prozess_bearbeiten": ("Prozess aufnehmen", "Map the process"),
    "bewerten": ("Anwendungsfall bewerten", "Assess the use case"),
    "datenschutz_freigeben": ("Datenschutz freigeben", "Approve data protection"),
    "it_freigeben": ("Technisch freigeben (IT-Check)", "Technical approval (IT check)"),
    "aiact_einstufen": ("AI-Act-Einstufung vorbereiten", "Prepare the AI Act classification"),
    "aiact_freigeben": ("AI-Act-Einstufung bestätigen", "Confirm the AI Act classification"),
    "entscheiden": ("Über Umsetzung entscheiden", "Decide on implementation"),
    "testen": ("Prüfstand: Tests ausführen", "Test bench: run tests"),
    "status_aendern": ("Projektstatus ändern", "Change project status"),
    "radar_bearbeiten": ("KI-Radar pflegen", "Maintain the AI radar"),
}
MAX_LLM_CALLS = 20

# IT-Check der Beispieldaten (gleich für beide Sprachen, Texte je Sprache)
_ALL = {"schnittstelle": True, "hosting": True, "anmeldung": True, "betrieb": True, "kosten": True}
IT_SEED = {
    "A": (_ALL, "freigegeben", 12, ("Dokumentenablage (SharePoint), Intranet", "Document store (SharePoint), intranet"),
          ("Läuft im EU-Rechenzentrum, Monitoring aktiv.", "Runs in an EU data centre, monitoring active.")),
    "C": (_ALL | {"betrieb": False}, "offen", 15, ("Service-Postfach, Mitgliederverwaltung", "Service mailbox, member database"),
          ("", "")),
    "D": (_ALL, "freigegeben", 6, ("Lernplattform (LMS)", "Learning platform (LMS)"),
          ("Unkritisch, keine Kundendaten.", "Not critical, no customer data.")),
}


# AI-Act-Einstufung der Beispieldaten: (Antworten, Freigabe, Kommentar DE, Kommentar EN)
AIACT_SEED = {
    "A": ({"chatbot": True}, "freigegeben", "Hinweis „Sie chatten mit einer KI“ ist im Assistenten sichtbar.",
          "The notice “You are chatting with an AI” is shown in the assistant."),
    "B": ({}, "offen", "", ""),
    "C": ({"synthetic": True}, "freigegeben", "Entwürfe werden vor dem Versand von einer Person geprüft und angepasst.",
          "Drafts are checked and edited by a person before they are sent."),
    "D": ({"education": True, "narrow_task": True}, "freigegeben",
          "Übungsfragen bewerten niemanden; Ausnahme nach Art. 6 (3) dokumentiert.",
          "Practice questions do not grade anyone; exception under Art. 6 (3) documented."),
    "G": ({"hr": True, "profiling": True}, "offen", "", ""),
}


def aiact_seed(uid: str, lang: str) -> dict:
    answers, release, de, en = AIACT_SEED.get(uid, ({}, "offen", "", ""))
    return {"antworten": dict(answers), "gxp": {}, "freigabe": release, "kommentar": en if lang == "en" else de}


def it_seed(uid: str, lang: str) -> dict:
    if uid not in IT_SEED:
        return {"antworten": {}, "systeme": "", "personentage": 0, "freigabe": "offen", "kommentar": ""}
    answers, release, days, systems, comment = IT_SEED[uid]
    i = 1 if lang == "en" else 0
    return {"antworten": dict(answers), "systeme": systems[i], "personentage": days, "freigabe": release, "kommentar": comment[i]}


def load_sample_data(lang: str) -> None:
    s = st.session_state
    src = seed if lang == "de" else seed_en
    s.usecases = copy.deepcopy(src.usecases())
    s.log = copy.deepcopy(src.log())
    s.radar = copy.deepcopy(src.radar())
    for u in s.usecases:
        u.setdefault("it", it_seed(u["id"], lang))
        u.setdefault("aiact", aiact_seed(u["id"], lang))
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
