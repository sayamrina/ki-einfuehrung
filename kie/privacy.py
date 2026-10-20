"""Pseudonymisierung vor jedem Modellaufruf (regelbasiert, bewusst vorsichtig)."""
import re

PATTERNS = [
    ("E-MAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b")),
    ("TELEFON", re.compile(r"(?<!\w)(?:\+\d{2}|0)[ ]?[1-9][\d /-]{6,14}\d")),
    ("KENNZEICHEN", re.compile(r"\b[A-ZÄÖÜ]{1,3}[- ][A-Z]{1,2} ?\d{1,4}[EH]?\b")),
    ("GEBURTSDATUM", re.compile(r"(?i)(?<=geboren am )\d{1,2}\.\d{1,2}\.\d{4}|(?<=geb\. )\d{1,2}\.\d{1,2}\.\d{4}"
                                r"|(?<=born on )\d{1,2}[./]\d{1,2}[./]\d{4}")),
    ("NAME", re.compile(r"(?<=Herr )[A-ZÄÖÜ][a-zäöüß]+|(?<=Frau )[A-ZÄÖÜ][a-zäöüß]+|(?<=Mr\. )[A-Z][a-z]+|(?<=Ms\. )[A-Z][a-z]+"
                        r"|(?<=Mr )[A-Z][a-z]+|(?<=Ms )[A-Z][a-z]+")),
    ("NAME", re.compile(r"(?<=Grüßen\n)[A-ZÄÖÜ][a-zäöüß]+ [A-ZÄÖÜ][a-zäöüß]+")),
    ("NAME", re.compile(r"(?:(?<=Kontakt: )|(?<=Contact: )|(?<=regards, )|(?<=regards\n))[A-ZÄÖÜ][a-zäöüß]+ [A-ZÄÖÜ][a-zäöüß]+")),
]


def pseudonymise(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    def mark(label: str) -> str:
        counts[label] = counts.get(label, 0) + 1
        return f"<{label}>"

    for label, pattern in PATTERNS:
        text = pattern.sub(lambda _m, label=label: mark(label), text)
    return text, counts
