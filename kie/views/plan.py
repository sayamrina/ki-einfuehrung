import pandas as pd
import streamlit as st

from .. import ui
from ..i18n import T, lang, status

PHASES = [
    (("Woche 1 bis 3", "Weeks 1 to 3"), ("Analyse und Entscheidung", "Analysis and decision"),
     ("Gespräche mit dem Fachbereich, Prozessaufnahme, Datenschutz-Check, Bewertung",
      "Talks with the business unit, process mapping, data protection check, assessment"),
     ("Entscheidung der Geschäftsführung", "Management decision"), {"Idee", "Bewertung", "Entscheidung"}),
    (("Woche 4 bis 7", "Weeks 4 to 7"), ("Prototyp und Tests", "Prototype and tests"),
     ("Prototyp mit IT und Entwicklungspartnern, Testfragen aus dem Fachbereich",
      "Prototype with IT and development partners, test questions from the business unit"),
     ("Dokumentierte Trefferquote und Grenzen", "Documented hit rate and limits"), {"Prototyp"}),
    (("Woche 8 bis 11", "Weeks 8 to 11"), ("Pilot", "Pilot"),
     ("Pilot mit 8 bis 10 Personen, wöchentliches Feedback", "Pilot with 8 to 10 people, weekly feedback"),
     ("Pilotbericht", "Pilot report"), {"Pilot"}),
    (("Woche 12 bis 13", "Weeks 12 to 13"), ("Einführung und Schulung", "Rollout and training"),
     ("Schulung „KI-Führerschein“, Betriebshinweise, Verantwortlichkeiten", "\"AI licence\" training, operating notes, responsibilities"),
     ("Einführung oder begründeter Stopp", "Rollout or a reasoned stop"), {"Einführung"}),
]
ORDER = ["Idee", "Bewertung", "Entscheidung", "Prototyp", "Pilot", "Einführung"]


def tr(pair: tuple[str, str]) -> str:
    return pair[1] if lang() == "en" else pair[0]


def phase_state(status: str, phase_statuses: set[str]) -> str:
    if status in phase_statuses:
        return T("▶ läuft", "▶ running")
    first = min(ORDER.index(s) for s in phase_statuses)
    return T("✅ erledigt", "✅ done") if ORDER.index(status) > first else T("○ geplant", "○ planned")


def render() -> None:
    ui.hero(T("90-Tage-Plan", "90-day plan"),
            T("Jedes freigegebene Vorhaben durchläuft dieselben vier Phasen. So sieht die Geschäftsführung jederzeit, wo ein Vorhaben steht und was als Nächstes kommt.",
              "Every approved project goes through the same four phases. Management can see at any time where a project stands and what comes next."))
    st.dataframe(pd.DataFrame([{T("Zeitraum", "Period"): tr(p[0]), "Phase": tr(p[1]), T("Was passiert", "What happens"): tr(p[2]),
                                T("Ergebnis", "Result"): tr(p[3])} for p in PHASES]), hide_index=True, use_container_width=True)
    st.subheader(T("Stand je Vorhaben", "Status per project"))
    rows = []
    for u in st.session_state.usecases:
        if u["status"] == "Zurückgestellt":
            continue
        row = {T("Vorhaben", "Project"): f'{u["id"]}. {u["titel"]}', "Status": status(u["status"])}
        for p in PHASES:
            row[tr(p[1])] = phase_state(u["status"], p[4])
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption(T("▶ läuft · ✅ erledigt · ○ geplant. Zurückgestellte Vorhaben erscheinen nicht im Plan.",
                 "▶ running · ✅ done · ○ planned. Projects on hold do not appear in the plan."))
