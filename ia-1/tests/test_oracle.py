"""Tests hors ligne de l'oracle (sans appel à Bedrock)."""
from pathlib import Path

import oracle.oracle as O

CORPUS = Path(__file__).resolve().parents[1] / "oracle" / "corpus_demo"
ARNAQUE = "0x6253540229bdcc8ae009fe075005a3fa5137c352"


def test_texte_cache_ecarte():
    assert "0x9d69739792" not in O.texte_de(str(CORPUS / "04-injection.html"))


def test_citation_doit_etre_dans_la_page_et_contenir_l_adresse():
    texte = O.texte_de(str(CORPUS / "01-forum-arnaque.html"))
    assert O.citation_valide("a reçu les fonds de trois victimes", ARNAQUE, texte) is False  # sans l'adresse
    assert O.citation_valide(f"l'adresse {ARNAQUE} a volé 1 million", ARNAQUE, texte) is False  # inventée
    assert O.citation_valide(f"l'adresse {ARNAQUE}   a reçu les fonds", ARNAQUE, texte) is True  # espaces normalisés


def faux_modele(reponses):
    return lambda texte, adresses: reponses


def test_hallucination_rejetee(monkeypatch):
    monkeypatch.setattr(O, "analyser_bedrock", faux_modele([
        {"adresse": ARNAQUE, "verdict": "accusation", "categorie": "scam_report", "confiance": 0.99,
         "citation": f"{ARNAQUE} a blanchi 50 millions"}]))
    acc, rej = O.traiter_page(str(CORPUS / "01-forum-arnaque.html"))
    assert acc == [] and rej[0]["reject_reason"] == "quote_not_found"


def test_adresse_inventee_par_le_modele_ignoree(monkeypatch):
    monkeypatch.setattr(O, "analyser_bedrock", faux_modele([
        {"adresse": "0x" + "9" * 40, "verdict": "accusation", "categorie": "scam_report", "confiance": 0.99,
         "citation": "x"}]))
    acc, rej = O.traiter_page(str(CORPUS / "03-mention-neutre.html"))
    assert acc == [] and rej[0]["reject_reason"] == "not_analysed"


def test_accusation_acceptee_format_flags(monkeypatch):
    monkeypatch.setattr(O, "analyser_bedrock", faux_modele([
        {"adresse": ARNAQUE, "verdict": "accusation", "categorie": "scam_report", "confiance": 0.9,
         "citation": f"Arnaque : l'adresse {ARNAQUE} a reçu les fonds de trois victimes cette semaine"}]))
    acc, _ = O.traiter_page(str(CORPUS / "01-forum-arnaque.html"), maintenant=1000)
    f = acc[0]
    assert f["level"] == "hold" and f["expires_at"] == 1000 + O.DUREE_SIGNALEMENT_S
    assert f["evidence_hash"].startswith("0x") and len(f["evidence_hash"]) == 66
    assert set(f) >= {"address", "level", "category", "confidence", "sources_count", "source_url", "quote", "evidence_hash", "expires_at"}


def test_confiance_faible_rejetee(monkeypatch):
    monkeypatch.setattr(O, "analyser_bedrock", faux_modele([
        {"adresse": ARNAQUE, "verdict": "accusation", "categorie": "scam_report", "confiance": 0.4,
         "citation": f"l'adresse {ARNAQUE} a reçu les fonds"}]))
    acc, rej = O.traiter_page(str(CORPUS / "01-forum-arnaque.html"))
    assert acc == [] and rej[0]["reject_reason"] == "low_confidence"


def cand(adr, src, conf=0.9):
    return {"address": adr, "level": "hold", "category": "scam_report", "confidence": conf, "sources_count": 1,
            "source_url": src, "quote": "x", "evidence_hash": "0x", "expires_at": 1}


def test_cle_source_url_et_page_locale():
    assert O.cle_source("https://www.ChainAbuse.com/report/12") == "chainabuse.com"
    assert O.cle_source(str(CORPUS / "01-forum-arnaque.html")) == "forum cryptoentraide"


def test_empoisonnement_meme_source_repetee_non_publiee(monkeypatch):
    monkeypatch.setattr(O, "reputations", lambda: {})
    pub, att = O.consolider([cand("0xaa", "https://blog-anonyme.test/1"), cand("0xaa", "https://blog-anonyme.test/2"),
                             cand("0xaa", "https://blog-anonyme.test/3")])
    assert pub == [] and att[0]["reject_reason"] == "single_low_reputation_source" and att[0]["sources_count"] == 1


def test_deux_sources_independantes_publient(monkeypatch):
    monkeypatch.setattr(O, "reputations", lambda: {})
    pub, att = O.consolider([cand("0xaa", "https://site-a.test/1", 0.7), cand("0xaa", "https://site-b.test/9", 0.9)])
    assert att == [] and pub[0]["sources_count"] == 2 and pub[0]["confidence"] == 0.9


def test_une_source_reputee_suffit(monkeypatch):
    monkeypatch.setattr(O, "reputations", lambda: {"chainabuse.com": 0.9})
    pub, _ = O.consolider([cand("0xaa", "https://chainabuse.com/r/1")])
    assert len(pub) == 1
