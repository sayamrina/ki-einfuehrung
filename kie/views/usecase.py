import re
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from .. import aiact, llm, pdf, state, ui, value
from ..i18n import T, decision, lang, release, role, status, verdict
from ..knowledge import Index, load_sections
from ..privacy import pseudonymise
from ..scoring import AMPEL_LABEL, DS_MEASURES, DS_QUESTIONS, IT_CHECKS, IT_LABEL, ampel, it_status, ranking, score, time_saving
from ..seed import STATUSES

DATA = Path(__file__).resolve().parents[2] / "data"


@st.cache_resource
def knowledge_index(language: str) -> Index:
    if language == "en":
        return Index(load_sections(DATA / "wissen_en", "Overview"))
    return Index(load_sections(DATA / "wissen"))


def render() -> None:
    ucs = st.session_state.usecases
    ui.hero(T("Anwendungsfall bearbeiten", "Work on a use case"),
            T("Steckbrief, Prozess, Datenschutz, AI Act, IT, Bewertung, Entscheidung und Tests: jeder Schritt wird festgehalten.",
              "Brief, process, data protection, AI Act, IT, assessment, decision and tests: every step is recorded."))
    labels = {u["id"]: f'{u["id"]}. {u["titel"]} ({status(u["status"])})' for u in ucs}
    uid = st.selectbox(T("Anwendungsfall", "Use case"), list(labels), format_func=labels.get, key="uc_select")
    uc = state.usecase(uid)
    rank = ranking(ucs)[uid]
    level = ampel(uc["datenschutz"].get("antworten", {}), lang())[0]
    text, kind = ui.ampel_badge(level)
    it_text, it_kind = ui.it_badge(it_status(uc["it"].get("antworten", {}), lang())[0])
    ai_text, ai_kind = ui.aiact_badge(aiact.classify(uc["aiact"].get("antworten", {}))[0])
    st.markdown(ui.badge(uc["fachbereich"]) + ui.badge(f"Status: {status(uc['status'])}") + ui.badge(T("Rang ", "Rank ") + str(rank))
                + ui.badge(text, kind) + ui.badge(it_text, it_kind) + ui.badge(ai_text, ai_kind), unsafe_allow_html=True)

    tabs = st.tabs([T("Steckbrief", "Brief"), T("Prozessaufnahme", "Process mapping"), T("Datenschutz-Check", "Data protection check"),
                    T("EU AI Act", "EU AI Act"), T("IT-Check", "IT check"), T("Bewertung", "Assessment"), T("Wert", "Value"), T("Entscheidung", "Decision"), T("Prüfstand", "Test bench"), T("Verlauf", "History")])
    with tabs[0]:
        steckbrief(uc)
    with tabs[1]:
        prozess(uc)
    with tabs[2]:
        datenschutz(uc)
    with tabs[3]:
        ai_act(uc)
    with tabs[4]:
        it_check(uc)
    with tabs[5]:
        bewertung(uc, rank)
    with tabs[6]:
        wert(uc)
    with tabs[7]:
        entscheidung(uc, rank)
    with tabs[8]:
        pruefstand(uc)
    with tabs[9]:
        verlauf(uc)


def steckbrief(uc: dict) -> None:
    sb = uc["steckbrief"]
    editable = state.can("steckbrief_bearbeiten")
    with st.form(f"sb_{uc['id']}"):
        title = st.text_input(T("Titel", "Title"), uc["titel"], disabled=not editable)
        fields = {}
        for label, key in [("Problem", "problem"), (T("Ziel", "Goal"), "ziel"), (T("Nutzende", "Users"), "nutzende"),
                           (T("Daten", "Data"), "daten"), (T("Schnittstellen", "Systems"), "schnittstellen")]:
            fields[key] = st.text_area(label, sb.get(key) or "", height=70, disabled=not editable)
        lists = {}
        for label, key in [(T("Erfolgskriterien (eine pro Zeile)", "Success criteria (one per line)"), "erfolgskriterien"),
                           (T("Offene Fragen (eine pro Zeile)", "Open questions (one per line)"), "offene_fragen")]:
            lists[key] = st.text_area(label, "\n".join(sb.get(key) or []), height=80, disabled=not editable)
        if st.form_submit_button(T("Steckbrief speichern", "Save brief"), disabled=not editable):
            uc["titel"] = title
            sb.update(fields)
            for key, value in lists.items():
                sb[key] = [line.strip() for line in value.splitlines() if line.strip()]
            state.log(uc["id"], T("Steckbrief geändert", "Brief changed"))
            st.success(T("Gespeichert.", "Saved."))
    if not editable:
        state.deny_hint("steckbrief_bearbeiten")


def prozess(uc: dict) -> None:
    st.markdown(T("Der Fachbereich beschreibt die Arbeitsschritte heute und schätzt, wie lange sie mit KI-Unterstützung dauern würden.",
                  "The business unit describes today's work steps and estimates how long they would take with AI support."))
    editable = state.can("prozess_bearbeiten")
    df = pd.DataFrame(uc["prozess"] or [{"schritt": "", "minuten": 0, "ki": False, "minuten_mit_ki": 0}])
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, disabled=not editable, key=f"proc_{uc['id']}_{lang()}",
        column_config={"schritt": st.column_config.TextColumn(T("Arbeitsschritt", "Work step"), width="large"),
                       "minuten": st.column_config.NumberColumn(T("Minuten heute", "Minutes today"), min_value=0, step=0.5),
                       "ki": st.column_config.CheckboxColumn(T("KI hilft?", "AI helps?")),
                       "minuten_mit_ki": st.column_config.NumberColumn(T("Minuten mit KI", "Minutes with AI"), min_value=0, step=0.5)})
    cases = st.number_input(T("Fälle pro Monat", "Cases per month"), 0, 100000, int(uc["faelle_pro_monat"]), step=50,
                            disabled=not editable, key=f"cases_{uc['id']}")
    steps = [r for r in edited.to_dict("records") if str(r.get("schritt") or "").strip()]
    saving = time_saving(steps, cases)
    c = st.columns(3)
    c[0].metric(T("Minuten pro Fall heute", "Minutes per case today"), f"{saving.minutes_before:g}")
    c[1].metric(T("Minuten pro Fall mit KI", "Minutes per case with AI"), f"{saving.minutes_after:g}")
    c[2].metric(T("Ersparnis pro Monat", "Saved per month"), f"{saving.hours_per_month:g} h")
    if editable and st.button(T("Prozess speichern", "Save process"), key=f"save_proc_{uc['id']}"):
        uc["prozess"], uc["faelle_pro_monat"] = steps, int(cases)
        state.log(uc["id"], T("Prozessaufnahme gespeichert", "Process mapping saved"),
                  f"{saving.hours_per_month:g} h/{T('Monat geschätzt', 'month estimated')}")
        st.success(T("Gespeichert.", "Saved."))
    if not editable:
        state.deny_hint("prozess_bearbeiten")


def datenschutz(uc: dict) -> None:
    ds = uc["datenschutz"]
    answers = dict(ds.get("antworten") or {})
    en = lang() == "en"
    st.markdown(f"**{T('Risiken', 'Risks')}**")
    for q in DS_QUESTIONS:
        answers[q[0]] = st.toggle(q[2] if en else q[1], answers.get(q[0], False), key=f"ds_{uc['id']}_{q[0]}")
    st.markdown(f"**{T('Schutzmaßnahmen', 'Safeguards')}**")
    for m in DS_MEASURES:
        answers[m[0]] = st.toggle(m[2] if en else m[1], answers.get(m[0], False), key=f"ds_{uc['id']}_{m[0]}")
    level, risk, hints = ampel(answers, lang())
    kind = {"gruen": "success", "gelb": "warning", "rot": "error", "offen": "info"}[level]
    getattr(st, kind)(f"{AMPEL_LABEL[lang()][level]} ({T('Risikopunkte nach Maßnahmen', 'Risk points after safeguards')}: {risk})")
    for hint in hints:
        st.markdown(f"- {hint}")
    if st.button(T("Antworten speichern", "Save answers"), key=f"ds_save_{uc['id']}"):
        ds["antworten"] = answers
        state.log(uc["id"], T("Datenschutz-Check ausgefüllt", "Data protection check completed"), AMPEL_LABEL[lang()][level])
        st.success(T("Gespeichert.", "Saved."))
    st.divider()
    st.markdown(f"**{T('Freigabe durch den Datenschutz', 'Data protection approval')}:** {release(ds.get('freigabe', 'offen'))}"
                + (f" · {ds['kommentar']}" if ds.get("kommentar") else ""))
    if state.can("datenschutz_freigeben"):
        comment = st.text_input(T("Kommentar / Auflagen", "Comment / conditions"), key=f"ds_comment_{uc['id']}")
        a, b = st.columns(2)
        if a.button(T("Freigeben", "Approve"), key=f"ds_ok_{uc['id']}", disabled=level == "rot" and not comment):
            ds.update(freigabe="freigegeben", kommentar=comment, antworten=answers)
            state.log(uc["id"], T("Datenschutz freigegeben", "Data protection approved"), comment)
            st.rerun()
        if b.button(T("Nicht freigeben", "Do not approve"), key=f"ds_no_{uc['id']}"):
            ds.update(freigabe="nicht freigegeben", kommentar=comment, antworten=answers)
            state.log(uc["id"], T("Datenschutz nicht freigegeben", "Data protection not approved"), comment)
            st.rerun()
        if level == "rot":
            st.caption(T("Bei roter Ampel ist eine Freigabe nur mit dokumentierten Auflagen möglich.",
                         "With a red light, approval is only possible with documented conditions."))
    else:
        state.deny_hint("datenschutz_freigeben")


def ai_act(uc: dict) -> None:
    ai = uc["aiact"]
    answers = dict(ai.get("antworten") or {})
    gxp = dict(ai.get("gxp") or {})
    en = lang() == "en"
    editable = state.can("aiact_einstufen")
    st.markdown(T("Einstufung nach der KI-Verordnung (EU) 2024/1689, Schritt für Schritt wie im Gesetz: verbotene Praktiken, "
                  "Hochrisiko, Transparenzpflichten. Dazu ein GxP-Check für regulierte Prozesse.",
                  "Classification under the AI Act (EU) 2024/1689, step by step as in the law: prohibited practices, high risk, "
                  "transparency obligations. Plus a GxP check for regulated processes."))

    def ask(items, store, prefix):
        for q in items:
            label = (q[2] if en else q[1]) + (f" · *{aiact.ref(q[3], lang())}*" if len(q) > 3 else "")
            store[q[0]] = st.toggle(label, store.get(q[0], False), disabled=not editable, key=f"{prefix}_{uc['id']}_{q[0]}")

    st.markdown(f"**1. {T('Verbotene Praktiken', 'Prohibited practices')}**")
    ask(aiact.PROHIBITED, answers, "ai")
    st.markdown(f"**2. {T('Hochrisiko-Bereiche', 'High-risk areas')}**")
    ask(aiact.HIGH_RISK, answers, "ai")
    if any(answers.get(q[0]) for q in aiact.HIGH_RISK if q[0] != "product_safety"):
        ask([aiact.PROFILING, aiact.EXCEPTION], answers, "ai")
    st.markdown(f"**3. {T('Transparenz', 'Transparency')}**")
    ask(aiact.TRANSPARENCY, answers, "ai")
    st.markdown(f"**4. {T('GxP (Pharma und Medizinprodukte)', 'GxP (pharma and medical devices)')}**")
    ask(aiact.GXP, gxp, "gxp")

    level, reasons = aiact.classify(answers)
    kind = {"offen": "info", "verboten": "error", "hoch": "error", "begrenzt": "warning", "minimal": "success"}[level]
    getattr(st, kind)(aiact.LABEL[lang()][level] + (f" ({aiact.ref(', '.join(reasons), lang())})" if reasons else ""))
    for duty in aiact.duties(level, lang()):
        st.markdown(f"- {duty}")
    if aiact.gxp_relevant(gxp):
        st.warning(T("GxP-relevant: zusätzlich zur AI-Act-Einstufung gelten die GMP-Anforderungen an computergestützte Systeme.",
                     "GxP-relevant: GMP requirements for computerised systems apply in addition to the AI Act class."))
        for hint in aiact.gxp_hints(gxp, lang()):
            st.markdown(f"- {hint}")
    st.caption(T("Orientierungshilfe für das Gespräch mit Compliance und Recht, keine Rechtsberatung. Fristen und Leitlinien der "
                 "EU-Kommission vor der Freigabe prüfen.",
                 "Guidance for the conversation with Compliance and Legal, not legal advice. Check deadlines and the European "
                 "Commission's guidelines before approval."))
    if editable and st.button(T("Einstufung speichern", "Save classification"), key=f"ai_save_{uc['id']}"):
        ai.update(antworten=answers, gxp=gxp)
        state.log(uc["id"], T("AI-Act-Einstufung gespeichert", "AI Act classification saved"), aiact.LABEL[lang()][level])
        st.success(T("Gespeichert.", "Saved."))
    if not editable:
        state.deny_hint("aiact_einstufen")
    st.divider()
    st.markdown(f"**{T('Bestätigung durch Compliance', 'Confirmation by Compliance')}:** {release(ai.get('freigabe', 'offen'))}"
                + (f" · {ai['kommentar']}" if ai.get("kommentar") else ""))
    if state.can("aiact_freigeben"):
        comment = st.text_input(T("Kommentar / Auflagen", "Comment / conditions"), key=f"ai_comment_{uc['id']}")
        a, b = st.columns(2)
        blocked = level in ("verboten", "offen") or (level == "hoch" and not comment)
        if a.button(T("Einstufung bestätigen", "Confirm classification"), key=f"ai_ok_{uc['id']}", disabled=blocked):
            ai.update(freigabe="freigegeben", kommentar=comment, antworten=answers, gxp=gxp)
            state.log(uc["id"], T("AI-Act-Einstufung bestätigt", "AI Act classification confirmed"), aiact.LABEL[lang()][level])
            st.rerun()
        if b.button(T("Nicht freigeben", "Do not approve"), key=f"ai_no_{uc['id']}"):
            ai.update(freigabe="nicht freigegeben", kommentar=comment, antworten=answers, gxp=gxp)
            state.log(uc["id"], T("AI Act: nicht freigegeben", "AI Act: not approved"), comment)
            st.rerun()
        if level == "verboten":
            st.caption(T("Verbotene Praktiken können nicht freigegeben werden.", "Prohibited practices cannot be approved."))
        elif level == "hoch":
            st.caption(T("Hochrisiko: Bestätigung nur mit dokumentierten Auflagen (Aufsicht, Protokolle, Information der Beschäftigten).",
                         "High risk: confirmation only with documented conditions (oversight, logs, informing employees)."))
    else:
        state.deny_hint("aiact_freigeben")


def it_check(uc: dict) -> None:
    it = uc["it"]
    answers = dict(it.get("antworten") or {})
    en = lang() == "en"
    editable = state.can("it_freigeben")
    st.markdown(T("Die IT prüft, ob die Lösung technisch angebunden und sicher betrieben werden kann.",
                  "IT checks whether the solution can be connected and run safely."))
    c = st.columns([2, 1])
    systems = c[0].text_input(T("Beteiligte Systeme", "Systems involved"), it.get("systeme", ""), disabled=not editable,
                              key=f"it_sys_{uc['id']}")
    days = c[1].number_input(T("Aufwand in Personentagen", "Effort in person-days"), 0, 500, int(it.get("personentage", 0)),
                             disabled=not editable, key=f"it_days_{uc['id']}")
    st.markdown(f"**{T('Technische Bereitschaft', 'Technical readiness')}**")
    for chk in IT_CHECKS:
        answers[chk[0]] = st.toggle(chk[2] if en else chk[1], answers.get(chk[0], False), disabled=not editable,
                                    key=f"it_{uc['id']}_{chk[0]}")
    level, done, hints = it_status(answers, lang())
    kind = {"gruen": "success", "gelb": "warning", "rot": "error", "offen": "info"}[level]
    getattr(st, kind)(f"{IT_LABEL[lang()][level]} ({done} {T('von', 'of')} {len(IT_CHECKS)})")
    for hint in hints:
        st.markdown(f"- {hint}")
    st.divider()
    st.markdown(f"**{T('Technische Freigabe durch die IT', 'Technical approval by IT')}:** {release(it.get('freigabe', 'offen'))}"
                + (f" · {it['kommentar']}" if it.get("kommentar") else ""))
    if editable:
        comment = st.text_input(T("Kommentar / Auflagen", "Comment / conditions"), key=f"it_comment_{uc['id']}")
        a, b = st.columns(2)
        if a.button(T("IT freigeben", "IT approve"), key=f"it_ok_{uc['id']}", disabled=level in ("rot", "offen") and not comment):
            it.update(freigabe="freigegeben", kommentar=comment, antworten=answers, systeme=systems, personentage=int(days))
            state.log(uc["id"], T("IT freigegeben", "IT approved"), comment or IT_LABEL[lang()][level])
            st.rerun()
        if b.button(T("IT nicht freigeben", "IT do not approve"), key=f"it_no_{uc['id']}"):
            it.update(freigabe="nicht freigegeben", kommentar=comment, antworten=answers, systeme=systems, personentage=int(days))
            state.log(uc["id"], T("IT nicht freigegeben", "IT not approved"), comment)
            st.rerun()
        if level in ("rot", "offen"):
            st.caption(T("Solange wichtige Punkte offen sind, ist eine Freigabe nur mit dokumentierten Auflagen möglich.",
                         "While important points are open, approval is only possible with documented conditions."))
    else:
        state.deny_hint("it_freigeben")


def bewertung(uc: dict, rank: int) -> None:
    editable = state.can("bewerten")
    b = dict(uc["bewertung"])
    names = {"nutzen": T("Nutzen", "Benefit"), "aufwand": T("Aufwand", "Effort"), "umsetzbarkeit": T("Umsetzbarkeit", "Feasibility"),
             "risiko": T("Risiko", "Risk")}
    hints = {"nutzen": T("Wie stark entlastet es?", "How much does it relieve the team?"),
             "aufwand": T("Wie viel Arbeit bis zum Pilot?", "How much work until the pilot?"),
             "umsetzbarkeit": T("Liegen Daten und Schnittstellen vor?", "Are data and interfaces available?"),
             "risiko": T("Datenschutz und Fehlerfolgen", "Data protection and impact of errors")}
    c = st.columns(4)
    for col, key in zip(c, ["nutzen", "aufwand", "umsetzbarkeit", "risiko"], strict=True):
        b[key] = col.slider(names[key], 1, 5, b[key], help=hints[key], disabled=not editable, key=f"b_{uc['id']}_{key}")
    st.metric(T("Punkte", "Points"), score(b), help=T("Nutzen + Umsetzbarkeit − Aufwand − Risiko", "Benefit + feasibility − effort − risk"))
    st.caption(T(f"Aktueller Rang: {rank}. Die Punkte sind eine Gesprächsgrundlage, keine automatische Entscheidung.",
                 f"Current rank: {rank}. The points are a basis for discussion, not an automatic decision."))
    if editable and st.button(T("Bewertung speichern", "Save assessment"), key=f"b_save_{uc['id']}"):
        uc["bewertung"] = b
        if uc["status"] == "Idee":
            uc["status"] = "Bewertung"
        state.log(uc["id"], T("Bewertung gespeichert", "Assessment saved"), f"{score(b)} {T('Punkte', 'points')}")
        st.rerun()
    if not editable:
        state.deny_hint("bewerten")


def euro(amount: float) -> str:
    text = f"{amount:,.0f} €"
    return text.replace(",", ".") if lang() == "de" else "€" + text[:-2]


def wert(uc: dict) -> None:
    w = uc["wert"]
    editable = state.can("wert_pflegen")
    st.markdown(T("Value Case aus der Prozessaufnahme und gemessener Nutzen im Betrieb: Ziel und Ist je Monat, damit der Nutzen "
                  "nicht nur versprochen, sondern nachgewiesen wird.",
                  "Value case from the process mapping and measured benefit in operation: target and actual per month, so the "
                  "benefit is shown, not just promised."))
    a = value.settings(uc)
    c = st.columns(3)
    rate = c[0].number_input(T("Stundensatz Fachbereich (€/h, voll)", "Business unit hourly cost (€/h, fully loaded)"), 0.0, 300.0,
                             float(a["stundensatz"]), 5.0, disabled=not editable, key=f"w_rate_{uc['id']}")
    dev = c[1].number_input(T("Entwicklungssatz (€/h)", "Development rate (€/h)"), 0.0, 300.0, float(a["entwicklung_satz"]), 5.0,
                            disabled=not editable, key=f"w_dev_{uc['id']}")
    run = c[2].number_input(T("Laufende Kosten (€/Monat)", "Running costs (€/month)"), 0.0, 100000.0, float(a["betrieb_monat"]), 10.0,
                            disabled=not editable, key=f"w_run_{uc['id']}",
                            help=T("Modellnutzung, Hosting, Lizenzen", "Model usage, hosting, licences"))
    preview = dict(uc, wert={"annahmen": {"stundensatz": rate, "entwicklung_satz": dev, "betrieb_monat": run}})
    vc = value.value_case(preview)
    m = st.columns(4)
    m[0].metric(T("Gesparte Stunden pro Monat", "Hours saved per month"), f"{vc.hours_per_month:g} h")
    m[1].metric(T("Netto-Nutzen pro Monat", "Net benefit per month"), euro(vc.net_per_month),
                help=T(f"Nutzen {euro(vc.benefit_per_month)} − laufende Kosten {euro(vc.run_cost_per_month)}",
                       f"Benefit {euro(vc.benefit_per_month)} − running costs {euro(vc.run_cost_per_month)}"))
    payback = "–"
    if vc.payback_months is not None:  # ohne Aufbaukosten oder ohne Netto-Nutzen keine Amortisation
        months = f"{vc.payback_months:g}"
        payback = f"{months.replace('.', ',') if lang() == 'de' else months} {T('Monate', 'months')}"
    m[2].metric(T("Amortisation", "Payback"), payback,
                help=T(f"Aufbaukosten {euro(vc.build_cost)} aus den Personentagen im IT-Check",
                       f"Build cost {euro(vc.build_cost)} from the person-days in the IT check"))
    m[3].metric(T("ROI im ersten Jahr", "First-year ROI"), f"{vc.roi_first_year:.0%}" if vc.roi_first_year is not None else "–")
    if editable and st.button(T("Annahmen speichern", "Save assumptions"), key=f"w_save_{uc['id']}"):
        w["annahmen"] = {"stundensatz": rate, "entwicklung_satz": dev, "betrieb_monat": run}
        state.log(uc["id"], T("Value Case aktualisiert", "Value case updated"), f"{euro(vc.net_per_month)}/{T('Monat', 'month')}")
        st.success(T("Gespeichert.", "Saved."))
    st.caption(T("Annahmen sind Schätzungen und werden mit dem Fachbereich abgestimmt. Die Zahlen sind eine Entscheidungshilfe, "
                 "kein Versprechen.", "Assumptions are estimates agreed with the business unit. The figures support a decision; "
                 "they are not a promise."))

    st.markdown(f"**{T('Gemessener Nutzen', 'Measured benefit')}**")
    rows = []
    for e in sorted(w.get("messungen", []), key=lambda e: e["monat"]):
        share, level = value.realisation(e["ziel"], e["ist"])
        rows.append({T("Monat", "Month"): e["monat"], T("Ziel (h)", "Target (h)"): e["ziel"], T("Ist (h)", "Actual (h)"): e["ist"],
                     T("Nutzende", "Users"): e.get("nutzende", 0),
                     T("Realisierung", "Realisation"): f"{AMPEL_DOT[level]} {share:.0%}" if share is not None else "–"})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.info(T("Noch keine Messung. Gemessen wird ab Pilot.", "No measurement yet. Measuring starts with the pilot."))
    if editable:
        with st.form(f"w_add_{uc['id']}"):
            f = st.columns(4)
            month = f[0].text_input(T("Monat (JJJJ-MM)", "Month (YYYY-MM)"), date.today().strftime("%Y-%m"))
            target = f[1].number_input(T("Ziel (h)", "Target (h)"), 0.0, 10000.0, 0.0, 1.0)
            actual = f[2].number_input(T("Ist (h)", "Actual (h)"), 0.0, 10000.0, 0.0, 1.0)
            users = f[3].number_input(T("Nutzende", "Users"), 0, 10000, 0)
            if st.form_submit_button(T("Messung speichern", "Save measurement")):
                if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month.strip()):
                    st.error(T("Monat bitte als JJJJ-MM eingeben, z. B. 2026-11.", "Please enter the month as YYYY-MM, e.g. 2026-11."))
                else:
                    w.setdefault("messungen", []).append({"monat": month.strip(), "ziel": target, "ist": actual, "nutzende": int(users)})
                    state.log(uc["id"], T("Nutzen gemessen", "Benefit measured"), f"{month.strip()}: {actual:g} / {target:g} h")
                    st.rerun()
    else:
        state.deny_hint("wert_pflegen")


AMPEL_DOT = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴", "offen": "⚪"}


def entscheidung(uc: dict, rank: int) -> None:
    st.download_button(T("📄 Entscheidungsvorlage als PDF", "📄 Decision paper as PDF"), pdf.entscheidungsvorlage(uc, rank, lang()),
                       file_name=T(f"Entscheidungsvorlage_{uc['id']}.pdf", f"Decision_paper_{uc['id']}.pdf"), mime="application/pdf")
    d = uc.get("entscheidung") or {}
    if d:
        st.info(T(f"Entscheidung vom {d['datum']}: **{decision(d['ergebnis'])}**. {d['begruendung']}",
                  f"Decision of {d['datum']}: **{decision(d['ergebnis'])}**. {d['begruendung']}"))
    if state.can("entscheiden"):
        ds_ok = uc["datenschutz"].get("freigabe") == "freigegeben"
        it_ok = uc["it"].get("freigabe") == "freigegeben"
        ai_ok = uc["aiact"].get("freigabe") == "freigegeben"
        missing = [x for x, ok in [(T("Datenschutz", "data protection"), ds_ok), ("Compliance (AI Act)", ai_ok), ("IT", it_ok)] if not ok]
        if missing:
            st.warning(T(f"Noch keine Freigabe von: {', '.join(missing)}. Eine Umsetzung ist erst danach möglich.",
                         f"No approval yet from: {', '.join(missing)}. Implementation is only possible afterwards."))
        options = {"Freigegeben": T("Freigeben", "Approve"), "Zurückgestellt": T("Zurückstellen", "Put on hold"),
                   "Abgelehnt": T("Ablehnen", "Reject")}
        with st.form(f"dec_{uc['id']}"):
            result = st.radio(T("Entscheidung", "Decision"), list(options), format_func=options.get, horizontal=True)
            reason = st.text_area(T("Begründung", "Reason"), height=70)
            if st.form_submit_button(T("Entscheidung festhalten", "Record decision"), type="primary"):
                if result == "Freigegeben" and missing:
                    st.error(T(f"Freigabe nicht möglich: Freigabe von {' und '.join(missing)} fehlt.",
                               f"Approval not possible: approval from {' and '.join(missing)} is missing."))
                elif not reason.strip():
                    st.error(T("Bitte kurz begründen, damit die Entscheidung nachvollziehbar bleibt.",
                               "Please give a short reason so the decision stays traceable."))
                else:
                    uc["entscheidung"] = {"ergebnis": result, "begruendung": reason.strip(), "datum": date.today().isoformat()}
                    uc["status"] = "Prototyp" if result == "Freigegeben" else "Zurückgestellt"
                    state.log(uc["id"], T("Entscheidung: ", "Decision: ") + decision(result), reason.strip())
                    st.rerun()
    else:
        state.deny_hint("entscheiden")
    st.divider()
    if state.can("status_aendern"):
        new = st.selectbox(T("Projektstatus", "Project status"), STATUSES, index=STATUSES.index(uc["status"]), format_func=status,
                           key=f"status_{uc['id']}")
        if new != uc["status"] and st.button(T("Status übernehmen", "Apply status"), key=f"status_btn_{uc['id']}"):
            state.log(uc["id"], T("Status geändert", "Status changed"), f"{status(uc['status'])} → {status(new)}")
            uc["status"] = new
            st.rerun()


def pruefstand(uc: dict) -> None:
    st.markdown(T("Ergebnisse werden mit echten Fragen aus dem Fachbereich geprüft. Die Trefferquote und die erkannten Grenzen fließen in die Entscheidung ein.",
                  "Results are checked with real questions from the business unit. The hit rate and the limits found feed into the decision."))
    if uc["id"] == "A":
        live_assistant(uc)
    tests = uc["tests"]
    if tests:
        df = pd.DataFrame(tests).reindex(columns=["frage", "erwartet", "antwort", "bewertung"])
        df = df.fillna("–").replace("", "–")
        df["bewertung"] = df["bewertung"].map(verdict)
        st.dataframe(df.rename(columns={"frage": T("Testfrage", "Test question"), "erwartet": T("Erwartet", "Expected"),
                                        "antwort": T("Antwort der KI", "AI answer"), "bewertung": T("Bewertung", "Verdict")}),
                     hide_index=True, use_container_width=True)
        correct = sum(t["bewertung"] == "richtig" for t in tests)
        st.metric(T("Trefferquote", "Hit rate"), f"{correct / len(tests):.0%}",
                  help=T(f"{correct} von {len(tests)} Testfragen richtig", f"{correct} of {len(tests)} test questions correct"))
    else:
        st.info(T("Noch keine Testfälle.", "No test cases yet."))
    verdicts = {v: verdict(v) for v in ["richtig", "teilweise", "falsch"]}
    if state.can("testen"):
        with st.form(f"test_add_{uc['id']}"):
            st.markdown(f"**{T('Testfall von Hand erfassen', 'Add a test case manually')}**")
            q = st.text_input(T("Testfrage oder Eingabe", "Test question or input"))
            exp = st.text_input(T("Erwartetes Ergebnis", "Expected result"))
            got = st.text_input(T("Ergebnis der KI", "AI result"))
            v = st.radio(T("Bewertung", "Verdict"), list(verdicts), format_func=verdicts.get, horizontal=True)
            if st.form_submit_button(T("Testfall speichern", "Save test case")) and q.strip():
                tests.append({"frage": q, "erwartet": exp, "antwort": got, "bewertung": v})
                state.log(uc["id"], T("Testfall erfasst", "Test case added"), f"{verdict(v)}: {q[:60]}")
                st.rerun()
    grenzen = st.text_area(T("Dokumentierte Grenzen", "Documented limits"), uc.get("grenzen", ""), height=70, key=f"grenzen_{uc['id']}",
                           disabled=not state.can("testen"))
    if state.can("testen") and grenzen != uc.get("grenzen", "") and st.button(T("Grenzen speichern", "Save limits"), key=f"gr_{uc['id']}"):
        uc["grenzen"] = grenzen
        state.log(uc["id"], T("Grenzen dokumentiert", "Limits documented"))
        st.success(T("Gespeichert.", "Saved."))


def live_assistant(uc: dict) -> None:
    st.markdown("##### " + T("Live-Test: Wissensassistent", "Live test: knowledge assistant"))
    question = st.text_input(T("Frage an den Assistenten", "Question for the assistant"),
                             T("Wie schnell bekommt ein Mitglied eine Ersatzkarte?", "How fast does a member get a replacement card?"),
                             key=f"la_q_{lang()}")
    if st.button(T("Assistent fragen", "Ask the assistant"), type="primary", key="la_btn") and question.strip():
        clean, counts = pseudonymise(question)
        hits = knowledge_index(lang()).search(clean, k=3)
        if not hits:
            result = {"gefunden": False, "antwort": "", "quellen": []}
        elif llm.available() and state.llm_budget_ok():
            context = "\n\n".join(f"[{s.id}] {s.title} – {s.section}\n{s.text}" for s, _ in hits)
            with st.spinner(T("Assistent sucht …", "The assistant is searching …")):
                _, system = llm.prompts(lang())
                result = llm.chat_json(system, f"{T('Auszüge', 'Excerpts')}:\n{context}\n\n{T('Frage', 'Question')}: {clean}")
        else:
            top = hits[0][0]
            result = {"gefunden": True, "antwort": top.text.split(". ")[0] + ".", "quellen": [top.id]}
        allowed = {s.id: s for s, _ in hits}
        sources = [allowed[i] for i in result.get("quellen", []) if i in allowed]
        found = result.get("gefunden") and result.get("antwort") and sources
        if found:
            st.success(result["antwort"])
            for s in sources:
                st.caption(f"📄 {s.title} → {s.section} ({T('Bereich', 'Area')} {s.area})")
        else:
            st.warning(T("Die Unterlagen enthalten dazu keine Antwort. Der Assistent rät nicht.",
                         "The documents contain no answer to this. The assistant does not guess."))
        if counts:
            st.caption(T("Vor dem Modellaufruf ersetzt: ", "Replaced before the model call: ") + ", ".join(f"{v}× {k}" for k, v in counts.items()))
        st.session_state.last_answer = (question, result.get("antwort", "") if found else T("keine Antwort", "no answer"))
    if "last_answer" in st.session_state and state.can("testen"):
        q, a = st.session_state.last_answer
        cols = st.columns(3)
        for col, v in zip(cols, ["richtig", "teilweise", "falsch"], strict=True):
            if col.button(T(f"Als „{verdict(v)}“ übernehmen", f"Record as \"{verdict(v)}\""), key=f"la_{v}"):
                uc["tests"].append({"frage": q, "erwartet": "", "antwort": a, "bewertung": v})
                state.log(uc["id"], T("Live-Test bewertet", "Live test rated"), f"{verdict(v)}: {q[:60]}")
                del st.session_state.last_answer
                st.rerun()


def verlauf(uc: dict) -> None:
    entries = [e | {"rolle": role(e["rolle"])} for e in st.session_state.log if e["usecase"] == uc["id"]]
    if entries:
        st.dataframe(pd.DataFrame(entries[::-1]).rename(columns={
            "datum": T("Datum", "Date"), "rolle": T("Rolle", "Role"), "usecase": T("Fall", "Case"), "aktion": T("Aktion", "Action"),
            "details": "Details"}), hide_index=True, use_container_width=True)
    else:
        st.info(T("Noch keine Einträge.", "No entries yet."))
