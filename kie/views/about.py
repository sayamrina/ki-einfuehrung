import streamlit as st

from .. import ui
from ..i18n import T

ABOUT_DE = """
**Was die Plattform zeigt:** den gesamten Arbeitszyklus eines AI Solutions Managers, vom ersten Gespräch mit dem Fachbereich bis zur Einführung.

1. **Idee einreichen:** Der Fachbereich beschreibt ein Problem in eigenen Worten; die KI strukturiert es zu einem Steckbrief. Personenbezogene Daten werden vorher entfernt.
2. **Prozessaufnahme:** Arbeitsschritte und Zeiten heute und mit KI; daraus ergibt sich die geschätzte Zeitersparnis.
3. **Datenschutz-, AI-Act- und IT-Check:** Risiken und Schutzmaßnahmen ergeben eine Datenschutz-Ampel. Die Einstufung nach dem EU AI Act (verboten, Hochrisiko, Transparenz, minimal) zeigt die Pflichten, ein GxP-Check ergänzt regulierte Prozesse; Compliance bestätigt. Die IT prüft Schnittstellen, Hosting, Anmeldung, Betrieb und Kosten.
4. **Bewertung:** Nutzen, Aufwand, Umsetzbarkeit und Risiko ergeben Punkte und einen Rang als Gesprächsgrundlage.
5. **Entscheidung:** Die Geschäftsführung entscheidet mit Begründung, erst nach Freigabe durch Datenschutz, Compliance und IT; die Entscheidungsvorlage gibt es als PDF.
6. **Prüfstand:** Ergebnisse werden mit echten Testfragen geprüft, Grenzen werden dokumentiert.
7. **90-Tage-Plan und Projekt-Board:** Jeder sieht, wo ein Vorhaben steht.
8. **KI-Führerschein:** Schulung mit Abschlusstest, Zertifikat und Auswertung für Trainer.
9. **KI-Radar und Protokoll:** neue Werkzeuge nüchtern bewertet; jede Entscheidung nachvollziehbar.
10. **SOP-Assistent mit GxP-Leitplanken:** ein Beispiel aus der Pharmaproduktion mit fiktiven SOPs. Der Assistent trifft keine GxP-Entscheidungen, ändert keine Aufzeichnungen, nutzt nur gültige SOP-Versionen und antwortet nur mit Quelle; jede Frage steht im Audit-Trail.

**Technik:** Python, Streamlit, OpenAI (gpt-4o-mini) mit regelbasiertem Offline-Modus, Pseudonymisierung vor jedem Modellaufruf,
Suche in der Wissensbasis per BM25, PDF-Export, automatisierte Tests. Oberfläche auf Deutsch und Englisch.

**Hinweise:** Alle Inhalte sind Beispieldaten aus der Logistikbranche. Eingaben bleiben in Ihrer Sitzung und werden nicht gespeichert.

Diese App wurde von Amrina entwickelt, mit KI als unterstützendem Werkzeug beim Programmieren.
"""

ABOUT_EN = """
**What the platform shows:** the whole work cycle of an AI Solutions Manager, from the first talk with a business unit to the rollout.

1. **Submit an idea:** The business unit describes a problem in its own words; the AI turns it into a brief. Personal data is removed first.
2. **Process mapping:** Work steps and times today and with AI; this gives the estimated time saving.
3. **Data protection, AI Act and IT check:** Risks and safeguards give a data protection light. The EU AI Act classification (prohibited, high risk, transparency, minimal) shows the obligations, and a GxP check covers regulated processes; Compliance confirms. IT checks interfaces, hosting, sign-in, operations and costs.
4. **Assessment:** Benefit, effort, feasibility and risk give points and a rank as a basis for discussion.
5. **Decision:** Management decides with a reason, only after data protection, Compliance and IT have approved; the decision paper is available as a PDF.
6. **Test bench:** Results are checked with real test questions, and limits are documented.
7. **90-day plan and project board:** Everyone can see where a project stands.
8. **AI licence:** Training with a final test, certificate and results for trainers.
9. **AI radar and log:** new tools assessed soberly; every decision traceable.
10. **SOP assistant with GxP guardrails:** an example from pharmaceutical production with fictional SOPs. The assistant makes no GxP decisions, changes no records, uses only effective SOP versions and answers only with a source; every question goes into the audit trail.

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
