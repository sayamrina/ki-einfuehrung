"""Zweisprachigkeit: Deutsch ist Standard, Englisch ist wählbar."""
import streamlit as st

LANGS = {"de": "Deutsch", "en": "English"}

STATUS_EN = {"Idee": "Idea", "Bewertung": "Assessment", "Entscheidung": "Decision", "Prototyp": "Prototype",
             "Pilot": "Pilot", "Einführung": "Rollout", "Zurückgestellt": "On hold"}
ROLE_EN = {"Fachbereich": "Business unit", "AI Manager": "AI Manager", "Datenschutz": "Data protection", "IT": "IT",
           "Geschäftsführung": "Management"}
DECISION_EN = {"Freigegeben": "Approved", "Zurückgestellt": "On hold", "Abgelehnt": "Rejected"}
DS_RELEASE_EN = {"offen": "open", "freigegeben": "approved", "nicht freigegeben": "not approved"}
VERDICT_EN = {"richtig": "correct", "teilweise": "partly correct", "falsch": "wrong"}


def lang() -> str:
    try:
        return st.session_state.get("lang", "de")
    except Exception:  # außerhalb einer Streamlit-Sitzung (z. B. PDF-Tests)
        return "de"


def T(de: str, en: str) -> str:
    return en if lang() == "en" else de


def status(value: str) -> str:
    return STATUS_EN.get(value, value) if lang() == "en" else value


def role(value: str) -> str:
    return ROLE_EN.get(value, value) if lang() == "en" else value


def decision(value: str) -> str:
    return DECISION_EN.get(value, value) if lang() == "en" else value


def release(value: str) -> str:
    return DS_RELEASE_EN.get(value, value) if lang() == "en" else value


def verdict(value: str) -> str:
    return VERDICT_EN.get(value, value) if lang() == "en" else value
