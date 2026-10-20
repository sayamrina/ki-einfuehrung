"""Lernbereich „KI-Führerschein: Sicher arbeiten mit KI“: Module, Szenarien und Abschlusstest (Deutsch und Englisch)."""

MODULES_DE = [
    {
        "titel": "1. Was KI kann und was nicht",
        "dauer": "10 Min.",
        "inhalt": [
            "Ein Sprachmodell schreibt wahrscheinliche Texte. Es kennt Ihre internen Regeln nur, wenn sie ihm als Dokumente gegeben werden.",
            "Unser Wissensassistent antwortet nur aus freigegebenen Unterlagen und nennt immer die Quelle.",
            "KI kann sich irren und dabei sehr überzeugend klingen. Deshalb gilt: Ergebnisse sind Entwürfe.",
        ],
    },
    {
        "titel": "2. Welche Daten gehören nicht in die KI?",
        "dauer": "15 Min.",
        "inhalt": [
            "Namen, Adressen, Kennzeichen mit Personenbezug, Bankdaten und Gesundheitsdaten nur in freigegebene Anwendungen eingeben.",
            "Private Konten bei KI-Diensten sind für Firmendaten tabu.",
            "Im Zweifel: Daten weglassen oder ersetzen (z. B. „Kunde A“ statt Name) und das Datenschutz-Team fragen.",
        ],
    },
    {
        "titel": "3. Ergebnisse prüfen",
        "dauer": "15 Min.",
        "inhalt": [
            "Quelle öffnen: Steht die Antwort wirklich dort?",
            "Zahlen, Fristen und Namen immer gegenprüfen.",
            "Vor dem Versand an Kunden, Mitglieder oder Behörden prüft immer eine Person.",
        ],
    },
    {
        "titel": "4. Fehler melden und mitgestalten",
        "dauer": "5 Min.",
        "inhalt": [
            "Falsche oder unklare Antworten mit einem Klick melden: Daraus werden neue Testfälle.",
            "Ideen für neue Anwendungen über den Bereich „Idee einreichen“ eingeben.",
        ],
    },
]

# Szenarien mit Rückmeldung (zum Üben, ohne Wertung)
SCENARIOS_DE = [
    {"frage": "Ein Mitglied schickt eine Schadensmeldung mit Name, Kennzeichen und Verletzungen. Darf ich den Text in einen frei verfügbaren KI-Chat kopieren, um ihn zusammenzufassen?",
     "optionen": ["Ja, wenn es schneller geht", "Nein, nur in eine freigegebene Anwendung mit Pseudonymisierung"],
     "richtig": 1, "erklaerung": "Gesundheitsdaten und Kennzeichen mit Personenbezug gehören nur in freigegebene Anwendungen."},
    {"frage": "Der Assistent nennt eine Stornofrist von zehn Tagen und verweist auf das Dokument „Weiterbildung“. Was tun Sie vor der Antwort an den Kunden?",
     "optionen": ["Antwort direkt weitergeben", "Quelle kurz öffnen und die Frist prüfen"],
     "richtig": 1, "erklaerung": "Fristen und Zahlen immer an der Quelle prüfen; das dauert Sekunden."},
]

# Abschlusstest: Schlüssel q1 bis q5 passen zur Kursauswertung
QUIZ_DE = [
    {"id": "q1", "frage": "Was ist ein KI-Ergebnis in unserem Unternehmen?",
     "optionen": ["Eine geprüfte Auskunft", "Ein Entwurf, den eine Person prüft", "Eine verbindliche Entscheidung"], "richtig": 1},
    {"id": "q2", "frage": "Welche Angabe dürfen Sie ohne freigegebene Anwendung NICHT eingeben?",
     "optionen": ["Die Frage „Wie sperre ich eine Tankkarte?“", "Ein Kennzeichen zusammen mit dem Namen des Fahrers", "Den Titel einer Richtlinie"], "richtig": 1},
    {"id": "q3", "frage": "Der Assistent sagt: „Dazu enthalten die Unterlagen keine Antwort.“ Was bedeutet das?",
     "optionen": ["Er ist defekt", "Er rät nicht, sondern sagt ehrlich, dass Informationen fehlen", "Man soll die Frage so lange umformulieren, bis er antwortet"], "richtig": 1},
    {"id": "q4", "frage": "Wo prüfen Sie eine Antwort am schnellsten?",
     "optionen": ["In der angegebenen Quelle", "Bei einem zweiten KI-Dienst", "Gar nicht, die KI ist zuverlässig"], "richtig": 0},
    {"id": "q5", "frage": "Was machen Sie mit einer falschen Antwort?",
     "optionen": ["Ignorieren", "Über „Fehler melden“ weitergeben", "Den Assistenten nicht mehr nutzen"], "richtig": 1},
]
MODULES_EN = [
    {"titel": "1. What AI can and cannot do", "dauer": "10 min",
     "inhalt": ["A language model writes likely texts. It only knows your internal rules if they are given to it as documents.",
                "Our knowledge assistant answers only from approved documents and always names the source.",
                "AI can be wrong while sounding very convincing. That is why results are drafts."]},
    {"titel": "2. Which data does not belong in AI?", "dauer": "15 min",
     "inhalt": ["Enter names, addresses, licence plates linked to people, bank details and health data only in approved applications.",
                "Private accounts with AI services are off limits for company data.",
                "If in doubt: leave data out or replace it (e.g. \"Customer A\" instead of a name) and ask the data protection team."]},
    {"titel": "3. Checking results", "dauer": "15 min",
     "inhalt": ["Open the source: is the answer really there?", "Always double-check numbers, deadlines and names.",
                "A person always checks before anything is sent to customers, members or authorities."]},
    {"titel": "4. Report errors and help shape the tools", "dauer": "5 min",
     "inhalt": ["Report wrong or unclear answers with one click: they become new test cases.",
                "Submit ideas for new applications under \"Submit an idea\"."]},
]

SCENARIOS_EN = [
    {"frage": "A member sends a damage report with name, licence plate and injuries. May I paste the text into a freely available AI chat to summarise it?",
     "optionen": ["Yes, if it is faster", "No, only into an approved application with pseudonymisation"], "richtig": 1,
     "erklaerung": "Health data and licence plates linked to people belong only in approved applications."},
    {"frage": "The assistant states a cancellation period of ten days and refers to the document \"Training\". What do you do before replying to the customer?",
     "optionen": ["Pass the answer on directly", "Open the source briefly and check the period"], "richtig": 1,
     "erklaerung": "Always check deadlines and numbers in the source; it takes seconds."},
]

QUIZ_EN = [
    {"id": "q1", "frage": "What is an AI result in our company?",
     "optionen": ["A verified statement", "A draft that a person checks", "A binding decision"], "richtig": 1},
    {"id": "q2", "frage": "Which information may you NOT enter without an approved application?",
     "optionen": ["The question \"How do I block a fuel card?\"", "A licence plate together with the driver's name", "The title of a policy"], "richtig": 1},
    {"id": "q3", "frage": "The assistant says: \"The documents contain no answer to this.\" What does that mean?",
     "optionen": ["It is broken", "It does not guess but says honestly that information is missing", "You should rephrase until it answers"], "richtig": 1},
    {"id": "q4", "frage": "Where can you check an answer fastest?",
     "optionen": ["In the cited source", "With a second AI service", "Not at all, the AI is reliable"], "richtig": 0},
    {"id": "q5", "frage": "What do you do with a wrong answer?",
     "optionen": ["Ignore it", "Report it via \"Report error\"", "Stop using the assistant"], "richtig": 1},
]

PASS_MARK = 0.8


def content(lang: str) -> tuple[list, list, list]:
    return (MODULES_DE, SCENARIOS_DE, QUIZ_DE) if lang == "de" else (MODULES_EN, SCENARIOS_EN, QUIZ_EN)
