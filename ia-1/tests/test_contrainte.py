"""Clé d'identité / de contrainte : alerte privée quand tx_from n'est pas le signataire nommé ; jamais dans alerts.jsonl."""
from score.moteur import Moteur

EMMA, EMMA_ID, A = "0x" + "e" * 40, "0x" + "1" * 40, "0x" + "a" * 40


def test_signature_par_cle_d_identite_alerte_privee_seulement():
    envoyes = []
    m = Moteur(carnet=[A], notifier=lambda a, p: envoyes.append(a))
    publique = m.traiter({"seq": 1, "timestamp": 1760100000, "tx_hash": "0x1", "tx_from": EMMA_ID, "type": "payment_approved",
                          "data": {"payment_id": 7, "owner": EMMA, "approvals": 2, "required_approvals": 2}})
    assert publique is None  # rien pour le relais
    assert m.alertes_privees[0]["reasons"][0]["code"] == "DURESS_SIGNATURE" and m.alertes_privees[0]["prive"]
    assert envoyes and envoyes[0]["reasons"][0]["code"] == "DURESS_SIGNATURE"


def test_signature_normale_sans_alerte():
    m = Moteur(carnet=[A])
    m.traiter({"seq": 1, "timestamp": 1760100000, "tx_hash": "0x1", "tx_from": EMMA, "type": "payment_approved",
               "data": {"payment_id": 7, "owner": EMMA, "approvals": 2, "required_approvals": 2}})
    assert m.alertes_privees == []
