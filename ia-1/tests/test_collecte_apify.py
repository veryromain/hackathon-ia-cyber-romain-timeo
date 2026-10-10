"""Collecte par Apify : testée sans réseau, en remplaçant l'appel à Apify par des pages du corpus de démo."""
from pathlib import Path

from oracle import collecte_apify, oracle

DEMO = Path(__file__).resolve().parents[1] / "oracle" / "corpus_demo"


def fausses_pages(urls):
    html = (DEMO / "01-forum-arnaque.html").read_text(encoding="utf-8")
    return [{"url": u, "html": html} for u in urls]


def test_une_page_collectee_passe_par_l_oracle_et_garde_son_url(tmp_path, monkeypatch):
    monkeypatch.setattr(collecte_apify, "CACHE", tmp_path / "cache")
    url = "https://chainabuse.com/report/123"
    candidats, _ = collecte_apify.lire_pages(fausses_pages([url]), sans_llm=True, maintenant=1_760_000_000)
    assert candidats, "le forum de démo accuse au moins une adresse"
    for c in candidats:
        assert c["source_url"] == url
        assert c["address"].startswith("0x") and len(c["address"]) == 42
        assert oracle.citation_valide(c["quote"], c["address"], oracle.texte_de(str(DEMO / "01-forum-arnaque.html")))
    assert oracle.cle_source(url) == "chainabuse.com"  # la réputation tient à l'hôte réel, pas au fichier en cache


def test_la_meme_source_collectee_deux_fois_ne_compte_qu_une_fois(tmp_path, monkeypatch):
    monkeypatch.setattr(collecte_apify, "CACHE", tmp_path / "cache")
    pages = fausses_pages(["https://blog-inconnu.test/a", "https://blog-inconnu.test/b"])
    candidats, _ = collecte_apify.lire_pages(pages, sans_llm=True, maintenant=1_760_000_000)
    publies, attente = oracle.consolider(candidats)
    assert not publies and attente  # un seul hôte inconnu, même répété : pas assez pour publier


def test_le_texte_de_l_oracle_est_retabli_apres_la_lecture(tmp_path, monkeypatch):
    monkeypatch.setattr(collecte_apify, "CACHE", tmp_path / "cache")
    avant = oracle.texte_de
    collecte_apify.lire_pages(fausses_pages(["https://exemple.test/x"]), sans_llm=True)
    assert oracle.texte_de is avant


def test_la_recherche_dedoublonne_et_borne_les_urls(monkeypatch):
    reponse = [{"organicResults": [{"url": "https://a.test/1"}, {"url": "https://a.test/1"}, {"url": "https://b.test/2"}, {"url": "https://c.test/3"}]}]
    monkeypatch.setattr(collecte_apify, "appeler_apify", lambda acteur, entree, delai_s=300: reponse)
    assert collecte_apify.rechercher("0x" + "ab" * 20, maximum=2) == ["https://a.test/1", "https://b.test/2"]
