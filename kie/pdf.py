"""PDF-Export: Entscheidungsvorlage für die Geschäftsführung und Teilnahmezertifikat."""
from datetime import date
from pathlib import Path

from fpdf import FPDF

from .i18n import DECISION_EN, DS_RELEASE_EN, STATUS_EN
from .scoring import AMPEL_LABEL, IT_LABEL, ampel, it_status, score, time_saving

FONTS = Path(__file__).resolve().parent.parent / "assets"
NAVY = (18, 53, 91)


def _pdf() -> FPDF:
    pdf = FPDF(format="A4")
    pdf.add_font("DejaVu", "", str(FONTS / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONTS / "DejaVuSans-Bold.ttf"))
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_page()
    pdf.set_margins(18, 16, 18)
    return pdf


def _clean(text: str) -> str:
    return text.replace("⚪ ", "").replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "")


def entscheidungsvorlage(uc: dict, rank: int, lang: str = "de") -> bytes:
    en = lang == "en"

    def t(de: str, en_text: str) -> str:
        return en_text if en else de

    pdf = _pdf()
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(11, 110, 138)
    pdf.cell(0, 6, t("ENTSCHEIDUNGSVORLAGE FÜR DIE GESCHÄFTSFÜHRUNG", "DECISION PAPER FOR MANAGEMENT"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 8, f"{uc['id']}. {uc['titel']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(90, 90, 90)
    status = STATUS_EN.get(uc["status"], uc["status"]) if en else uc["status"]
    pdf.cell(0, 6, t(f"Fachbereich: {uc['fachbereich']} · Status: {status} · Stand: {date.today():%d.%m.%Y}",
                     f"Business unit: {uc['fachbereich']} · Status: {status} · Date: {date.today():%d %b %Y}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    sb = uc["steckbrief"]
    saving = time_saving(uc["prozess"], uc["faelle_pro_monat"])
    level, _, _ = ampel(uc["datenschutz"].get("antworten", {}), lang)
    b = uc["bewertung"]
    release = uc["datenschutz"].get("freigabe", "offen")
    release = DS_RELEASE_EN.get(release, release) if en else release
    it = uc.get("it", {})
    it_release = it.get("freigabe", "offen")
    it_release = DS_RELEASE_EN.get(it_release, it_release) if en else it_release
    rows = [
        ("Problem", sb.get("problem", "")), (t("Ziel", "Goal"), sb.get("ziel", "")), (t("Nutzende", "Users"), sb.get("nutzende", "")),
        (t("Daten", "Data"), sb.get("daten", "")), (t("Schnittstellen", "Systems"), sb.get("schnittstellen", "")),
        (t("Bewertung", "Assessment"), t(f"Nutzen {b['nutzen']}, Aufwand {b['aufwand']}, Umsetzbarkeit {b['umsetzbarkeit']}, "
                                         f"Risiko {b['risiko']} → {score(b)} Punkte, Rang {rank}",
                                         f"Benefit {b['nutzen']}, effort {b['aufwand']}, feasibility {b['umsetzbarkeit']}, "
                                         f"risk {b['risiko']} → {score(b)} points, rank {rank}")),
        (t("Zeitersparnis (Schätzung)", "Time saved (estimate)"),
         t(f"{saving.minutes_before:g} → {saving.minutes_after:g} Minuten pro Fall; etwa {saving.hours_per_month:g} Stunden pro Monat "
           f"bei {uc['faelle_pro_monat']} Fällen",
           f"{saving.minutes_before:g} → {saving.minutes_after:g} minutes per case; about {saving.hours_per_month:g} hours per month "
           f"at {uc['faelle_pro_monat']} cases")),
        (t("Datenschutz", "Data protection"), f"{_clean(AMPEL_LABEL[lang][level])}; {t('Freigabe', 'Approval')}: {release}"),
        ("IT", f"{_clean(IT_LABEL[lang][it_status(it.get('antworten', {}), lang)[0]])}; {t('Freigabe', 'Approval')}: {it_release}"
               + (f"; {it['systeme']}" if it.get("systeme") else "")),
        (t("Erfolgskriterien", "Success criteria"), "\n".join(f"• {k}" for k in sb.get("erfolgskriterien", []))),
        (t("Offene Fragen", "Open questions"), "\n".join(f"• {k}" for k in sb.get("offene_fragen", []))),
    ]
    for label, value in rows:
        pdf.set_font("DejaVu", "B", 9.5)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, label, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 9.5)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 5, value or "–", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

    pdf.ln(2)
    pdf.set_draw_color(*NAVY)
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, t("Empfehlung und Entscheidung", "Recommendation and decision"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9.5)
    pdf.set_text_color(30, 30, 30)
    decision = uc.get("entscheidung") or {}
    if decision:
        result = DECISION_EN.get(decision["ergebnis"], decision["ergebnis"]) if en else decision["ergebnis"]
        text = t(f"Entscheidung: {result} am {decision['datum']}. Begründung: {decision['begruendung']}",
                 f"Decision: {result} on {decision['datum']}. Reason: {decision['begruendung']}")
    else:
        text = t("Noch offen.  ☐ Freigeben   ☐ Zurückstellen   ☐ Ablehnen", "Still open.  ☐ Approve   ☐ Put on hold   ☐ Reject")
    pdf.multi_cell(0, 5, text, border=1, padding=3, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 4, t("Erstellt mit der Plattform „KI-Einführung“ (Beispieldaten aus der Logistikbranche). "
                           "Zeitangaben sind Schätzungen der Fachbereiche.",
                           "Created with the \"AI Adoption\" platform (sample data from the logistics sector). "
                           "Time figures are estimates by the business units."))
    return bytes(pdf.output())


def zertifikat(name: str, quote: float, lang: str = "de") -> bytes:
    en = lang == "en"
    pdf = _pdf()
    pdf.ln(30)
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(11, 110, 138)
    pdf.cell(0, 8, "CERTIFICATE OF COMPLETION" if en else "TEILNAHMEZERTIFIKAT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(*NAVY)
    title = "AI Licence: Working safely with AI" if en else "KI-Führerschein: Sicher arbeiten mit KI"
    pdf.cell(0, 14, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("DejaVu", "", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, name or ("Participant" if en else "Teilnehmende Person"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10.5)
    pdf.multi_cell(0, 6, f"has completed the four-module course and passed the final test with {quote:.0%}." if en else
                   f"hat den Kurs mit vier Modulen abgeschlossen und den Abschlusstest mit {quote:.0%} bestanden.",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.cell(0, 6, f"Date: {date.today():%d %b %Y}" if en else f"Datum: {date.today():%d.%m.%Y}", align="C", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
