"""Sample data from the logistics sector (English version, same numbers as the German seed)."""
from .seed import _steps


def usecases() -> list[dict]:
    return [
        {
            "id": "A", "titel": "Knowledge assistant for internal policies", "fachbereich": "Customer advice",
            "status": "Pilot", "faelle_pro_monat": 900,
            "steckbrief": {
                "problem": "Answers to recurring questions about tariffs, cards and procedures are spread across many documents. "
                           "New employees ask colleagues or search for a long time.",
                "ziel": "Answer questions in seconds with the source; say honestly when the documents contain no answer.",
                "nutzende": "Customer advice and insurance, 8 people in the pilot",
                "daten": "Approved internal documents (policies, product sheets, FAQ), no customer data",
                "schnittstellen": "Document storage (SharePoint), sign-in with the company account",
                "erfolgskriterien": ["At least 90 % correct answers with the correct source on real test questions",
                                     "Questions without an answer in the documents are refused instead of guessed",
                                     "At least 70 % of users say they save time"],
                "datenschutz_hinweise": ["Approved documents only", "Personal data in questions is removed first"],
                "offene_fragen": ["Who maintains the documents?", "How often do tariffs change?"],
            },
            "prozess": _steps(("Understand the question and think of keywords", 1, False, 1), ("Search folders and e-mails", 6, True, 0.5),
                              ("Ask a colleague if nothing is found", 3, True, 0.5), ("Write the answer", 2, False, 2)),
            "bewertung": {"nutzen": 5, "aufwand": 2, "umsetzbarkeit": 5, "risiko": 2},
            "datenschutz": {"antworten": {"personenbezogen": False, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": True, "pseudonymisierung": True, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Approved for the pilot with EU hosting and a data processing agreement."},
            "entscheidung": {"ergebnis": "Freigegeben", "begruendung": "High benefit, low risk; pilot with 8 people.", "datum": "2026-09-22"},
            "tests": [
                {"frage": "How fast does a replacement card arrive?", "erwartet": "Within five working days", "bewertung": "richtig"},
                {"frage": "Until when can I cancel a course free of charge?", "erwartet": "Up to ten days before the course starts", "bewertung": "richtig"},
                {"frage": "How many hours of training does a professional driver need?", "erwartet": "35 hours every five years", "bewertung": "richtig"},
                {"frage": "How much does a replacement card cost?", "erwartet": "Not in the documents, so refuse", "bewertung": "teilweise"},
            ],
            "grenzen": "Does not replace an insurance review. Prices for replacement cards are missing from the documents.",
        },
        {
            "id": "B", "titel": "Inbox for damage reports", "fachbereich": "Insurance",
            "status": "Bewertung", "faelle_pro_monat": 420,
            "steckbrief": {
                "problem": "Damage reports arrive by e-mail and form. Data such as licence plate, date and type of damage is copied by hand.",
                "ziel": "Recognise reports automatically, extract data and request missing documents; a person checks every case.",
                "nutzende": "Motor insurance case handlers",
                "daten": "Reports with licence plates, names, accident details, sometimes injuries",
                "schnittstellen": "E-mail inbox, insurance policy system",
                "erfolgskriterien": ["95 % of mandatory fields extracted correctly", "Handling time per report halved"],
                "datenschutz_hinweise": ["Health data possible in injury cases", "Licence plates linked to people"],
                "offene_fragen": ["May an external service be used?", "How many reports involve injuries?"],
            },
            "prozess": _steps(("Open the report and identify its type", 2, True, 0.5), ("Copy data into the policy system", 8, True, 2),
                              ("Check completeness", 4, True, 1), ("Request missing documents", 5, True, 1.5)),
            "bewertung": {"nutzen": 5, "aufwand": 3, "umsetzbarkeit": 4, "risiko": 4},
            "datenschutz": {"antworten": {"personenbezogen": True, "besondere": True, "extern": True, "automatisch": False,
                                          "speicherung": True, "pseudonymisierung": False, "pruefung": True, "rollen": True},
                            "freigabe": "offen", "kommentar": ""},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "C", "titel": "Reply drafts for fuel and service cards", "fachbereich": "Customer service",
            "status": "Entscheidung", "faelle_pro_monat": 650,
            "steckbrief": {
                "problem": "Many e-mails about blocking, billing and replacement cards are answered one by one.",
                "ziel": "Suggest reply drafts based on the policies; customer service checks and sends them.",
                "nutzende": "Customer service", "daten": "Customer requests, card policies",
                "schnittstellen": "E-mail system", "erfolgskriterien": ["80 % of drafts usable without major edits"],
                "datenschutz_hinweise": ["Customer data in e-mails"], "offene_fragen": ["Which requests are most frequent?"],
            },
            "prozess": _steps(("Read the request", 1, False, 1), ("Look up the rule", 3, True, 0.5), ("Write the reply", 4, True, 1.5)),
            "bewertung": {"nutzen": 4, "aufwand": 2, "umsetzbarkeit": 4, "risiko": 3},
            "datenschutz": {"antworten": {"personenbezogen": True, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": False, "pseudonymisierung": True, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Only with pseudonymisation and a check before sending."},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "D", "titel": "Practice questions from training materials", "fachbereich": "Training",
            "status": "Prototyp", "faelle_pro_monat": 40,
            "steckbrief": {
                "problem": "Practice questions and summaries for professional driver training are written by hand.",
                "ziel": "Generate draft practice questions from existing materials, approved by trainers.",
                "nutzende": "Trainers", "daten": "Training materials without personal data",
                "schnittstellen": "Learning platform", "erfolgskriterien": ["Preparation time per module reduced by 30 %"],
                "datenschutz_hinweise": ["No personal data"], "offene_fragen": ["Which modules first?"],
            },
            "prozess": _steps(("Review materials", 30, False, 30), ("Write questions", 90, True, 25), ("Check questions", 20, False, 20)),
            "bewertung": {"nutzen": 3, "aufwand": 2, "umsetzbarkeit": 5, "risiko": 1},
            "datenschutz": {"antworten": {"personenbezogen": False, "besondere": False, "extern": True, "automatisch": False,
                                          "speicherung": False, "pseudonymisierung": False, "pruefung": True, "rollen": True},
                            "freigabe": "freigegeben", "kommentar": "Not critical."},
            "entscheidung": {"ergebnis": "Freigegeben", "begruendung": "Quick win without personal data.", "datum": "2026-10-06"},
            "tests": [], "grenzen": "",
        },
        {
            "id": "E", "titel": "Meeting minutes from Teams meetings", "fachbereich": "All departments",
            "status": "Idee", "faelle_pro_monat": 120,
            "steckbrief": {
                "problem": "Minutes and task lists are written by hand after meetings.",
                "ziel": "Suggest a summary and tasks automatically.", "nutzende": "Teams in all departments",
                "daten": "Meeting content", "schnittstellen": "Microsoft Teams",
                "erfolgskriterien": ["Minutes ready in under 5 minutes"], "datenschutz_hinweise": ["Consent of participants"],
                "offene_fragen": ["Are existing Microsoft 365 features enough?"],
            },
            "prozess": _steps(("Sort notes", 10, True, 2), ("Write minutes", 15, True, 3)),
            "bewertung": {"nutzen": 3, "aufwand": 1, "umsetzbarkeit": 4, "risiko": 3},
            "datenschutz": {"antworten": {}, "freigabe": "offen", "kommentar": ""},
            "entscheidung": {}, "tests": [], "grenzen": "",
        },
        {
            "id": "F", "titel": "Anomalies in fuel card transactions", "fachbereich": "Billing",
            "status": "Zurückgestellt", "faelle_pro_monat": 0,
            "steckbrief": {
                "problem": "Unusual refuelling (place, volume, time) is often noticed late.",
                "ziel": "Flag suspicious transactions.", "nutzende": "Billing, member companies",
                "daten": "Transaction data", "schnittstellen": "Billing system",
                "erfolgskriterien": ["Fewer undetected misuse cases"], "datenschutz_hinweise": ["Movement data of drivers"],
                "offene_fragen": ["Rather classic data analysis than a language model?"],
            },
            "prozess": [], "bewertung": {"nutzen": 4, "aufwand": 5, "umsetzbarkeit": 2, "risiko": 4},
            "datenschutz": {"antworten": {}, "freigabe": "offen", "kommentar": ""},
            "entscheidung": {"ergebnis": "Zurückgestellt", "begruendung": "High effort; review as a data analysis project in 2027.",
                             "datum": "2026-09-22"},
            "tests": [], "grenzen": "",
        },
    ]


def log() -> list[dict]:
    return [
        {"datum": "2026-09-15", "rolle": "Fachbereich", "usecase": "A", "aktion": "Idea submitted", "details": "Customer advice"},
        {"datum": "2026-09-18", "rolle": "Datenschutz", "usecase": "A", "aktion": "Data protection approved", "details": "EU hosting, DPA"},
        {"datum": "2026-09-22", "rolle": "Geschäftsführung", "usecase": "A", "aktion": "Decision: Approved", "details": "Pilot with 8 people"},
        {"datum": "2026-09-22", "rolle": "Geschäftsführung", "usecase": "F", "aktion": "Decision: On hold", "details": "High effort"},
        {"datum": "2026-10-06", "rolle": "Geschäftsführung", "usecase": "D", "aktion": "Decision: Approved", "details": "Quick win"},
        {"datum": "2026-10-13", "rolle": "AI Manager", "usecase": "A", "aktion": "Pilot started", "details": "Test questions 3 of 4 correct"},
    ]


def radar() -> list[dict]:
    return [
        {"name": "GPT-4o mini (OpenAI)", "kategorie": "Language model", "einsatz": "Knowledge assistant, drafts",
         "datenschutz": "Only with a DPA and EU data processing", "einschaetzung": "Einsetzen", "geprueft": "2026-09"},
        {"name": "Microsoft 365 Copilot", "kategorie": "Office software", "einsatz": "Minutes, summaries",
         "datenschutz": "Within the company's Microsoft 365 tenant", "einschaetzung": "Testen", "geprueft": "2026-10"},
        {"name": "Mistral (EU provider)", "kategorie": "Language model", "einsatz": "Alternative based in the EU",
         "datenschutz": "Processing in the EU possible", "einschaetzung": "Testen", "geprueft": "2026-10"},
        {"name": "Ollama with open models", "kategorie": "Local models", "einsatz": "Sensitive data without an external service",
         "datenschutz": "Data stays in the company network", "einschaetzung": "Testen", "geprueft": "2026-08"},
        {"name": "n8n", "kategorie": "Automation", "einsatz": "Connect e-mail, portal and AI workflows",
         "datenschutz": "Can be self-hosted", "einschaetzung": "Einsetzen", "geprueft": "2026-09"},
        {"name": "Image generation for marketing", "kategorie": "Generative images", "einsatz": "Graphics for social media",
         "datenschutz": "Copyright and personality rights unclear", "einschaetzung": "Beobachten", "geprueft": "2026-07"},
    ]
