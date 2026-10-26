from pathlib import Path

from kie import pdf, seed
from kie.knowledge import Index, load_sections
from kie.privacy import pseudonymise
from kie.scoring import ampel, ranking, score, time_saving

ROOT = Path(__file__).resolve().parents[1]


def test_score_and_ranking_follow_the_formula():
    ucs = seed.usecases()
    assert score({"nutzen": 5, "aufwand": 2, "umsetzbarkeit": 5, "risiko": 2}) == 6
    ranks = ranking(ucs)
    assert ranks["A"] == 1 and ranks["D"] == 2 and ranks["F"] == 7
    assert ranks["C"] == ranks["E"] == 3  # gleiche Punktzahl, gleicher Rang


def test_time_saving():
    steps = [{"schritt": "Suchen", "minuten": 6, "ki": True, "minuten_mit_ki": 1},
             {"schritt": "Schreiben", "minuten": 2, "ki": False, "minuten_mit_ki": 0}]
    s = time_saving(steps, 120)
    assert (s.minutes_before, s.minutes_after, s.hours_per_month) == (8, 3, 10.0)


def test_ampel_levels():
    assert ampel({})[0] == "offen"
    assert ampel({"personenbezogen": False, "extern": True, "pseudonymisierung": True, "pruefung": True})[0] == "gruen"
    assert ampel({"personenbezogen": True, "extern": True, "pseudonymisierung": True, "pruefung": True, "rollen": True})[0] == "gelb"
    assert ampel({"personenbezogen": True, "besondere": True, "extern": True})[0] == "rot"


def test_pseudonymise_german_identifiers():
    text = "Kontakt: Kim Becker, Tel. 0261 1234567, Fahrzeug KO-AB 123, Mail becker@spedition.example, IBAN DE89 3704 0044 0532 0130 00"
    clean, counts = pseudonymise(text)
    for secret in ["Becker,", "1234567", "KO-AB 123", "becker@", "DE89"]:
        assert secret not in clean
    assert counts["KENNZEICHEN"] == 1 and counts["TELEFON"] == 1


def test_knowledge_search_and_refusal():
    index = Index(load_sections(ROOT / "data" / "wissen"))
    top = index.search("Wie schnell bekommt man eine Ersatzkarte?")[0][0]
    assert top.section == "Ersatzkarte"
    assert index.search("Wer hat das Fußballspiel gewonnen?") == []


def test_pdf_exports():
    ucs = seed.usecases()
    assert pdf.entscheidungsvorlage(ucs[1], 5).startswith(b"%PDF")
    assert pdf.zertifikat("Test", 0.8).startswith(b"%PDF")


def test_it_status_levels():
    from kie.scoring import IT_CHECKS, it_status

    assert it_status({})[0] == "offen"
    assert it_status({c[0]: True for c in IT_CHECKS})[0] == "gruen"
    assert it_status({"schnittstelle": True, "hosting": True, "anmeldung": True})[0] == "gelb"
    level, done, hints = it_status({"schnittstelle": True})
    assert level == "rot" and done == 1 and len(hints) == 4


def test_aiact_classification_follows_the_order_of_the_law():
    from kie.aiact import classify, duties

    assert classify({}) == ("offen", [])
    assert classify({"chatbot": False})[0] == "minimal"
    assert classify({"emotion_work": True, "hr": True})[0] == "verboten"  # prohibited beats high risk
    assert classify({"hr": True}) == ("hoch", ["Anhang III Nr. 4"])
    assert classify({"product_safety": True})[0] == "hoch"
    assert classify({"chatbot": True})[0] == "begrenzt"
    assert duties("offen") == []
    assert any("Art. 4" in d for d in duties("minimal", "en"))


def test_aiact_exception_never_applies_with_profiling():
    from kie.aiact import classify

    assert classify({"education": True, "narrow_task": True}) == ("minimal", ["Art. 6 (3)"])
    assert classify({"hr": True, "narrow_task": True, "profiling": True})[0] == "hoch"
    assert classify({"hr": True, "narrow_task": True, "chatbot": True}) == ("begrenzt", ["Art. 6 (3)", "Art. 50 (1)"])


def test_gxp_hints_only_when_relevant():
    from kie.aiact import gxp_hints

    assert gxp_hints({}) == []
    assert any("Annex 11" in h for h in gxp_hints({"gxp_records": True}, "en"))
