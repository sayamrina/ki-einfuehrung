from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from .. import llm, state, ui
from ..i18n import T, lang, role
from ..privacy import pseudonymise
from ..sop import TESTS, Assistant, answer, guardrail, run_tests

DATA = Path(__file__).resolve().parents[2] / "data"

SYSTEM = {
    "de": """Du bist der SOP-Assistent eines Pharmawerks. Beantworte die Frage NUR mit den nummerierten SOP-Auszügen.
Triff nie eine GxP-Entscheidung (Freigabe, Einstufung, Annahme, Ablehnung) und ändere keine Aufzeichnungen.
Wenn die Auszüge die Frage nicht beantworten, lass "antwort" leer. Rate nie. Antworte in 1 bis 3 ganzen Sätzen auf Deutsch und nenne die Werte mit Einheit.
Gib JSON zurück: {"antwort": str, "quellen": [int]}""",
    "en": """You are the SOP assistant of a pharmaceutical plant. Answer ONLY from the numbered SOP excerpts.
Never make a GxP decision (release, classification, acceptance, rejection) and never change records.
If the excerpts do not answer the question, leave "antwort" empty. Never guess. Answer in 1 to 3 full sentences in English and give values with their unit.
Return JSON: {"antwort": str, "quellen": [int]}""",
}
KIND = {
    "antwort": ("success", "✅ Antwort aus gültiger SOP", "✅ Answer from an effective SOP"),
    "entscheidung": ("error", "🛑 Leitplanke: GxP-Entscheidung, an QA eskaliert", "🛑 Guardrail: GxP decision, escalated to QA"),
    "aufzeichnung": ("error", "🛑 Leitplanke: Änderung einer Aufzeichnung abgelehnt", "🛑 Guardrail: record change refused"),
    "keine_quelle": ("warning", "⚠️ Keine gültige SOP gefunden", "⚠️ No effective SOP found"),
}


@st.cache_resource
def assistant(language: str) -> Assistant:
    return Assistant(DATA / ("sop_en" if language == "en" else "sop_de"))


def kind_label(kind: str) -> str:
    _, de, en = KIND[kind]
    return T(de, en)


def model(question: str, hits: list) -> tuple[str, list[int]]:
    context = "\n\n".join(f"[{s.id}] {s.title} – {s.section}\n{s.text}" for s in hits)
    result = llm.chat_json(SYSTEM[lang()], f"{T('Auszüge', 'Excerpts')}:\n{context}\n\n{T('Frage', 'Question')}: {question}")
    return result.get("antwort", ""), [int(i) for i in result.get("quellen", []) if str(i).isdigit()]


def render() -> None:
    ui.hero(T("SOP-Assistent mit GxP-Leitplanken", "SOP assistant with GxP guardrails"),
            T("Beispiel aus der Pharmaproduktion: Fragen an die SOPs eines erfundenen Werks, mit Regeln, die vor jedem Modellaufruf greifen.",
              "An example from pharmaceutical production: questions to the SOPs of a fictional plant, with rules that apply before any model call."))
    c = st.columns(4)
    rules = [(T("Keine GxP-Entscheidung", "No GxP decision"),
              T("Freigabe, Einstufung, Annahme oder Ablehnung entscheidet die QA.", "Release, classification, acceptance or rejection is QA's call.")),
             (T("Keine Änderung an Aufzeichnungen", "No change to records"),
              T("Korrekturen nur durch die Person selbst, nach ALCOA+.", "Corrections only by the person, following ALCOA+.")),
             (T("Nur gültige SOP-Versionen", "Only effective SOP versions"),
              T("Ersetzte Versionen werden nie als Quelle genutzt.", "Superseded versions are never used as a source.")),
             (T("Ohne Quelle keine Antwort", "No source, no answer"),
              T("Jede Antwort nennt SOP, Version und Abschnitt.", "Every answer names the SOP, version and section."))]
    for col, (title, text) in zip(c, rules, strict=True):
        col.markdown(f'<div class="kie-card" style="min-height:126px"><h4>{ui.esc(title)}</h4><div class="kie-muted">{ui.esc(text)}</div></div>',
                     unsafe_allow_html=True)

    a = assistant(lang())
    examples = [q for q, _, _ in TESTS[lang()]]
    pick = st.selectbox(T("Beispielfrage", "Example question"), examples, key=f"sop_pick_{lang()}")
    question = st.text_input(T("Frage an den SOP-Assistenten", "Question for the SOP assistant"), pick, key=f"sop_q_{lang()}_{pick}")
    if st.button(T("Assistent fragen", "Ask the assistant"), type="primary", key="sop_ask") and question.strip():
        clean, counts = pseudonymise(question)
        use_model = llm.available() and guardrail(clean) is None and state.llm_budget_ok()  # Leitplanken kosten keinen Modellaufruf
        with st.spinner(T("Assistent sucht in den SOPs …", "The assistant is searching the SOPs …")):
            result = answer(a, clean, lang(), model if use_model else None)
        st.session_state.sop_result = (result, counts)
        st.session_state.setdefault("sop_log", []).append({
            "zeit": datetime.now().isoformat(timespec="seconds"), "rolle": role(st.session_state.role), "frage": clean,
            "ergebnis": kind_label(result.kind), "quellen": "; ".join(a.label(s) for s in result.sources)})
    if "sop_result" in st.session_state:
        result, counts = st.session_state.sop_result
        kind = KIND[result.kind][0]
        getattr(st, kind)(f"**{kind_label(result.kind)}**\n\n{result.text}")
        for s in result.sources:
            st.caption(f"📄 {a.label(s)}")
        if result.superseded:
            st.caption(T("Nicht verwendet, weil ersetzt: ", "Not used because superseded: ") + ", ".join(result.superseded))
        if counts:
            st.caption(T("Vor dem Modellaufruf ersetzt: ", "Replaced before the model call: ") + ", ".join(f"{v}× {k}" for k, v in counts.items()))

    st.markdown("##### " + T("Audit-Trail dieser Sitzung", "Audit trail of this session"))
    log = st.session_state.get("sop_log", [])
    if log:
        df = pd.DataFrame(log).rename(columns={"zeit": T("Zeit", "Time"), "rolle": T("Rolle", "Role"), "frage": T("Frage", "Question"),
                                               "ergebnis": T("Ergebnis", "Outcome"), "quellen": T("Quellen", "Sources")})
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button(T("Audit-Trail als CSV", "Audit trail as CSV"), df.to_csv(index=False).encode("utf-8"),
                           file_name="sop_audit_trail.csv", mime="text/csv")
    else:
        st.caption(T("Jede Frage wird mit Zeit, Rolle, Ergebnis und Quellen festgehalten (zuordenbar und zeitnah nach ALCOA+).",
                     "Every question is recorded with time, role, outcome and sources (attributable and contemporaneous under ALCOA+)."))

    st.markdown("##### " + T("Prüfstand der Leitplanken", "Guardrail test bench"))
    if st.button(T("Alle Testfälle ausführen", "Run all test cases"), key="sop_tests"):
        rows = run_tests(a, lang())
        df = pd.DataFrame(rows)
        df["erwartet"] = df["erwartet"].map(kind_label)
        df["ergebnis"] = df["ergebnis"].map(kind_label)
        df["ok"] = df["ok"].map({True: "✅", False: "❌"})
        st.dataframe(df.rename(columns={"frage": T("Testfrage", "Test question"), "erwartet": T("Erwartet", "Expected"),
                                        "ergebnis": T("Ergebnis", "Result"), "sop": "SOP", "ok": T("Bestanden", "Passed")}),
                     hide_index=True, use_container_width=True)
        passed = sum(r["ok"] for r in rows)
        st.metric(T("Bestanden", "Passed"), f"{passed} / {len(rows)}",
                  help=T("Die Tests laufen ohne Sprachmodell, damit sie reproduzierbar sind.", "The tests run without a language model so they are reproducible."))
    st.caption(T("Alle SOPs und das Werk sind erfunden. Ein echter Einsatz im GxP-Umfeld braucht eine Validierung als computergestütztes "
                 "System (EU-GMP Anhang 11) und die Freigabe durch die QA.",
                 "All SOPs and the plant are fictional. Real use in a GxP environment needs validation as a computerised system "
                 "(EU GMP Annex 11) and approval by QA."))
