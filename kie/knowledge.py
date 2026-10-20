"""Kleine Wissensbasis für den Prüfstand: Abschnitte aus Markdown, Suche per BM25 (ohne externe Dienste)."""
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

WORD = re.compile(r"[a-zäöüß0-9]+", re.I)
STOP = set(
    "der die das und oder ein eine einer eines ist sind wird werden wie was wer wo wann mit von zu im in am an auf für"
    " den dem des nicht nur ich wir sie es bei nach über ab"
    " a an the and or is are be do does how what when which who with of to in on at for from my i can"
    " it this that".split()
)


@dataclass
class Section:
    id: int
    source: str
    title: str
    section: str
    area: str
    text: str


def _tokens(text: str) -> list[str]:
    return [w for w in (t.lower() for t in WORD.findall(text)) if w not in STOP]


def load_sections(folder: Path, overview: str = "Überblick") -> list[Section]:
    sections: list[Section] = []
    for path in sorted(folder.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ").strip()
        area = (re.search(r"(?:Bereich|Area): ([^·\n]+)", raw) or [None, ""])[1].strip()
        parts = re.split(r"(?m)^## ", raw)
        intro = "\n".join(line for line in parts[0].splitlines()[1:] if not line.startswith(("Bereich:", "Area:"))).strip()
        chunks = ([(overview, intro)] if intro else []) + [
            (p.splitlines()[0].strip(), "\n".join(p.splitlines()[1:]).strip()) for p in parts[1:]]
        for name, body in chunks:
            if body:
                sections.append(Section(len(sections), path.name, title, name, area, body))
    return sections


class Index:
    def __init__(self, sections: list[Section]):
        self.sections = sections
        self.docs = [_tokens(f"{s.title} {s.section} {s.text}") for s in sections]
        self.df = Counter(t for d in self.docs for t in set(d))
        self.avg = sum(map(len, self.docs)) / max(len(self.docs), 1)

    def _tf(self, term: str, doc: list[str]) -> int:
        """Exakte Treffer; bei längeren Wörtern zählen auch Komposita mit gleichem Wortanfang (Karte, Ersatzkarte)."""
        exact = doc.count(term)
        if exact or len(term) < 5:
            return exact
        return sum(1 for t in doc if term[:5] in t)

    def search(self, query: str, k: int = 3) -> list[tuple[Section, float]]:
        n = len(self.docs)
        terms = set(_tokens(query))
        scores = []
        for doc in self.docs:
            s = 0.0
            for term in terms:
                tf = self._tf(term, doc)
                if not tf:
                    continue
                idf = math.log(1 + (n - self.df.get(term, 1) + 0.5) / (self.df.get(term, 1) + 0.5))
                s += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * len(doc) / self.avg))
            scores.append(s)
        best = sorted(range(n), key=lambda i: -scores[i])[:k]
        return [(self.sections[i], round(scores[i], 2)) for i in best if scores[i] > 0]
