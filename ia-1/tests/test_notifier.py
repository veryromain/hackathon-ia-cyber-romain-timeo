"""P5 : la notification part à chaque mise en attente, n'arrête jamais le moteur, et laisse une trace."""
import json

import score.notifier as N
from score.moteur import Moteur

A, B = "0x" + "a" * 40, "0x" + "b" * 40


def prop(pid, montant=95 * 10**21):
    t = 1760126111
    return {"seq": pid, "timestamp": t, "tx_hash": "0x" + "1" * 64, "tx_from": A, "type": "payment_proposed",
            "data": {"payment_id": pid, "proposer": A, "to": B, "token": A, "amount": str(montant), "memo": "URGENT confidentiel",
                     "required_approvals": 2, "executable_after": t + 60}}


def test_notification_sur_hold_journalisee(monkeypatch, tmp_path):
    envoyes = []
    monkeypatch.setattr(N, "CANAUX", {"test": lambda titre, corps: envoyes.append((titre, corps)) or True})
    j = tmp_path / "notifications.jsonl"
    m = Moteur(notifier=lambda a, p: N.notifier(a, p, j))
    a = m.traiter(prop(1))
    assert a["level"] == "hold" and len(envoyes) == 1 and "MISE EN ATTENTE" in envoyes[0][0] and "95 000 mUSD" in envoyes[0][1]
    assert json.loads(j.read_text())["canaux"] == ["test"]


def test_canal_en_panne_ne_bloque_pas(monkeypatch, tmp_path):
    def plante(t, c):
        raise RuntimeError("smtp down")
    monkeypatch.setattr(N, "CANAUX", {"email": plante})
    m = Moteur(notifier=lambda a, p: N.notifier(a, p, tmp_path / "n.jsonl"))
    assert m.traiter(prop(2))["level"] == "hold"  # l'alerte part quand même
    assert "smtp down" in (tmp_path / "n.jsonl").read_text()
