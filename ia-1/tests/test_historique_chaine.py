"""Historique on-chain du destinataire : testé sans réseau, avec un lecteur factice."""
import json
from pathlib import Path

from score import historique_chaine, regles
from score.historique_chaine import Historique
from score.moteur import Moteur

ECH = Path(__file__).resolve().parents[2] / "shared" / "echantillons"
CARNET = json.loads((Path(__file__).resolve().parents[1] / "config" / "carnet.exemple.json").read_text())
T0 = 1_760_000_000  # un lundi à 10h53, heure de Paris : aucune règle d'horaire
INCONNU = "0x" + "ab" * 20


def proposition(to=INCONNU, pid=1, montant=1_000):
    return {"type": "payment_proposed", "timestamp": T0, "tx_hash": "0x" + "11" * 32,
            "data": {"payment_id": pid, "to": to, "amount": str(montant * regles.UNITE), "memo": "Facture", "proposer": "0x" + "01" * 20}}


def codes(historique, to=INCONNU, carnet=()):
    appels = []
    def lecteur(adresse):
        appels.append(adresse)
        return historique
    alerte = Moteur(list(carnet), historique=lecteur).traiter(proposition(to))
    return ({r["code"]: r for r in alerte["reasons"]} if alerte else {}), alerte, appels


def test_adresse_vierge_signalee_sans_mise_en_attente():
    raisons, alerte, _ = codes(Historique(INCONNU, 0, False, jamais_vue=True))
    assert "vierge" in raisons["FRESH_ADDRESS"]["detail"]
    assert alerte["level"] == "step_up"  # avec NEW_RECIPIENT : une signature de plus, pas d'attente


def test_adresse_active_depuis_trois_jours():
    raisons, _, _ = codes(Historique(INCONNU, 4, False, premiere_activite=T0 - 3 * 86400))
    assert "depuis 3 j" in raisons["FRESH_ADDRESS"]["detail"]


def test_adresse_ancienne_et_active_ne_dit_rien():
    raisons, _, _ = codes(Historique(INCONNU, 250, False, premiere_activite=T0 - 400 * 86400))
    assert list(raisons) == ["NEW_RECIPIENT"]


def test_contrat_neuf_non_verifie_pese_plus_qu_un_contrat_neuf_verifie():
    neuf = dict(transactions_emises=1, est_contrat=True, premiere_activite=T0 - 86400)
    non_verifie, _, _ = codes(Historique(INCONNU, code_verifie=False, **neuf))
    verifie, _, _ = codes(Historique(INCONNU, code_verifie=True, **neuf))
    assert "non publié" in non_verifie["NEW_CONTRACT"]["detail"]
    assert "NEW_CONTRACT" in verifie and "non publié" not in verifie["NEW_CONTRACT"]["detail"]
    ancien, _, _ = codes(Historique(INCONNU, 1, True, premiere_activite=T0 - 900 * 86400, code_verifie=False))
    assert "NEW_CONTRACT" not in ancien  # un vieux contrat non vérifié (coffre multi-signataires d'un fournisseur) n'est pas un signal


def test_aucun_poids_ne_met_en_attente_seul_avec_nouveau_destinataire():
    for cle in ("FRESH_ADDRESS", "FRESH_ADDRESS_FAIBLE", "NEW_CONTRACT", "NEW_CONTRACT_NON_VERIFIE"):
        assert 1 - (1 - regles.POIDS["NEW_RECIPIENT"]) * (1 - regles.POIDS[cle]) < regles.SEUIL_HOLD


def test_destinataire_du_carnet_jamais_interroge():
    raisons, alerte, appels = codes(Historique(INCONNU, 0, False, jamais_vue=True), carnet=[INCONNU])
    assert alerte is None and appels == []


def test_reseau_muet_le_moteur_note_quand_meme():
    raisons, alerte, _ = codes(None)
    assert list(raisons) == ["NEW_RECIPIENT"]


def test_sans_lecteur_les_alertes_des_exemples_sont_inchangees():
    def jouer(**options):
        m = Moteur(CARNET, **options)
        sorties = [m.traiter(json.loads(l)) for l in (ECH / "events.exemple.jsonl").read_text().splitlines()]
        return [(a["payment_id"], a["level"], a["score"], [r["code"] for r in a["reasons"]]) for a in sorties if a]
    assert jouer() == jouer(historique=None)
    assert all("FRESH_ADDRESS" not in c and "NEW_CONTRACT" not in c for *_, c in jouer())


def test_lecteur_garde_en_memoire_et_ne_leve_jamais(monkeypatch):
    appels = []
    def lire(adresse, rpc, explorateur=None):
        appels.append(adresse)
        if adresse.endswith("ff"):
            raise OSError("réseau coupé")
        return Historique(adresse, 0, False)
    monkeypatch.setattr(historique_chaine, "lire", lire)
    lecteur = historique_chaine.Lecteur("http://noeud.test")
    assert lecteur(INCONNU.upper().replace("0X", "0x")).adresse == INCONNU
    lecteur(INCONNU)
    assert appels == [INCONNU]
    assert lecteur("0x" + "ff" * 20) is None
