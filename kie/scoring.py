"""Bewertung, Zeitersparnis und Datenschutz-Ampel: reine Funktionen, damit sie testbar und nachvollziehbar sind."""
from dataclasses import dataclass

CRITERIA = ["nutzen", "aufwand", "umsetzbarkeit", "risiko"]

# Datenschutz-Check: (Schlüssel, Frage DE, Frage EN, Gewicht, Hinweis DE, Hinweis EN)
DS_QUESTIONS = [
    ("personenbezogen", "Werden personenbezogene Daten verarbeitet (Namen, Kontaktdaten, Kennzeichen mit Personenbezug)?",
     "Is personal data processed (names, contact details, licence plates linked to people)?", 2,
     "Pseudonymisierung vor dem Modellaufruf einplanen.", "Plan pseudonymisation before the model call."),
    ("besondere", "Sind besondere Kategorien betroffen (z. B. Gesundheitsdaten nach Art. 9 DSGVO)?",
     "Are special categories involved (e.g. health data under Art. 9 GDPR)?", 3,
     "Nur mit Datenschutz-Folgenabschätzung und ausdrücklicher Freigabe.", "Only with a data protection impact assessment and explicit approval."),
    ("extern", "Werden Daten an einen externen KI-Dienst übertragen?", "Is data sent to an external AI service?", 2,
     "Auftragsverarbeitungsvertrag und Hosting in der EU prüfen, sonst lokales Modell.",
     "Check the data processing agreement and EU hosting; otherwise use a local model."),
    ("automatisch", "Trifft die Anwendung Entscheidungen ohne Prüfung durch eine Person?",
     "Does the application make decisions without a person checking them?", 3,
     "Menschliche Prüfung vor jeder Entscheidung mit Außenwirkung vorsehen.", "Add a human check before every decision with external impact."),
    ("speicherung", "Werden Eingaben oder Ergebnisse dauerhaft gespeichert?", "Are inputs or results stored permanently?", 1,
     "Löschfristen festlegen und Protokolle ohne Inhalte führen.", "Define deletion periods and keep logs without content."),
]
# Schutzmaßnahmen, die das Risiko senken (Antwort "Ja" ist hier gut): (Schlüssel, DE, EN, Gewicht)
DS_MEASURES = [
    ("pseudonymisierung", "Personenbezogene Daten werden vor dem Modellaufruf entfernt oder ersetzt.",
     "Personal data is removed or replaced before the model call.", 2),
    ("pruefung", "Jedes Ergebnis mit Außenwirkung wird von einer Person geprüft.", "A person checks every result with external impact.", 2),
    ("rollen", "Zugriff ist über Rollen und Rechte geregelt.", "Access is controlled by roles and rights.", 1),
]


def score(b: dict) -> int:
    """Punkte = Nutzen + Umsetzbarkeit − Aufwand − Datenschutzrisiko (jeweils 1 bis 5)."""
    return b["nutzen"] + b["umsetzbarkeit"] - b["aufwand"] - b["risiko"]


def ranking(usecases: list[dict]) -> dict[str, int]:
    """Gleiche Punktzahl ergibt den gleichen Rang."""
    points = {u["id"]: score(u["bewertung"]) for u in usecases}
    return {uid: 1 + sum(1 for p in points.values() if p > pts) for uid, pts in points.items()}


@dataclass
class Saving:
    minutes_before: float
    minutes_after: float
    hours_per_month: float


def time_saving(steps: list[dict], cases_per_month: int) -> Saving:
    before = sum(float(s.get("minuten") or 0) for s in steps)
    after = sum(float(s.get("minuten_mit_ki") if s.get("ki") else s.get("minuten") or 0) for s in steps)
    return Saving(before, after, round((before - after) * cases_per_month / 60, 1))


def ampel(answers: dict, lang: str = "de") -> tuple[str, int, list[str]]:
    """Gibt (offen|gruen|gelb|rot, Risikopunkte, offene Hinweise) zurück."""
    if not answers:
        return "offen", 0, ["Datenschutz-Check noch nicht ausgefüllt." if lang == "de" else "Data protection check not completed yet."]
    risk = sum(q[3] for q in DS_QUESTIONS if answers.get(q[0]))
    risk -= sum(m[3] for m in DS_MEASURES if answers.get(m[0]))
    hints = [q[4] if lang == "de" else q[5] for q in DS_QUESTIONS if answers.get(q[0])]
    if answers.get("besondere") and not answers.get("pseudonymisierung"):
        return "rot", max(risk, 0), hints
    level = "gruen" if risk <= 1 else "gelb" if risk <= 4 else "rot"
    if level == "gruen" and answers.get("personenbezogen") and answers.get("extern"):
        level = "gelb"  # personenbezogene Daten bei einem externen Dienst nie ohne Auflagen
    return level, max(risk, 0), hints


AMPEL_LABEL = {
    "de": {"offen": "⚪ Offen: Check ausstehend", "gruen": "🟢 Grün: unkritisch", "gelb": "🟡 Gelb: mit Auflagen", "rot": "🔴 Rot: nicht ohne Freigabe"},
    "en": {"offen": "⚪ Open: check pending", "gruen": "🟢 Green: not critical", "gelb": "🟡 Amber: with conditions", "rot": "🔴 Red: not without approval"},
}

# IT-Check: technische Bereitschaft (Antwort "Ja" ist gut): (Schlüssel, DE, EN, Hinweis DE, Hinweis EN)
IT_CHECKS = [
    ("schnittstelle", "Die nötigen Systeme sind über eine Schnittstelle (API) erreichbar.",
     "The required systems can be reached through an interface (API).",
     "Schnittstelle mit dem Anbieter klären oder einen manuellen Zwischenschritt einplanen.",
     "Clarify the interface with the vendor or plan a manual step in between."),
    ("hosting", "Das Hosting ist geklärt (Cloud in der EU oder eigener Server).",
     "Hosting is settled (cloud in the EU or own server).",
     "Hosting festlegen; bei sensiblen Daten ein lokales Modell prüfen.", "Decide on hosting; for sensitive data consider a local model."),
    ("anmeldung", "Die Anmeldung läuft über das Firmenkonto (z. B. Microsoft Entra ID).",
     "Sign-in uses the company account (e.g. Microsoft Entra ID).",
     "Anbindung an die Firmenanmeldung einplanen, keine eigenen Passwörter.", "Plan the link to the company sign-in, no separate passwords."),
    ("betrieb", "Der Betrieb ist geregelt: Monitoring, Backups und eine Ansprechperson bei Störungen.",
     "Operations are covered: monitoring, backups and a contact person for incidents.",
     "Zuständigkeit für Betrieb und Störungen festlegen, bevor es live geht.", "Assign who runs it and handles incidents before go-live."),
    ("kosten", "Die laufenden Kosten (Modellnutzung, Hosting) sind geschätzt und im Budget.",
     "Running costs (model usage, hosting) are estimated and within budget.",
     "Kosten pro Monat schätzen und mit dem Budget abgleichen.", "Estimate monthly costs and check them against the budget."),
]


def it_status(answers: dict, lang: str = "de") -> tuple[str, int, list[str]]:
    """Gibt (offen|gruen|gelb|rot, erfüllte Punkte, offene Hinweise) zurück."""
    if not answers:
        return "offen", 0, ["IT-Check noch nicht ausgefüllt." if lang == "de" else "IT check not completed yet."]
    done = sum(1 for c in IT_CHECKS if answers.get(c[0]))
    hints = [c[3] if lang == "de" else c[4] for c in IT_CHECKS if not answers.get(c[0])]
    level = "gruen" if done == len(IT_CHECKS) else "gelb" if done >= 3 else "rot"
    return level, done, hints


IT_LABEL = {
    "de": {"offen": "⚪ Offen: Check ausstehend", "gruen": "🟢 Bereit für den Betrieb", "gelb": "🟡 Teilweise bereit", "rot": "🔴 Noch nicht bereit"},
    "en": {"offen": "⚪ Open: check pending", "gruen": "🟢 Ready for operation", "gelb": "🟡 Partly ready", "rot": "🔴 Not ready yet"},
}
