"""Tests du moteur de score sur les exemples de Timéo (shared/echantillons)."""
import json
from pathlib import Path

from score.moteur import Moteur

ECH = Path(__file__).resolve().parents[2] / "shared" / "echantillons"
CARNET = json.loads((Path(__file__).resolve().parents[1] / "config" / "carnet.exemple.json").read_text())


def alertes(carnet=CARNET):
    m = Moteur(carnet)
    out = {}
    for ligne in (ECH / "events.exemple.jsonl").read_text().splitlines():
        a = m.traiter(json.loads(ligne))
        if a:
            out[a["payment_id"]] = a
    return out


def test_paiements_normaux_connus_passent():
    a = alertes()
    assert 1 not in a and 2 not in a


def test_nouveau_fournisseur_legitime_seulement_step_up():
    a = alertes()
    assert a[3]["level"] == "step_up"
    assert [r["code"] for r in a[3]["reasons"]] == ["NEW_RECIPIENT"]


def test_fraude_en_rafale_mise_en_attente():
    a = alertes()
    for pid in (4, 5, 6):
        assert a[pid]["level"] == "hold"
    assert "BURST" in [r["code"] for r in a[5]["reasons"]]


def test_adresse_signalee_par_oracle():
    a = alertes()
    assert a[6]["reasons"][0]["code"] == "FLAGGED_ADDRESS"  # raison la plus forte en premier


def test_chaque_raison_a_un_detail_et_des_preuves_liste():
    for a in alertes().values():
        for r in a["reasons"]:
            assert r["detail"] and isinstance(r["evidence"], list)
