import pandas as pd
import streamlit as st

from .. import state, ui
from ..i18n import T, role


def render() -> None:
    ui.hero(T("Protokoll und Rechte", "Log and permissions"),
            T("Jede Entscheidung, Freigabe und Änderung ist nachvollziehbar festgehalten. Rollen regeln, wer welchen Schritt ausführen darf.",
              "Every decision, approval and change is recorded in a traceable way. Roles define who may carry out which step."))
    st.subheader(T("Entscheidungsprotokoll", "Decision log"))
    log = pd.DataFrame([e | {"rolle": role(e["rolle"])} for e in st.session_state.log[::-1]]).rename(columns={
        "datum": T("Datum", "Date"), "rolle": T("Rolle", "Role"), "usecase": T("Fall", "Case"), "aktion": T("Aktion", "Action"),
        "details": "Details"})
    st.dataframe(log, hide_index=True, use_container_width=True)
    st.download_button(T("Protokoll als CSV", "Log as CSV"), log.to_csv(index=False).encode("utf-8"),
                       file_name=T("ki-protokoll.csv", "ai-log.csv"), mime="text/csv")
    st.subheader(T("Rollen und Rechte", "Roles and permissions"))
    rows = [{T("Schritt", "Step"): state.right_label(r), **{role(x): "✅" if x in roles else "–" for x in state.ROLES}}
            for r, roles in state.RIGHTS.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption(T("Die Rolle wird links gewählt. In einem Echtbetrieb käme sie aus der Firmenanmeldung (z. B. Microsoft Entra ID).",
                 "The role is chosen on the left. In production it would come from the company sign-in (e.g. Microsoft Entra ID)."))
