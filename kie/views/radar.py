from datetime import date

import pandas as pd
import streamlit as st

from .. import state, ui
from ..i18n import T

RATINGS = ["Einsetzen", "Testen", "Beobachten"]
RATING_EN = {"Einsetzen": "Adopt", "Testen": "Trial", "Beobachten": "Watch"}


def rating(value: str) -> str:
    return T(value, RATING_EN.get(value, value))


def render() -> None:
    ui.hero(T("KI-Radar", "AI radar"),
            T("Neue Modelle und Werkzeuge werden ausprobiert und nüchtern bewertet: Was bringt es uns, und was bedeutet es für den Datenschutz?",
              "New models and tools are tried out and assessed soberly: what do they bring us, and what do they mean for data protection?"))
    df = pd.DataFrame(st.session_state.radar)
    labels = {"Alle": T("Alle", "All")} | {r: rating(r) for r in RATINGS}
    choice = st.segmented_control(T("Einschätzung", "Rating"), list(labels), default="Alle", format_func=labels.get)
    if choice and choice != "Alle":
        df = df[df["einschaetzung"] == choice]
    df = df.assign(einschaetzung=df["einschaetzung"].map(rating))
    df = df[["name", "einschaetzung", "kategorie", "einsatz", "datenschutz", "geprueft"]].rename(columns={
        "name": T("Werkzeug", "Tool"), "kategorie": T("Kategorie", "Category"), "einsatz": T("Möglicher Einsatz", "Possible use"),
        "datenschutz": T("Datenschutz", "Data protection"), "einschaetzung": T("Einschätzung", "Rating"), "geprueft": T("Geprüft", "Checked")})
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.caption(T("Einsetzen: freigegeben für passende Fälle · Testen: im Prototyp prüfen · Beobachten: noch nicht reif oder rechtlich unklar",
                 "Adopt: approved for suitable cases · Trial: check in a prototype · Watch: not mature yet or legally unclear"))
    if state.can("radar_bearbeiten"):
        with st.form("radar_add"):
            st.markdown("**" + T("Neues Werkzeug erfassen", "Add a new tool") + "**")
            c = st.columns(2)
            name = c[0].text_input(T("Werkzeug", "Tool"))
            cat = c[1].text_input(T("Kategorie", "Category"))
            use = st.text_input(T("Möglicher Einsatz", "Possible use"))
            ds = st.text_input(T("Datenschutz-Einschätzung", "Data protection assessment"))
            labels = {r: rating(r) for r in RATINGS}
            value = st.radio(T("Einschätzung", "Rating"), RATINGS, format_func=labels.get, horizontal=True, index=1)
            if st.form_submit_button(T("Hinzufügen", "Add")) and name.strip():
                st.session_state.radar.append({"name": name, "kategorie": cat, "einsatz": use, "datenschutz": ds,
                                               "einschaetzung": value, "geprueft": date.today().strftime("%Y-%m")})
                state.log("-", T("KI-Radar ergänzt", "AI radar updated"), name)
                st.rerun()
    else:
        state.deny_hint("radar_bearbeiten")
