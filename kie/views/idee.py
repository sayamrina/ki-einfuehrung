import streamlit as st

from .. import llm, state, ui
from ..i18n import T, lang
from ..privacy import pseudonymise

EXAMPLE = {
    "de": ("Wir bekommen jeden Tag viele Mails von Mitgliedern, deren Tankkarte gesperrt werden soll oder die eine Frage zur Abrechnung "
           "haben. Wir suchen dann in unseren Unterlagen und schreiben die Antwort. Beispiel: Kontakt: Kim Becker, Spedition Becker, "
           "Tel. 0261 1234567, Fahrzeug KO-AB 123, Anliegen: Ersatzkarte."),
    "en": ("Every day we receive many e-mails from members who want to block a fuel card or have a billing question. We search our "
           "documents and write the answer. Example: Contact: Kim Becker, Becker Logistics, phone 0261 1234567, vehicle KO-AB 123, "
           "request: replacement card."),
}
AREAS = {"de": ["Kundenservice", "Kundenberatung", "Versicherung", "Schulung", "Abrechnung", "Verwaltung", "Alle Bereiche"],
         "en": ["Customer service", "Customer advice", "Insurance", "Training", "Billing", "Administration", "All departments"]}


def render() -> None:
    ui.hero(T("Idee einreichen", "Submit an idea"),
            T("Der Fachbereich beschreibt ein Problem in eigenen Worten. Die KI strukturiert es zu einem Steckbrief, der dann gemeinsam geprüft und bewertet wird.",
              "A business unit describes a problem in its own words. The AI turns it into a structured brief, which is then reviewed and assessed together."))
    if not state.can("idee_einreichen"):
        state.deny_hint("idee_einreichen")
    with st.form("idee"):
        title = st.text_input(T("Kurzer Titel (optional)", "Short title (optional)"),
                              placeholder=T("z. B. Anfragen zu Tankkarten schneller beantworten", "e.g. answer fuel card requests faster"))
        area = st.selectbox(T("Fachbereich", "Business unit"), AREAS[lang()])
        text = st.text_area(T("Beschreiben Sie die Aufgabe und das Problem", "Describe the task and the problem"), EXAMPLE[lang()],
                            height=150, max_chars=2000)
        cases = st.number_input(T("Wie oft fällt die Aufgabe pro Monat ungefähr an?", "Roughly how often does the task occur per month?"),
                                0, 100000, 300, step=50)
        submitted = st.form_submit_button(T("Mit KI strukturieren", "Structure with AI"), type="primary",
                                          disabled=not state.can("idee_einreichen"))
    if submitted and text.strip():
        clean, counts = pseudonymise(text)
        with st.expander(T("Text, der an das Sprachmodell geht (pseudonymisiert)", "Text sent to the language model (pseudonymised)"),
                         expanded=bool(counts)):
            st.code(clean, language=None, wrap_lines=True)
            if counts:
                st.caption(T("Vor dem Modellaufruf ersetzt: ", "Replaced before the model call: ")
                           + ", ".join(f"{v}× {k}" for k, v in counts.items()))
        if llm.available() and state.llm_budget_ok():
            with st.spinner(T("Steckbrief wird erstellt …", "Creating the brief …")):
                system, _ = llm.prompts(lang())
                sb = llm.chat_json(system, f"{T('Fachbereich', 'Business unit')}: {area}\n{T('Titel', 'Title')}: {title}\n"
                                           f"{T('Beschreibung', 'Description')}: {clean}")
        else:
            sb = llm.offline_steckbrief(clean, title, lang())
        uid = state.next_id()
        st.session_state.usecases.append({
            "id": uid, "titel": sb.get("titel") or title or T("Neue Idee", "New idea"), "fachbereich": area, "status": "Idee",
            "faelle_pro_monat": int(cases), "steckbrief": {k: sb.get(k) for k in (
                "problem", "ziel", "nutzende", "daten", "schnittstellen", "erfolgskriterien", "datenschutz_hinweise", "offene_fragen")},
            "prozess": [], "bewertung": {"nutzen": 3, "aufwand": 3, "umsetzbarkeit": 3, "risiko": 3},
            "datenschutz": {"antworten": {}, "freigabe": "offen", "kommentar": ""},
            "it": state.it_seed("-", lang()), "entscheidung": {}, "tests": [], "grenzen": ""})
        state.log(uid, T("Idee eingereicht", "Idea submitted"), area)
        st.success(T(f"Als Anwendungsfall {uid} angelegt. Weiter unter „Anwendungsfall bearbeiten“.",
                     f"Created as use case {uid}. Continue under \"Work on a use case\"."))
        show_steckbrief(sb)


def show_steckbrief(sb: dict) -> None:
    st.markdown(f"#### {ui.esc(sb.get('titel', ''))}")
    for label, key in [("Problem", "problem"), (T("Ziel", "Goal"), "ziel"), (T("Nutzende", "Users"), "nutzende"),
                       (T("Daten", "Data"), "daten"), (T("Schnittstellen", "Systems"), "schnittstellen")]:
        st.markdown(f"**{label}:** {sb.get(key) or '–'}")
    for label, key in [(T("Erfolgskriterien", "Success criteria"), "erfolgskriterien"),
                       (T("Datenschutz-Hinweise", "Data protection notes"), "datenschutz_hinweise"),
                       (T("Offene Fragen an den Fachbereich", "Open questions for the business unit"), "offene_fragen")]:
        items = sb.get(key) or []
        st.markdown(f"**{label}:**\n" + "\n".join(f"- {i}" for i in items))
