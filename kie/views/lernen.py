import altair as alt
import pandas as pd
import streamlit as st

from .. import pdf, ui
from ..course import PASS_MARK, content
from ..i18n import T, lang


def render() -> None:
    modules, scenarios, quiz = content(lang())
    ui.hero(T("KI-Führerschein: Sicher arbeiten mit KI", "AI licence: working safely with AI"),
            T("Kurzer Online-Kurs für alle Mitarbeitenden: vier Module, Übungen aus dem Arbeitsalltag, Abschlusstest und Zertifikat.",
              "Short online course for all employees: four modules, exercises from daily work, a final test and a certificate."))
    tab_kurs, tab_test, tab_auswertung = st.tabs([T("Kurs", "Course"), T("Abschlusstest", "Final test"),
                                                  T("Auswertung für Trainer", "Results for trainers")])
    with tab_kurs:
        for m in modules:
            with st.expander(f"{m['titel']} · {m['dauer']}", expanded=m is modules[0]):
                for line in m["inhalt"]:
                    st.markdown(f"- {line}")
        st.markdown("#### " + T("Übung: Wie würden Sie entscheiden?", "Exercise: what would you decide?"))
        for i, sc in enumerate(scenarios):
            choice = st.radio(sc["frage"], sc["optionen"], index=None, key=f"sc_{lang()}_{i}")
            if choice is not None:
                if sc["optionen"].index(choice) == sc["richtig"]:
                    st.success(T("Richtig. ", "Correct. ") + sc["erklaerung"])
                else:
                    st.error(T("Nicht ganz. ", "Not quite. ") + sc["erklaerung"])
    with tab_test:
        with st.form("quiz"):
            name = st.text_input(T("Name für das Zertifikat (optional)", "Name for the certificate (optional)"))
            picks = {q["id"]: st.radio(q["frage"], q["optionen"], index=None, key=f"quiz_{lang()}_{q['id']}") for q in quiz}
            done = st.form_submit_button(T("Test auswerten", "Check test"), type="primary")
        if done:
            wrong = [q["id"] for q in quiz if picks[q["id"]] is None or q["optionen"].index(picks[q["id"]]) != q["richtig"]]
            quote = (len(quiz) - len(wrong)) / len(quiz)
            stats = st.session_state.course_stats
            stats["teilnehmende"] += 1
            stats["bestanden"] += quote >= PASS_MARK
            for qid in wrong:
                stats["falsch_pro_frage"][qid] += 1
            st.session_state.quiz_result = (name, quote)
        if st.session_state.quiz_result:
            name, quote = st.session_state.quiz_result
            if quote >= PASS_MARK:
                st.success(T(f"Bestanden mit {quote:.0%}.", f"Passed with {quote:.0%}."))
                st.download_button(T("🎓 Zertifikat als PDF", "🎓 Certificate as PDF"), pdf.zertifikat(name, quote, lang()),
                                   file_name=T("KI-Fuehrerschein_Zertifikat.pdf", "AI_Licence_Certificate.pdf"), mime="application/pdf")
            else:
                st.warning(T(f"{quote:.0%} richtig. Zum Bestehen sind {PASS_MARK:.0%} nötig. Die Module helfen beim zweiten Versuch.",
                             f"{quote:.0%} correct. You need {PASS_MARK:.0%} to pass. The modules help with a second try."))
    with tab_auswertung:
        stats = st.session_state.course_stats
        c = st.columns(3)
        c[0].metric(T("Teilnehmende", "Participants"), stats["teilnehmende"])
        c[1].metric(T("Bestanden", "Passed"), f"{stats['bestanden'] / max(stats['teilnehmende'], 1):.0%}")
        c[2].metric(T("Zufriedenheit", "Satisfaction"), T(f"{sum(stats['feedback']) / len(stats['feedback']):.1f} von 5".replace(".", ","),
                                                          f"{sum(stats['feedback']) / len(stats['feedback']):.1f} of 5"))
        q_col, n_col = T("Frage", "Question"), T("Falsche Antworten", "Wrong answers")
        df = pd.DataFrame([{q_col: f"{q['id'].upper()}: {q['frage'][:55]}…", n_col: stats["falsch_pro_frage"][q["id"]]} for q in quiz])
        chart = alt.Chart(df).mark_bar(color="#2a78d6", cornerRadiusEnd=4, height=18).encode(
            x=alt.X(f"{n_col}:Q", axis=alt.Axis(grid=True, gridColor="#eef1f4", tickMinStep=1)),
            y=alt.Y(f"{q_col}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=380)),
            tooltip=[q_col, n_col]).properties(height=230, title=T("Wo braucht das Team mehr Erklärung?",
                                                                    "Where does the team need more explanation?"))
        st.altair_chart(chart, use_container_width=True)
        hardest = max(stats["falsch_pro_frage"], key=stats["falsch_pro_frage"].get)
        st.caption(T(f"Am häufigsten falsch: {hardest.upper()}. Diese Frage wird im nächsten Kurs mit einem Beispiel vertieft. "
                     "Werte vor dieser Sitzung sind Beispieldaten.",
                     f"Most often wrong: {hardest.upper()}. This question gets an extra example in the next course. "
                     "Values before this session are sample data."))
