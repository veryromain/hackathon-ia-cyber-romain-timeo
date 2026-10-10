"""Idées 1 et 2 : adresse sosie (address poisoning) et adresse piège (honeypot)."""
from score.moteur import Moteur

FOURNISSEUR = "0x3f7955b8895f5140b072276d92a2c8d05fa19438"
SOSIE = "0x3f79000000000000000000000000000000009438"       # mêmes 4 premiers et 4 derniers caractères
AUTRE = "0x1234000000000000000000000000000000005678"
PIEGE = "0xdead000000000000000000000000000000beef00"
T = 1760100000  # jeudi 10h


def prop(pid, to):
    return {"seq": pid, "timestamp": T, "tx_hash": "0x" + f"{pid:064x}", "tx_from": AUTRE, "type": "payment_proposed",
            "data": {"payment_id": pid, "proposer": AUTRE, "to": to, "token": AUTRE, "amount": str(3 * 10**21), "memo": "Facture",
                     "required_approvals": 2, "executable_after": T + 60}}


def test_sosie_mis_en_attente():
    a = Moteur(carnet=[FOURNISSEUR]).traiter(prop(1, SOSIE))
    assert a["level"] == "hold" and a["reasons"][0]["code"] == "LOOKALIKE_ADDRESS" and "0x3f79…9438" in a["reasons"][0]["detail"]


def test_vrai_fournisseur_et_inconnu_quelconque_non_concernes():
    m = Moteur(carnet=[FOURNISSEUR])
    assert m.traiter(prop(2, FOURNISSEUR)) is None
    a = m.traiter(prop(3, AUTRE))
    assert not a or all(r["code"] != "LOOKALIKE_ADDRESS" for r in a["reasons"])


def test_adresse_piege_hold_quoi_qu_il_arrive():
    m = Moteur(carnet=[FOURNISSEUR], pieges=[PIEGE])
    a = m.traiter(prop(4, PIEGE))
    assert a["level"] == "hold" and a["score"] >= 0.99 and a["reasons"][0]["code"] == "HONEYPOT_ADDRESS"
