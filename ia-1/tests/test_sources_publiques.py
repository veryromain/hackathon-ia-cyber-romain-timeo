"""Listes publiques (OFAC, ScamSniffer) : extraction, format flags, chargement hors chaîne dans le moteur."""
import json

import oracle.sources_publiques as S
from score.moteur import Moteur

SANC = "0x0330070fd38ec3bb94f58fa55d40368271e9e54a"  # première adresse ETH de la liste OFAC publiée (cache)


def test_extraction_et_format():
    adr = S.adresses_de("foo 0x0330070FD38EC3BB94F58FA55D40368271E9E54A bar\n0x0330070fd38ec3bb94f58fa55d40368271e9e54a")
    assert adr == [SANC]
    e = S.entree("ofac", SANC, 1000)
    assert e["level"] == "hold" and e["category"] == "sanctions" and e["expires_at"] == 1000 + S.DUREE_S
    assert set(e) >= {"address", "level", "category", "confidence", "sources_count", "source_url", "quote", "evidence_hash", "expires_at"}


def test_moteur_met_en_attente_un_paiement_vers_une_adresse_sanctionnee(tmp_path):
    f = tmp_path / "listes.jsonl"
    f.write_text(json.dumps(S.entree("ofac", SANC, 1760000000)) + "\n")
    m = Moteur(carnet=[SANC])  # même « connue », une adresse sanctionnée est mise en attente
    assert m.charger_listes_publiques(f) == 1
    t = 1760100000
    a = m.traiter({"seq": 1, "timestamp": t, "tx_hash": "0x" + "1" * 64, "tx_from": "0x" + "a" * 40, "type": "payment_proposed",
                   "data": {"payment_id": 1, "proposer": "0x" + "a" * 40, "to": SANC, "token": "0x", "amount": str(10**21),
                            "memo": "Facture", "required_approvals": 2, "executable_after": t + 60}})
    assert a["level"] == "hold" and a["reasons"][0]["code"] == "FLAGGED_ADDRESS" and "sanctions" in a["reasons"][0]["detail"]
