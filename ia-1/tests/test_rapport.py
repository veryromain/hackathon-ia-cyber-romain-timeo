"""Tests hors ligne de R4 : faits établis par le code, garde-fous sur la synthèse."""
import json
from pathlib import Path

import score.rapport as R

ICI = Path(__file__).resolve().parents[1]
DEMO = ICI / "dashboard" / "demo"  # exemple de Timéo joué par le moteur (python -m dashboard.preparer_demo)


def faits_demo():
    return R.etablir_faits(R.lire(DEMO / "events.jsonl"), R.lire(DEMO / "alerts.jsonl"), R.lire(DEMO / "flags.jsonl"))


def test_faits_de_la_demo():
    f = faits_demo()
    assert len(f["paiements"]) == 4  # 3 fraudes + nouveau fournisseur (step_up)
    assert f["sorti"] == 12000 * R.UNITE  # seul le nouveau fournisseur légitime a été payé
    assert f["protege"] == (95000 + 98000 + 99500) * R.UNITE
    assert f["delai_max"] is not None and f["delai_max"] <= 10


def test_rapport_sans_llm_complet(tmp_path):
    texte = R.generer(DEMO, sans_llm=True)
    assert "292 500 mUSD" in texte and "## 4. Preuves" in texte and "wallet_frozen" in texte
    assert "rédigée par code" in texte


def test_synthese_avec_montant_invente_rejetee():
    f = faits_demo()
    assert R.verifier("Les fraudeurs ont tenté 999 999 mUSD.", f) is False
    assert R.verifier("Au total, 292 500 mUSD ont été protégés.", f) is True


def test_synthese_avec_hash_rejetee():
    f = faits_demo()
    assert R.verifier("Voir la transaction 0x09caa1de14f86c5c19bf53cadc4206fd872a7bf71cda9814b590eb8c6e706fbb.", f) is False


def test_dossier_vide(tmp_path):
    assert "Aucun incident" in R.generer(tmp_path, sans_llm=True)
