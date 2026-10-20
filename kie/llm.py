"""Zugriff auf das Sprachmodell. Ohne API-Schlüssel arbeitet die App mit einfachen Regeln weiter (Offline-Modus)."""
import json
import os
import re

MODEL = "gpt-4o-mini"


def available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def chat_json(system: str, user: str) -> dict:
    from openai import OpenAI

    client = OpenAI(timeout=30, max_retries=2)
    response = client.chat.completions.create(
        model=MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return json.loads(response.choices[0].message.content)


STECKBRIEF_SYSTEM = """Du unterstützt die Einführung von KI in einem Unternehmen der Logistikbranche.
Ein Fachbereich beschreibt eine Idee in eigenen Worten. Strukturiere sie als Steckbrief auf Deutsch, sachlich und knapp.
Personenbezogene Daten wurden bereits durch Platzhalter wie <NAME> ersetzt. Erfinde keine Zahlen.
Gib JSON zurück mit den Schlüsseln:
"titel" (max. 8 Wörter), "problem", "ziel", "nutzende" (wer arbeitet damit), "daten" (welche Daten werden gebraucht),
"schnittstellen" (betroffene Systeme), "erfolgskriterien" (Liste mit 2 bis 3 messbaren Kriterien),
"datenschutz_hinweise" (Liste kurzer Hinweise), "offene_fragen" (Liste mit 2 bis 3 Fragen an den Fachbereich)."""

ANSWER_SYSTEM = """Du bist der interne Wissensassistent. Beantworte die Frage NUR mit den nummerierten Auszügen.
Wenn die Auszüge die Frage nicht beantworten, setze "gefunden" auf false und lass "antwort" leer. Rate nie.
Antworte kurz (höchstens 3 Sätze) auf Deutsch. Gib JSON zurück: {"gefunden": bool, "antwort": str, "quellen": [int]}"""


STECKBRIEF_SYSTEM_EN = """You support the introduction of AI in a logistics company.
A business unit describes an idea in its own words. Structure it as a short, factual brief in English.
Personal data has already been replaced by placeholders such as <NAME>. Do not invent numbers.
Return JSON with the keys:
"titel" (max. 8 words), "problem", "ziel" (goal), "nutzende" (who works with it), "daten" (data needed),
"schnittstellen" (systems involved), "erfolgskriterien" (list of 2 to 3 measurable criteria),
"datenschutz_hinweise" (list of short data protection notes), "offene_fragen" (list of 2 to 3 questions for the business unit)."""

ANSWER_SYSTEM_EN = """You are the internal knowledge assistant. Answer ONLY from the numbered excerpts.
If the excerpts do not answer the question, set "gefunden" to false and leave "antwort" empty. Never guess.
Answer briefly (max. 3 sentences) in English. Return JSON: {"gefunden": bool, "antwort": str, "quellen": [int]}"""


def prompts(lang: str) -> tuple[str, str]:
    return (STECKBRIEF_SYSTEM, ANSWER_SYSTEM) if lang == "de" else (STECKBRIEF_SYSTEM_EN, ANSWER_SYSTEM_EN)


def offline_steckbrief(text: str, title: str, lang: str = "de") -> dict:
    """Regelbasierter Ersatz, damit die App ohne Schlüssel bedienbar bleibt."""
    personal = re.search(r"kunde|mitglied|fahrer|name|kennzeichen|adresse|customer|member|driver|plate|address|<", text, re.I)
    if lang == "en":
        unit, it = "To be clarified with the business unit.", "To be clarified with IT."
        return {"titel": title or "New idea", "problem": text.strip()[:300], "ziel": unit, "nutzende": unit, "daten": unit,
                "schnittstellen": it, "erfolgskriterien": ["Measure time saved per case"],
                "datenschutz_hinweise": ["Probably contains personal data: check pseudonymisation."] if personal
                else ["No obvious personal data."],
                "offene_fragen": ["How often does the task occur per month?", "Which systems are involved?"]}
    unit, it = "Mit dem Fachbereich zu klären.", "Mit der IT zu klären."
    return {"titel": title or "Neue Idee", "problem": text.strip()[:300], "ziel": unit, "nutzende": unit, "daten": unit,
            "schnittstellen": it, "erfolgskriterien": ["Zeitersparnis pro Fall messen"],
            "datenschutz_hinweise": ["Enthält vermutlich personenbezogene Daten: Pseudonymisierung prüfen."] if personal
            else ["Keine offensichtlichen personenbezogenen Daten."],
            "offene_fragen": ["Wie oft fällt die Aufgabe pro Monat an?", "Welche Systeme sind beteiligt?"]}
