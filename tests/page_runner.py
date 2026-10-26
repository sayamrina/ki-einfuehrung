"""Runs a single page for AppTest (st.navigation pages cannot be switched to directly in tests)."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kie import state  # noqa: E402
from kie.views import about, idee, lernen, plan, protokoll, radar, sop, uebersicht, usecase, wert  # noqa: E402

state.init()
pages = {"uebersicht": uebersicht, "plan": plan, "idee": idee, "usecase": usecase, "lernen": lernen,
         "radar": radar, "protokoll": protokoll, "about": about, "sop": sop, "wert": wert}
pages[st.session_state.get("page", "uebersicht")].render()
