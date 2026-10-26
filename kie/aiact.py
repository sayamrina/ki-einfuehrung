"""EU-AI-Act-Einstufung und GxP-Hinweise: reine Funktionen, damit die Logik testbar und nachvollziehbar ist.

Die Einstufung folgt dem Aufbau der Verordnung (EU) 2024/1689: zuerst verbotene Praktiken (Art. 5), dann
Hochrisiko (Art. 6 mit Anhang I und III), dann Transparenzpflichten (Art. 50), sonst minimales Risiko.
Sie ist eine Orientierung für das Gespräch mit Compliance und Recht, keine Rechtsberatung.
"""

# (Schlüssel, Frage DE, Frage EN, Fundstelle)
PROHIBITED = [
    ("manipulation",
     "Beeinflusst das System Menschen unterschwellig oder nutzt es Schwächen (Alter, Behinderung, Notlage) aus, "
     "sodass ihnen Schaden droht?",
     "Does the system influence people subliminally or exploit vulnerabilities (age, disability, hardship) "
     "in a way that may harm them?",
     "Art. 5 (1) a, b"),
    ("social_scoring",
     "Bewertet es Menschen nach ihrem Sozialverhalten oder ihrer Persönlichkeit, mit Nachteilen in anderen "
     "Zusammenhängen (Social Scoring)?",
     "Does it rate people by social behaviour or personality, with disadvantages in unrelated contexts (social scoring)?",
     "Art. 5 (1) c"),
    ("emotion_work",
     "Erkennt es Emotionen von Beschäftigten oder Lernenden am Arbeitsplatz oder in der Bildung "
     "(außer aus medizinischen oder Sicherheitsgründen)?",
     "Does it recognise emotions of employees or learners at work or in education "
     "(other than for medical or safety reasons)?",
     "Art. 5 (1) f"),
    ("biometric_sensitive",
     "Ordnet es Menschen anhand biometrischer Daten sensiblen Merkmalen zu (z. B. Religion, politische Meinung, "
     "sexuelle Orientierung) oder baut es Gesichtsdatenbanken durch ungezieltes Auslesen auf?",
     "Does it infer sensitive traits (e.g. religion, political opinion, sexual orientation) from biometric data, "
     "or build face databases by untargeted scraping?",
     "Art. 5 (1) e, g"),
]
HIGH_RISK = [
    ("hr",
     "Beschäftigung und Personal: Auswahl von Bewerbungen, Entscheidungen über Beförderung oder Kündigung, "
     "Aufgabenzuteilung nach Verhalten, Leistungsüberwachung",
     "Employment and HR: screening applications, decisions on promotion or termination, "
     "task allocation based on behaviour, performance monitoring",
     "Anhang III Nr. 4"),
    ("education",
     "Bildung: Zulassung, Bewertung von Lernergebnissen, Einstufung oder Prüfungsaufsicht",
     "Education: admission, evaluation of learning outcomes, placement or exam proctoring",
     "Anhang III Nr. 3"),
    ("essential",
     "Zugang zu wesentlichen Leistungen: Kreditwürdigkeit, Risiko und Preise bei Lebens- und Krankenversicherung, "
     "öffentliche Leistungen",
     "Access to essential services: creditworthiness, risk and pricing in life and health insurance, public benefits",
     "Anhang III Nr. 5"),
    ("infrastructure",
     "Sicherheitsbauteil kritischer Infrastruktur (z. B. Strom, Wasser, Gas, Straßenverkehr)",
     "Safety component of critical infrastructure (e.g. electricity, water, gas, road traffic)",
     "Anhang III Nr. 2"),
    ("biometric_id",
     "Biometrische Fernidentifizierung oder Kategorisierung von Personen",
     "Remote biometric identification or categorisation of people",
     "Anhang III Nr. 1"),
    ("product_safety",
     "Sicherheitsbauteil eines Produkts mit Konformitätsbewertung durch Dritte, z. B. Medizinprodukt (MDR) oder Maschine",
     "Safety component of a product that needs third-party conformity assessment, e.g. a medical device (MDR) or machinery",
     "Art. 6 (1), Anhang I"),
]
# Ausnahme nach Art. 6 (3): nur für Anhang-III-Fälle und nie bei Profiling natürlicher Personen
EXCEPTION = ("narrow_task",
             "Das System erledigt nur eine eng begrenzte vorbereitende oder verfahrensbezogene Aufgabe "
             "und beeinflusst das Ergebnis der Entscheidung nicht wesentlich.",
             "The system only performs a narrow preparatory or procedural task "
             "and does not materially influence the outcome of the decision.",
             "Art. 6 (3)")
PROFILING = ("profiling",
             "Werden dabei Profile natürlicher Personen erstellt (Bewertung von Leistung, Verhalten, Zuverlässigkeit)?",
             "Does it profile natural persons (evaluating performance, behaviour, reliability)?",
             "Art. 6 (3)")
TRANSPARENCY = [
    ("chatbot",
     "Interagiert das System direkt mit Menschen (z. B. Chat oder Sprachassistent)?",
     "Does the system interact directly with people (e.g. chat or voice assistant)?",
     "Art. 50 (1)"),
    ("synthetic",
     "Erzeugt es Texte, Bilder, Audio oder Video, die veröffentlicht oder nach außen gegeben werden?",
     "Does it generate text, images, audio or video that is published or shared externally?",
     "Art. 50 (2), (4)"),
    ("emotion_other",
     "Erkennt es Emotionen oder kategorisiert es Personen biometrisch in einem erlaubten Zusammenhang?",
     "Does it recognise emotions or categorise people biometrically in a permitted context?",
     "Art. 50 (3)"),
]
# GxP-Check: (Schlüssel, Frage DE, Frage EN)
GXP = [
    ("gxp_process",
     "Unterstützt das System einen GxP-relevanten Prozess (z. B. Chargenfreigabe, Abweichungen, CAPA, "
     "Qualitätsdokumente, Zulassungsunterlagen)?",
     "Does the system support a GxP-relevant process (e.g. batch release, deviations, CAPA, quality records, "
     "regulatory submissions)?"),
    ("gxp_records",
     "Erzeugt oder verändert es Daten, die als GxP-Aufzeichnung gelten?",
     "Does it create or change data that counts as a GxP record?"),
]

LABEL = {
    "de": {"offen": "⚪ Offen: Einstufung ausstehend", "verboten": "⛔ Verbotene Praxis", "hoch": "🔴 Hochrisiko",
           "begrenzt": "🟡 Begrenztes Risiko: Transparenzpflichten", "minimal": "🟢 Minimales Risiko"},
    "en": {"offen": "⚪ Open: classification pending", "verboten": "⛔ Prohibited practice", "hoch": "🔴 High risk",
           "begrenzt": "🟡 Limited risk: transparency obligations", "minimal": "🟢 Minimal risk"},
}
# Pflichten je Stufe aus Sicht des Unternehmens als Betreiber (deployer): (DE, EN)
DUTIES = {
    "verboten": [
        ("Nicht umsetzen. Der Einsatz ist in der EU seit 2. Februar 2025 untersagt.",
         "Do not implement. This use has been banned in the EU since 2 February 2025."),
    ],
    "hoch": [
        ("Nach der Gebrauchsanweisung des Anbieters einsetzen und den Betrieb überwachen (Art. 26).",
         "Use it according to the provider's instructions and monitor operation (Art. 26)."),
        ("Menschliche Aufsicht durch geschulte Personen mit Befugnis zum Eingreifen festlegen (Art. 14, 26).",
         "Assign human oversight to trained people with the authority to intervene (Art. 14, 26)."),
        ("Eingabedaten auf Relevanz prüfen und automatisch erzeugte Protokolle mindestens sechs Monate aufbewahren (Art. 26).",
         "Check input data for relevance and keep automatically generated logs for at least six months (Art. 26)."),
        ("Betroffene Beschäftigte und ihre Vertretung vor dem Einsatz informieren (Art. 26 (7)).",
         "Inform affected employees and their representatives before use (Art. 26 (7))."),
        ("Beim Anbieter CE-Kennzeichnung, Registrierung und technische Dokumentation nachweisen lassen.",
         "Ask the provider for proof of CE marking, registration and technical documentation."),
    ],
    "begrenzt": [
        ("Menschen klar darüber informieren, dass sie mit einer KI interagieren (Art. 50 (1)).",
         "Tell people clearly that they are interacting with an AI (Art. 50 (1))."),
        ("KI-erzeugte Inhalte, die veröffentlicht werden, als solche kennzeichnen (Art. 50 (2), (4)).",
         "Label AI-generated content that is published as such (Art. 50 (2), (4))."),
    ],
    "minimal": [
        ("Keine besonderen Pflichten aus dem AI Act; freiwillige Verhaltensregeln und interne Richtlinie anwenden.",
         "No specific AI Act obligations; apply voluntary codes of conduct and the internal policy."),
    ],
}
LITERACY = ("Für alle Stufen gilt seit 2. Februar 2025 die Pflicht zur KI-Kompetenz der Beschäftigten (Art. 4), "
            "z. B. über den KI-Führerschein.",
            "For every class, the duty to ensure employees' AI literacy (Art. 4) has applied since 2 February 2025, "
            "e.g. through the AI licence.")
GXP_HINTS = [
    ("Als computergestütztes System validieren (EU-GMP-Leitfaden Anhang 11, risikobasiert nach GAMP 5).",
     "Validate it as a computerised system (EU GMP Annex 11, risk-based in line with GAMP 5)."),
    ("Datenintegrität nach ALCOA+ sicherstellen: Audit-Trail, Zugriffsrechte, keine unkontrollierten Änderungen.",
     "Ensure data integrity under ALCOA+: audit trail, access rights, no uncontrolled changes."),
    ("Eine qualifizierte Person prüft jedes Ergebnis mit GxP-Wirkung; das Modell entscheidet nicht allein.",
     "A qualified person reviews every result with GxP impact; the model never decides on its own."),
    ("Den Entwurf des neuen GMP-Anhangs 22 zu KI beobachten und die Qualitätssicherung früh einbinden.",
     "Follow the draft of the new GMP Annex 22 on AI and involve Quality Assurance early."),
]


def classify(answers: dict) -> tuple[str, list[str]]:
    """Gibt (Stufe, Fundstellen der Gründe) zurück. Stufen: offen, verboten, hoch, begrenzt, minimal."""
    if not answers:
        return "offen", []
    prohibited = [q[3] for q in PROHIBITED if answers.get(q[0])]
    if prohibited:
        return "verboten", prohibited
    annex_iii = [q[3] for q in HIGH_RISK if answers.get(q[0]) and q[0] != "product_safety"]
    if answers.get("product_safety"):
        return "hoch", [HIGH_RISK[-1][3]] + annex_iii
    reasons = []
    if annex_iii:
        if not answers.get(EXCEPTION[0]) or answers.get(PROFILING[0]):
            return "hoch", annex_iii
        reasons = [EXCEPTION[3]]  # Ausnahme dokumentieren; Transparenzpflichten können trotzdem gelten
    transparency = [q[3] for q in TRANSPARENCY if answers.get(q[0])]
    if transparency:
        return "begrenzt", reasons + transparency
    return "minimal", reasons


def ref(text: str, lang: str = "de") -> str:
    """Fundstellen sind auf Deutsch hinterlegt; auf Englisch heißt Anhang „Annex“."""
    return text.replace("Anhang", "Annex") if lang == "en" else text


def duties(level: str, lang: str = "de") -> list[str]:
    if level == "offen":
        return []
    i = 1 if lang == "en" else 0
    return [d[i] for d in DUTIES[level]] + [LITERACY[i]]


def gxp_relevant(answers: dict) -> bool:
    return any(answers.get(q[0]) for q in GXP)


def gxp_hints(answers: dict, lang: str = "de") -> list[str]:
    i = 1 if lang == "en" else 0
    return [h[i] for h in GXP_HINTS] if gxp_relevant(answers) else []
