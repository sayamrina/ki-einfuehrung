import altair as alt
import pandas as pd
import streamlit as st

from .. import ui, value
from ..i18n import T, lang, status
from .usecase import AMPEL_DOT, euro


def render() -> None:
    ui.hero(T("Wertbeitrag und Quartalsbericht", "Value tracking and quarterly review"),
            T("Value Case je Anwendungsfall und gemessener Nutzen im Quartal: Grundlage für den Quartalsbericht (QBR) an die Geschäftsführung.",
              "Value case per use case and measured benefit per quarter: the basis for the quarterly business review (QBR) for management."))
    ucs = st.session_state.usecases

    st.subheader(T("Value Cases im Portfolio", "Value cases in the portfolio"))
    rows = []
    for u in ucs:
        if u["status"] == "Zurückgestellt":
            continue
        vc = value.value_case(u)
        rows.append({"ID": u["id"], T("Anwendungsfall", "Use case"): u["titel"], "Status": status(u["status"]),
                     T("Stunden/Monat", "Hours/month"): vc.hours_per_month,
                     T("Netto-Nutzen/Monat", "Net benefit/month"): euro(vc.net_per_month),
                     T("Aufbaukosten", "Build cost"): euro(vc.build_cost) if vc.build_cost else "–",
                     T("Amortisation (Monate)", "Payback (months)"): vc.payback_months if vc.payback_months else "–",
                     "_net": vc.net_per_month})
    df = pd.DataFrame(rows).sort_values("_net", ascending=False)
    st.dataframe(df.drop(columns="_net"), hide_index=True, use_container_width=True)
    st.caption(T("Ohne IT-Check sind noch keine Aufbaukosten erfasst, deshalb fehlt dort die Amortisation.",
                 "Without an IT check no build cost is recorded yet, so payback is missing there."))

    st.subheader(T("Quartalsbericht", "Quarterly review"))
    options = value.periods(ucs)
    if not options:
        st.info(T("Noch keine Messungen. Messungen werden im Anwendungsfall unter „Wert“ erfasst.",
                  "No measurements yet. Measurements are recorded in the use case under “Value”."))
        return
    period = st.selectbox(T("Quartal", "Quarter"), options, key="qbr_period")
    qrows = value.qbr(ucs, period)
    target = sum(r["ziel_h"] for r in qrows)
    actual = sum(r["ist_h"] for r in qrows)
    c = st.columns(3)
    c[0].metric(T("Gesparte Stunden", "Hours saved"), f"{actual:g} h", help=T(f"Ziel: {target:g} h", f"Target: {target:g} h"))
    c[1].metric(T("Realisierung", "Realisation"), f"{actual / target:.0%}" if target else "–")
    c[2].metric(T("Wert im Quartal", "Value in the quarter"), euro(sum(r["wert_eur"] for r in qrows)))

    chart = pd.DataFrame([{"ID": r["id"], T("Art", "Type"): T("Ziel", "Target"), T("Stunden", "Hours"): r["ziel_h"]} for r in qrows]
                         + [{"ID": r["id"], T("Art", "Type"): T("Ist", "Actual"), T("Stunden", "Hours"): r["ist_h"]} for r in qrows])
    kind, hours = T("Art", "Type"), T("Stunden", "Hours")
    order = [T("Ziel", "Target"), T("Ist", "Actual")]
    bars = alt.Chart(chart).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=34).encode(
        x=alt.X("ID:N", title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset(f"{kind}:N", sort=order),
        y=alt.Y(f"{hours}:Q", title=T("Stunden im Quartal", "Hours in the quarter")),
        color=alt.Color(f"{kind}:N", sort=order, scale=alt.Scale(domain=order, range=["#9fb3c8", "#12355b"]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["ID", kind, hours])
    st.altair_chart(bars.properties(height=240, width=alt.Step(90)), use_container_width=False)

    table = pd.DataFrame([{"ID": r["id"], T("Anwendungsfall", "Use case"): r["titel"], "Status": status(r["status"]),
                           T("Ziel (h)", "Target (h)"): r["ziel_h"], T("Ist (h)", "Actual (h)"): r["ist_h"],
                           T("Realisierung", "Realisation"): f"{AMPEL_DOT[r['ampel']]} {r['realisierung']:.0%}",
                           T("Wert", "Value"): euro(r["wert_eur"]), T("Nutzende", "Users"): r["nutzende"]} for r in qrows])
    st.dataframe(table, hide_index=True, use_container_width=True)

    st.markdown(f"**{T('Kernaussagen für den QBR', 'Key messages for the QBR')}**")
    lines = value.summary(qrows, lang())
    for line in lines:
        st.markdown(f"- {line}")
    md_table = "\n".join(["| " + " | ".join(table.columns) + " |", "|" + " --- |" * len(table.columns)]
                         + ["| " + " | ".join(str(v) for v in row) + " |" for row in table.itertuples(index=False)])
    report = f"# QBR {period}\n\n" + "\n".join(f"- {line}" for line in lines) + "\n\n" + md_table + "\n"
    a, b = st.columns(2)
    a.download_button(T("QBR als Markdown", "QBR as Markdown"), report.encode("utf-8"), file_name=f"QBR_{period}.md", mime="text/markdown")
    b.download_button(T("Zahlen als CSV", "Figures as CSV"), table.to_csv(index=False).encode("utf-8"), file_name=f"QBR_{period}.csv",
                      mime="text/csv")
    st.caption(T("Ampel: ab 90 % des Ziels grün, ab 60 % gelb, darunter rot. Die Kernaussagen werden aus den Zahlen abgeleitet, "
                 "nicht von einem Sprachmodell geschrieben.",
                 "Light: green from 90 % of target, amber from 60 %, red below. The key messages are derived from the figures, "
                 "not written by a language model."))
