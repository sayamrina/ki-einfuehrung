import altair as alt
import pandas as pd
import streamlit as st

from .. import ui
from ..i18n import T, lang, status
from ..scoring import ampel, ranking, score, time_saving


def render() -> None:
    ui.hero(T("KI-Einführung", "AI Adoption"),
            T("Vom Vorschlag aus dem Fachbereich bis zur sicheren Anwendung im Alltag: alle KI-Vorhaben, Entscheidungen und Ergebnisse an einem Ort.",
              "From a business unit's suggestion to safe everyday use: all AI initiatives, decisions and results in one place."))
    ucs = st.session_state.usecases
    ranks = ranking(ucs)
    hours = sum(time_saving(u["prozess"], u["faelle_pro_monat"]).hours_per_month for u in ucs if u["status"] in ("Pilot", "Einführung"))
    c = st.columns(4)
    c[0].metric(T("Vorhaben gesamt", "Initiatives"), len(ucs))
    c[1].metric(T("In Umsetzung", "In progress"), sum(u["status"] in ("Prototyp", "Pilot") for u in ucs))
    c[2].metric(T("Warten auf Entscheidung", "Awaiting decision"), sum(u["status"] == "Entscheidung" for u in ucs))
    c[3].metric(T("Zeitersparnis im Pilot", "Time saved in pilot"), f"{hours:g} h/{T('Monat', 'month')}",
                help=T("Schätzung aus der Prozessaufnahme der Fachbereiche", "Estimate from the business units' process mapping"))

    st.subheader(T("Projekt-Board", "Project board"))
    lanes = [(T("Ideen und Bewertung", "Ideas and assessment"), {"Idee", "Bewertung"}), (T("Entscheidung", "Decision"), {"Entscheidung"}),
             (T("In Umsetzung", "In progress"), {"Prototyp", "Pilot"}), (T("Eingeführt", "Rolled out"), {"Einführung"}),
             (T("Zurückgestellt", "On hold"), {"Zurückgestellt"})]
    cols = st.columns(len(lanes))
    for col, (lane, statuses) in zip(cols, lanes, strict=True):
        with col:
            items = sorted((x for x in ucs if x["status"] in statuses), key=lambda x: ranks[x["id"]])
            st.markdown(f'<div class="kie-col"><h5>{lane} ({len(items)})</h5></div>', unsafe_allow_html=True)
            for u in items:
                level = ampel(u["datenschutz"].get("antworten", {}), lang())[0]
                text, kind = ui.ampel_badge(level)
                badges = (ui.badge(status(u["status"])) + ui.badge(T("Rang ", "Rank ") + str(ranks[u["id"]]))
                          + f'<div class="kie-ampel {kind}">{ui.esc(text)}</div>')
                st.markdown(f'<div class="kie-card" lang="{lang()}"><h4>{u["id"]}. {ui.esc(u["titel"])}</h4>'
                            f'<div class="kie-muted">{ui.esc(u["fachbereich"])}</div>{badges}</div>', unsafe_allow_html=True)
            if not items:
                st.markdown('<div class="kie-muted">–</div>', unsafe_allow_html=True)

    st.subheader(T("Prioritäten", "Priorities"))
    left, right = st.columns([1.15, 1])
    col_uc, col_benefit, col_effort, col_points, col_rank, col_status = (
        T("Anwendungsfall", "Use case"), T("Nutzen", "Benefit"), T("Aufwand", "Effort"), T("Punkte", "Points"), T("Rang", "Rank"), "Status")
    df = pd.DataFrame([{"ID": u["id"], col_uc: u["titel"], col_benefit: u["bewertung"]["nutzen"], col_effort: u["bewertung"]["aufwand"],
                        col_points: score(u["bewertung"]), col_rank: ranks[u["id"]], col_status: status(u["status"])} for u in ucs])
    with left:
        grid = {"values": [1, 2, 3, 4, 5], "grid": True, "gridColor": "#eef1f4"}
        base = alt.Chart(df).encode(
            x=alt.X(f"{col_effort}:Q", scale=alt.Scale(domain=[0.5, 5.5]), axis=alt.Axis(title=T("Aufwand (1 = gering)", "Effort (1 = low)"), **grid)),
            y=alt.Y(f"{col_benefit}:Q", scale=alt.Scale(domain=[0.5, 5.5]), axis=alt.Axis(title=T("Nutzen (5 = hoch)", "Benefit (5 = high)"), **grid)),
            tooltip=[col_uc, col_benefit, col_effort, col_points, col_rank, col_status])
        points = base.mark_circle(size=320, color="#2a78d6", opacity=0.9, stroke="#fcfcfb", strokeWidth=2)
        labels = base.mark_text(color="#ffffff", fontWeight="bold", fontSize=12).encode(text="ID:N")
        title = alt.TitleParams(T("Nutzen und Aufwand je Anwendungsfall", "Benefit and effort per use case"),
                                subtitle=T("Oben links: schnelle Erfolge mit hohem Nutzen und wenig Aufwand",
                                           "Top left: quick wins with high benefit and low effort"), subtitleColor="#52514e", anchor="start")
        st.altair_chart((points + labels).properties(height=330, title=title), use_container_width=True)
    with right:
        st.dataframe(df.sort_values(col_rank)[[col_rank, col_points, col_uc]].assign(**{col_uc: df[col_uc].radd(df["ID"] + ". ")}),
                     hide_index=True, use_container_width=True,
                     column_config={col_rank: st.column_config.NumberColumn(width="small"), col_points: st.column_config.NumberColumn(width="small")})
        st.caption(T("Punkte = Nutzen + Umsetzbarkeit − Aufwand − Datenschutzrisiko. Die Punkte sind eine Gesprächsgrundlage für die "
                     "Geschäftsführung, keine automatische Entscheidung.",
                     "Points = benefit + feasibility − effort − data protection risk. The points are a basis for discussion with "
                     "management, not an automatic decision."))
