"""Le moteur ne doit jamais planter ni se tromper sur des entrées bizarres."""
import json
import subprocess
import sys
from pathlib import Path

from score.moteur import Moteur

A, B = "0x" + "a" * 40, "0x" + "b" * 40


def prop(pid, to=B, montant=10**21, memo="Facture", t=1760000000, **kw):
    d = {"payment_id": pid, "proposer": A, "to": to, "token": A, "amount": str(montant), "memo": memo,
         "required_approvals": 2, "executable_after": t + 60}
    d.update(kw)
    return {"seq": pid, "timestamp": t, "tx_hash": "0x" + "1" * 64, "tx_from": A, "type": "payment_proposed", "data": d}


def test_type_inconnu_ignore():
    assert Moteur().traiter({"type": "evenement_du_futur", "data": {}, "timestamp": 0, "tx_hash": "0x"}) is None


def test_adresse_en_majuscules_reconnue():
    m = Moteur([B])
    a = m.traiter(prop(1, to=B.upper().replace("0X", "0x")))
    assert a is None  # destinataire du carnet, quelle que soit la casse


def test_libelle_absent_ou_vide():
    m = Moteur()
    for memo in (None, ""):
        m.traiter(prop(1, memo=memo))


def test_montant_nul():
    m = Moteur([B])
    m.traiter({"type": "payment_executed", "timestamp": 0, "tx_hash": "0x", "data": {"to": B, "amount": "0"}})
    m.traiter(prop(2, montant=0))


def test_adresse_signalee_expiree_ne_compte_plus():
    m = Moteur([B])
    m.traiter({"type": "address_flagged", "timestamp": 0, "tx_hash": "0x2",
               "data": {"flagged": B, "level": "hold", "category": "scam", "expires_at": 1759999000}})
    assert m.traiter(prop(1)) is None  # jeudi 10h53, signalement expiré la veille


def test_ligne_malformee_ne_plante_pas(tmp_path):
    f = tmp_path / "ev.jsonl"
    f.write_text('{"pas du json\n' + json.dumps({"type": "payment_proposed", "data": {}, "timestamp": 0}) + "\n"
                 + json.dumps(prop(1)) + "\n")
    out = tmp_path / "al.jsonl"
    r = subprocess.run([sys.executable, "-m", "score.moteur", "--events", str(f), "--out", str(out)],
                       cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert r.returncode == 0
    assert len(out.read_text().splitlines()) == 1  # la seule proposition valide (destinataire inconnu) donne une alerte
