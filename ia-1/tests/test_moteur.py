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


def test_modele_anomalie_s_entraine_et_s_integre():
    """R2 : appris sur le trafic normal de Timéo, le moteur fonctionne avec et garde ses résultats sur l'exemple."""
    from score.anomalie import entrainer
    donnees = ECH.parent / "donnees"
    events = [json.loads(l) for l in (donnees / "train.events.jsonl").read_text().splitlines() if l.strip()]
    modele, n = entrainer(events, json.loads((donnees / "carnet.json").read_text()))
    assert n > 100 and modele.seuil_fort > modele.seuil_alerte
    m = Moteur(CARNET, modele)
    niveaux = {}
    for ligne in (ECH / "events.exemple.jsonl").read_text().splitlines():
        a = m.traiter(json.loads(ligne))
        if a:
            niveaux[a["payment_id"]] = a["level"]
    assert niveaux.get(4) == niveaux.get(5) == niveaux.get(6) == "hold"


def test_modele_enregistre_se_recharge_depuis_le_moteur(tmp_path):
    """Régression trouvée en intégration : le modèle sauvé par « python -m score.anomalie » doit se charger dans le moteur."""
    import subprocess
    import sys
    racine = Path(__file__).resolve().parents[1]
    donnees = ECH.parent / "donnees"
    modele = tmp_path / "m.joblib"
    subprocess.run([sys.executable, "-m", "score.anomalie", "--events", str(donnees / "train.events.jsonl"),
                    "--carnet", str(donnees / "carnet.json"), "--sortie", str(modele)], cwd=racine, check=True)
    r = subprocess.run([sys.executable, "-m", "score.moteur", "--events", str(ECH / "events.exemple.jsonl"),
                        "--out", str(tmp_path / "a.jsonl"), "--modele", str(modele)], cwd=racine, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_reglage_client_jours_ouvres(tmp_path):
    """Le samedi déclaré ouvré (réglage client) ne déclenche plus OFF_HOURS ; le réglage par défaut, si."""
    from score import regles
    from score.regles import r_hors_heures, EtatPortefeuille
    p = {"timestamp": 1760126111, "tx_hash": "0x", "to": "0x"}  # samedi 10/10/2026 21h55, heure de Paris
    assert r_hors_heures(p, EtatPortefeuille()) is not None
    cfg = tmp_path / "c.json"
    cfg.write_text('{"heures_ouvrees": [7, 23], "jours_ouvres": [0,1,2,3,4,5]}')
    regles.charger_reglages_client(cfg)
    try:
        assert r_hors_heures(p, EtatPortefeuille()) is None
    finally:
        regles.HEURES_OUVREES, regles.JOURS_OUVRES = (7, 20), {0, 1, 2, 3, 4}
