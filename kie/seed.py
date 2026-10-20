"""Beispieldaten aus der Logistikbranche: Anwendungsfälle, KI-Radar und Kursstatistik."""

STATUSES = ["Idee", "Bewertung", "Entscheidung", "Prototyp", "Pilot", "Einführung", "Zurückgestellt"]


def _steps(*rows):
    return [{"schritt": s, "minuten": m, "ki": k, "minuten_mit_ki": mk} for s, m, k, mk in rows]


def usecases() -> list[dict]:
    return [
        {
            "id": "A", "titel": "Wissensassistent für interne Richtlinien", "fachbereich": "Kundenberatung",
            "status": "Pilot", "faelle_pro_monat": 900,
            "steckbrief": {
                "problem": "Antworten auf wiederkehrende Fragen zu Tarifen, Karten und Abläufen stecken in vielen Dokumenten. "
                           "Neue Mitarbeitende fragen Kolleginnen und Kollegen oder suchen lange.",
                "ziel": "Fragen in Sekunden mit Quellenangabe beantworten; ehrlich sagen, wenn die Unterlagen keine Antwort enthalten.",
                "nutzende": "Kundenberatung und Versicherung, im Pilot 8 Personen",
                "daten": "Freigegebene interne Dokumente (Richtlinien, Produktblätter, FAQ), keine Kundendaten",
                "schnittstellen": "Dokumentenablage (SharePoint), Anmeldung über das Firmenkonto",
                "erfolgskriterien": ["Mindestens 90 % richtige Antworten mit korrekter Quelle bei echten Testfragen",
                                     "Fragen ohne Antwort in den Unterlagen werden abgelehnt statt geraten",
                                     "Mindestens 70 % der Nutzenden sparen nach eigener Aussage Zeit"],
                "datenschutz_hinweise": ["Nur freigegebene Dokumente", "Personenbezogene Daten in Fragen werden vorab entfernt"],
                "offene_fragen": ["Wer pflegt die Dokumente?", "Wie oft ändern sich Tarife?"],
            },
            "prozess": _steps(("Frage verstehen und Stichworte überlegen", 1, False, 1), ("In Ordnern und Mails suchen", 6, True, 0.5),
                              ("Kollegin oder Kollegen fragen, falls nichts gefunden", 3, True, 0.5), ("Antwort formulieren", 2, False, 2)),
            "bewertung": {"nutzen": 5, "aufwand": 2, "umsetzbarkeit": 5, "risiko": 2},
            "datenschutz": {"antworten": {"personenbezogen": False, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": True, "pseudonymisierung": True, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Freigegeben für den Pilot mit EU-Hosting und AV-Vertrag."},
            "entscheidung": {"ergebnis": "Freigegeben", "begruendung": "Hoher Nutzen bei geringem Risiko; Pilot mit 8 Personen.",
                             "datum": "2026-09-22"},
            "tests": [
                {"frage": "Wie schnell kommt eine Ersatzkarte?", "erwartet": "Innerhalb von fünf Werktagen", "bewertung": "richtig"},
                {"frage": "Bis wann kann ich einen Kurs kostenlos stornieren?", "erwartet": "Bis zehn Tage vor Kursbeginn", "bewertung": "richtig"},
                {"frage": "Wie viele Stunden Weiterbildung braucht ein Berufskraftfahrer?", "erwartet": "35 Stunden alle fünf Jahre", "bewertung": "richtig"},
                {"frage": "Was kostet eine Ersatzkarte?", "erwartet": "Nicht in den Unterlagen, also ablehnen", "bewertung": "teilweise"},
            ],
            "grenzen": "Ersetzt keine versicherungsfachliche Prüfung. Preise für Ersatzkarten fehlen in den Unterlagen.",
        },
        {
            "id": "B", "titel": "Posteingang Schadensmeldungen", "fachbereich": "Versicherung",
            "status": "Bewertung", "faelle_pro_monat": 420,
            "steckbrief": {
                "problem": "Schadensmeldungen kommen per E-Mail und Formular. Daten wie Kennzeichen, Datum und Schadenart werden von Hand übertragen.",
                "ziel": "Meldungen automatisch erkennen, Daten auslesen und fehlende Unterlagen anfordern; Prüfung durch eine Person.",
                "nutzende": "Sachbearbeitung Kfz-Versicherung",
                "daten": "Meldungen mit Kennzeichen, Namen, Unfallhergang, teils Personenschäden",
                "schnittstellen": "E-Mail-Postfach, Bestandssystem der Versicherung",
                "erfolgskriterien": ["95 % der Pflichtfelder korrekt ausgelesen", "Bearbeitungszeit pro Meldung halbiert"],
                "datenschutz_hinweise": ["Gesundheitsdaten bei Personenschäden möglich", "Kennzeichen mit Personenbezug"],
                "offene_fragen": ["Darf ein externer Dienst genutzt werden?", "Wie viele Meldungen betreffen Personenschäden?"],
            },
            "prozess": _steps(("Meldung öffnen und Art erkennen", 2, True, 0.5), ("Daten ins Bestandssystem übertragen", 8, True, 2),
                              ("Vollständigkeit prüfen", 4, True, 1), ("Fehlende Unterlagen anfordern", 5, True, 1.5)),
            "bewertung": {"nutzen": 5, "aufwand": 3, "umsetzbarkeit": 4, "risiko": 4},
            "datenschutz": {"antworten": {"personenbezogen": True, "besondere": True, "extern": True, "automatisch": False,
                                          "speicherung": True, "pseudonymisierung": False, "pruefung": True, "rollen": True},
                            "freigabe": "offen", "kommentar": ""},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "C", "titel": "Antwortentwürfe zu Tank- und Servicekarten", "fachbereich": "Kundenservice",
            "status": "Entscheidung", "faelle_pro_monat": 650,
            "steckbrief": {
                "problem": "Viele E-Mails zu Sperrung, Abrechnung und Ersatzkarten werden einzeln beantwortet.",
                "ziel": "Antwortentwürfe aus den Richtlinien vorschlagen, die der Kundenservice prüft und versendet.",
                "nutzende": "Kundenservice", "daten": "Kundenanfragen, Richtlinien zu Karten",
                "schnittstellen": "E-Mail-System", "erfolgskriterien": ["80 % der Entwürfe ohne große Änderung nutzbar"],
                "datenschutz_hinweise": ["Kundendaten in Mails"], "offene_fragen": ["Welche Anfragen sind am häufigsten?"],
            },
            "prozess": _steps(("Anfrage lesen", 1, False, 1), ("Regel nachschlagen", 3, True, 0.5), ("Antwort schreiben", 4, True, 1.5)),
            "bewertung": {"nutzen": 4, "aufwand": 2, "umsetzbarkeit": 4, "risiko": 3},
            "datenschutz": {"antworten": {"personenbezogen": True, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": False, "pseudonymisierung": True, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Nur mit Pseudonymisierung und Prüfung vor Versand."},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "D", "titel": "Übungsfragen aus Schulungsunterlagen", "fachbereich": "Schulung",
            "status": "Prototyp", "faelle_pro_monat": 40,
            "steckbrief": {
                "problem": "Für die Weiterbildung von Berufskraftfahrern werden Übungsfragen und Zusammenfassungen von Hand erstellt.",
                "ziel": "Entwürfe für Übungsfragen aus vorhandenen Unterlagen erzeugen, die Dozentinnen und Dozenten freigeben.",
                "nutzende": "Dozentinnen und Dozenten", "daten": "Schulungsunterlagen ohne Personenbezug",
                "schnittstellen": "Lernplattform", "erfolgskriterien": ["Vorbereitungszeit pro Modul um 30 % gesenkt"],
                "datenschutz_hinweise": ["Kein Personenbezug"], "offene_fragen": ["Welche Module zuerst?"],
            },
            "prozess": _steps(("Unterlagen sichten", 30, False, 30), ("Fragen formulieren", 90, True, 25), ("Fragen prüfen", 20, False, 20)),
            "bewertung": {"nutzen": 3, "aufwand": 2, "umsetzbarkeit": 5, "risiko": 1},
            "datenschutz": {"antworten": {"personenbezogen": False, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": False, "pseudonymisierung": False, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Unkritisch."},
            "entscheidung": {"ergebnis": "Freigegeben", "begruendung": "Schneller Erfolg ohne personenbezogene Daten.", "datum": "2026-10-06"},
            "tests": [], "grenzen": "",
        },
        {
            "id": "E", "titel": "Besprechungsprotokolle aus Teams-Meetings", "fachbereich": "Alle Bereiche",
            "status": "Idee", "faelle_pro_monat": 120,
            "steckbrief": {
                "problem": "Protokolle und Aufgabenlisten werden nach Besprechungen von Hand geschrieben.",
                "ziel": "Zusammenfassung und Aufgaben automatisch vorschlagen.", "nutzende": "Teams aller Bereiche",
                "daten": "Besprechungsinhalte", "schnittstellen": "Microsoft Teams",
                "erfolgskriterien": ["Protokoll in unter 5 Minuten fertig"], "datenschutz_hinweise": ["Einwilligung der Teilnehmenden"],
                "offene_fragen": ["Reichen vorhandene Microsoft-365-Funktionen?"],
            },
            "prozess": _steps(("Notizen ordnen", 10, True, 2), ("Protokoll schreiben", 15, True, 3)),
            "bewertung": {"nutzen": 3, "aufwand": 1, "umsetzbarkeit": 4, "risiko": 3},
            "datenschutz": {"antworten": {}, "freigabe": "offen", "kommentar": ""},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "F", "titel": "Auffälligkeiten in Tankkarten-Transaktionen", "fachbereich": "Abrechnung",
            "status": "Zurückgestellt", "faelle_pro_monat": 0,
            "steckbrief": {
                "problem": "Ungewöhnliche Tankvorgänge (Ort, Menge, Uhrzeit) fallen oft erst spät auf.",
                "ziel": "Auffällige Transaktionen markieren.", "nutzende": "Abrechnung, Mitgliedsunternehmen",
                "daten": "Transaktionsdaten", "schnittstellen": "Abrechnungssystem",
                "erfolgskriterien": ["Weniger unentdeckte Missbrauchsfälle"], "datenschutz_hinweise": ["Bewegungsdaten von Fahrern"],
                "offene_fragen": ["Eher klassische Datenanalyse als Sprachmodell?"],
            },
            "prozess": [], "bewertung": {"nutzen": 4, "aufwand": 5, "umsetzbarkeit": 2, "risiko": 4},
            "datenschutz": {"antworten": {}, "freigabe": "offen", "kommentar": ""},
            "entscheidung": {"ergebnis": "Zurückgestellt", "begruendung": "Hoher Aufwand; als Datenanalyse-Projekt 2027 prüfen.",
                             "datum": "2026-09-22"},
            "tests": [], "grenzen": "",
        },
    ]


def log() -> list[dict]:
    return [
        {"datum": "2026-09-15", "rolle": "Fachbereich", "usecase": "A", "aktion": "Idee eingereicht", "details": "Kundenberatung"},
        {"datum": "2026-09-18", "rolle": "Datenschutz", "usecase": "A", "aktion": "Datenschutz freigegeben", "details": "EU-Hosting, AV-Vertrag"},
        {"datum": "2026-09-22", "rolle": "Geschäftsführung", "usecase": "A", "aktion": "Entscheidung: Freigegeben", "details": "Pilot mit 8 Personen"},
        {"datum": "2026-09-22", "rolle": "Geschäftsführung", "usecase": "F", "aktion": "Entscheidung: Zurückgestellt", "details": "Hoher Aufwand"},
        {"datum": "2026-10-06", "rolle": "Geschäftsführung", "usecase": "D", "aktion": "Entscheidung: Freigegeben", "details": "Schneller Erfolg"},
        {"datum": "2026-10-13", "rolle": "AI Manager", "usecase": "A", "aktion": "Pilot gestartet", "details": "Testfragen 3 von 4 richtig"},
    ]


def radar() -> list[dict]:
    return [
        {"name": "GPT-4o mini (OpenAI)", "kategorie": "Sprachmodell", "einsatz": "Wissensassistent, Entwürfe",
         "datenschutz": "Nur mit AV-Vertrag und EU-Datenverarbeitung", "einschaetzung": "Einsetzen", "geprueft": "2026-09"},
        {"name": "Microsoft 365 Copilot", "kategorie": "Bürosoftware", "einsatz": "Protokolle, Zusammenfassungen",
         "datenschutz": "Im eigenen Microsoft-365-Mandanten", "einschaetzung": "Testen", "geprueft": "2026-10"},
        {"name": "Mistral (EU-Anbieter)", "kategorie": "Sprachmodell", "einsatz": "Alternative mit Sitz in der EU",
         "datenschutz": "Verarbeitung in der EU möglich", "einschaetzung": "Testen", "geprueft": "2026-10"},
        {"name": "Ollama mit offenen Modellen", "kategorie": "Lokale Modelle", "einsatz": "Sensible Daten ohne externen Dienst",
         "datenschutz": "Daten bleiben im eigenen Netz", "einschaetzung": "Testen", "geprueft": "2026-08"},
        {"name": "n8n", "kategorie": "Automatisierung", "einsatz": "Abläufe zwischen E-Mail, Portal und KI verbinden",
         "datenschutz": "Selbst betreibbar", "einschaetzung": "Einsetzen", "geprueft": "2026-09"},
        {"name": "Bildgenerierung für Marketing", "kategorie": "Generative Bilder", "einsatz": "Grafiken für Social Media",
         "datenschutz": "Urheber- und Persönlichkeitsrechte unklar", "einschaetzung": "Beobachten", "geprueft": "2026-07"},
    ]


def course_stats() -> dict:
    """Beispielwerte für die Kursauswertung (Teilnehmende vor dieser Sitzung)."""
    return {"teilnehmende": 46, "bestanden": 39, "falsch_pro_frage": {"q1": 4, "q2": 17, "q3": 6, "q4": 11, "q5": 3},
            "feedback": [5, 4, 5, 4, 3, 5, 4, 4, 5, 5]}
