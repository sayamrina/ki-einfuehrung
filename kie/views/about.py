import streamlit as st

from .. import ui
from ..i18n import T

ABOUT_DE = """
**Was die Plattform zeigt:** den gesamten Arbeitszyklus eines AI Solutions Managers, vom ersten Gespräch mit dem Fachbereich bis zur Einführung.

1. **Idee einreichen:** Der Fachbereich beschreibt ein Problem in eigenen Worten; die KI strukturiert es zu einem Steckbrief. Personenbezogene Daten werden vorher entfernt.
2. **Prozessaufnahme:** Arbeitsschritte und Zeiten heute und mit KI; daraus ergibt sich die geschätzte Zeitersparnis.
3. **Datenschutz-Check:** Risiken und Schutzmaßnahmen ergeben eine Ampel; der Datenschutz gibt frei oder nicht.
4. **Bewertung:** Nutzen, Aufwand, Umsetzbarkeit und Risiko ergeben Punkte und einen Rang als Gesprächsgrundlage.
5. **Entscheidung:** Die Geschäftsführung entscheidet mit Begründung; die Entscheidungsvorlage gibt es als PDF.
6. **Prüfstand:** Ergebnisse werden mit echten Testfragen geprüft, Grenzen werden dokumentiert.
7. **90-Tage-Plan und Projekt-Board:** Jeder sieht, wo ein Vorhaben steht.
8. **KI-Führerschein:** Schulung mit Abschlusstest, Zertifikat und Auswertung für Trainer.
9. **KI-Radar und Protokoll:** neue Werkzeuge nüchtern bewertet; jede Entscheidung nachvollziehbar.

**Technik:** Python, Streamlit, OpenAI (gpt-4o-mini) mit regelbasiertem Offline-Modus, Pseudonymisierung vor jedem Modellaufruf,
Suche in der Wissensbasis per BM25, PDF-Export, automatisierte Tests. Oberfläche auf Deutsch und Englisch.

**Hinweise:** Alle Inhalte sind Beispieldaten aus der Logistikbranche. Eingaben bleiben in Ihrer Sitzung und werden nicht gespeichert.

Diese App wurde von Amrina entwickelt, mit KI als unterstützendem Werkzeug beim Programmieren.
"""

ABOUT_EN = """
**What the platform shows:** the whole work cycle of an AI Solutions Manager, from the first talk with a business unit to the rollout.

1. **Submit an idea:** The business unit describes a problem in its own words; the AI turns it into a brief. Personal data is removed first.
2. **Process mapping:** Work steps and times today and with AI; this gives the estimated time saving.
3. **Data protection check:** Risks and safeguards give a traffic light; data protection approves or not.
4. **Assessment:** Benefit, effort, feasibility and risk give points and a rank as a basis for discussion.
5. **Decision:** Management decides with a reason; the decision paper is available as a PDF.
6. **Test bench:** Results are checked with real test questions, and limits are documented.
7. **90-day plan and project board:** Everyone can see where a project stands.
8. **AI licence:** Training with a final test, certificate and results for trainers.
9. **AI radar and log:** new tools assessed soberly; every decision traceable.

**Technology:** Python, Streamlit, OpenAI (gpt-4o-mini) with a rule-based offline mode, pseudonymisation before every model call,
BM25 search in the knowledge base, PDF export, automated tests. Interface in German and English.

**Notes:** All content is sample data from the logistics sector. Inputs stay in your session and are not stored.

This app was built by Amrina, with AI as a supporting tool for coding.
"""


def render() -> None:
    ui.hero(T("Über das Projekt", "About the project"),
            T("Ein KI-Projekt von Amrina: die Arbeit eines AI Solutions Managers als durchgängiger, transparenter Ablauf. ",
              "An AI project by Amrina: the work of an AI Solutions Manager as one continuous, transparent workflow. ")
            + "<a href='https://sayamrina.github.io/' target='_blank'>Portfolio</a>")
    st.markdown(T(ABOUT_DE, ABOUT_EN))
