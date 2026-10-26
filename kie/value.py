"""Wertbeitrag: Value Case in Euro, Messung von Ziel und Ist sowie Quartalsbericht (QBR). Reine Funktionen, testbar."""
from dataclasses import dataclass

from .scoring import time_saving

HOURS_PER_PERSON_DAY = 8
DEFAULTS = {"stundensatz": 45.0, "entwicklung_satz": 80.0, "betrieb_monat": 0.0}


@dataclass
class ValueCase:
    hours_per_month: float
    benefit_per_month: float
    run_cost_per_month: float
    net_per_month: float
    build_cost: float
    payback_months: float | None  # None: rechnet sich nicht oder keine Aufbaukosten erfasst
    roi_first_year: float | None  # None: keine Aufbaukosten erfasst


def settings(uc: dict) -> dict:
    return DEFAULTS | uc.get("wert", {}).get("annahmen", {})


def value_case(uc: dict) -> ValueCase:
    """Nutzen = gesparte Stunden × Stundensatz; Aufbau = IT-Personentage × 8 h × Entwicklungssatz."""
    a = settings(uc)
    hours = time_saving(uc["prozess"], uc["faelle_pro_monat"]).hours_per_month
    benefit = round(hours * a["stundensatz"], 2)
    run = float(a["betrieb_monat"])
    net = round(benefit - run, 2)
    build = float(uc.get("it", {}).get("personentage", 0)) * HOURS_PER_PERSON_DAY * a["entwicklung_satz"]
    payback = round(build / net, 1) if net > 0 and build else None
    roi = round((12 * net - build) / build, 2) if build else None
    return ValueCase(hours, benefit, run, net, build, payback, roi)


def quarter(month: str) -> str:
    """„2026-10“ → „2026-Q4“."""
    year, m = month.split("-")
    return f"{year}-Q{(int(m) - 1) // 3 + 1}"


def realisation(target: float, actual: float) -> tuple[float | None, str]:
    """Anteil des Ziels, der erreicht wurde, und eine Ampel: ab 90 % grün, ab 60 % gelb, darunter rot."""
    if not target:
        return None, "offen"
    share = round(actual / target, 2)
    return share, "gruen" if share >= 0.9 else "gelb" if share >= 0.6 else "rot"


def qbr(usecases: list[dict], period: str) -> list[dict]:
    """Eine Zeile je Anwendungsfall mit Messungen im Quartal: Ziel- und Ist-Stunden, Realisierung, Wert in Euro."""
    rows = []
    for uc in usecases:
        entries = [e for e in uc.get("wert", {}).get("messungen", []) if quarter(e["monat"]) == period]
        if not entries:
            continue
        target = sum(float(e["ziel"]) for e in entries)
        actual = sum(float(e["ist"]) for e in entries)
        share, level = realisation(target, actual)
        rate = settings(uc)["stundensatz"]
        rows.append({"id": uc["id"], "titel": uc["titel"], "status": uc["status"], "ziel_h": target, "ist_h": actual,
                     "realisierung": share, "ampel": level, "wert_eur": round(actual * rate, 2),
                     "nutzende": max(int(e.get("nutzende", 0)) for e in entries)})
    return rows


def periods(usecases: list[dict]) -> list[str]:
    return sorted({quarter(e["monat"]) for uc in usecases for e in uc.get("wert", {}).get("messungen", [])}, reverse=True)


def summary(rows: list[dict], lang: str = "de") -> list[str]:
    """Kernaussagen für den Quartalsbericht, aus den Zahlen abgeleitet (kein Sprachmodell)."""
    if not rows:
        return []
    en = lang == "en"
    target = sum(r["ziel_h"] for r in rows)
    actual = sum(r["ist_h"] for r in rows)
    value = sum(r["wert_eur"] for r in rows)
    share = actual / target if target else 0
    euro = f"{value:,.0f}" if en else f"{value:,.0f}".replace(",", ".")  # deutsches Tausendertrennzeichen
    lines = [(f"{len(rows)} use cases measured: {actual:g} of {target:g} target hours saved ({share:.0%}), worth €{euro}."
              if en else f"{len(rows)} Anwendungsfälle gemessen: {actual:g} von {target:g} Zielstunden gespart ({share:.0%}), "
              f"Wert {euro} €.")]
    for r in sorted(rows, key=lambda r: r["realisierung"] or 0):
        if r["ampel"] == "rot":
            lines.append(f"{r['id']}. {r['titel']}: only {r['realisierung']:.0%} of target, find the cause with the business unit."
                         if en else f"{r['id']}. {r['titel']}: nur {r['realisierung']:.0%} des Ziels, Ursache mit dem Fachbereich klären.")
        elif r["ampel"] == "gelb":
            lines.append(f"{r['id']}. {r['titel']}: {r['realisierung']:.0%} of target, check adoption and training."
                         if en else f"{r['id']}. {r['titel']}: {r['realisierung']:.0%} des Ziels, Nutzung und Schulung prüfen.")
        else:
            lines.append(f"{r['id']}. {r['titel']}: {r['realisierung']:.0%} of target, ready to scale."
                         if en else f"{r['id']}. {r['titel']}: {r['realisierung']:.0%} des Ziels, bereit zum Ausrollen.")
    return lines
