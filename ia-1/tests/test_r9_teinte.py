"""R9 : propagation du risque aux adresses qui ont reçu les fonds d'une adresse signalée, avec ses garde-fous."""
from score.moteur import Moteur

SIGNALEE, MULE, INNOCENT, PLATEFORME, A = ("0x" + c * 40 for c in "fabpa")
T0 = 1760100000  # jeudi 10h, heure de Paris


def ev(t, typ, data, seq=1):
    return {"seq": seq, "timestamp": t, "tx_hash": "0x" + f"{seq:064x}", "tx_from": A, "type": typ, "data": data}


def prop(pid, to, t, montant=5 * 10**21):
    return ev(t, "payment_proposed", {"payment_id": pid, "proposer": A, "to": to, "token": A, "amount": str(montant),
                                      "memo": "Facture", "required_approvals": 2, "executable_after": t + 60}, seq=100 + pid)


def moteur():
    m = Moteur(carnet=[MULE, INNOCENT, PLATEFORME], services=[PLATEFORME])  # tous « connus » : seul R9 peut parler
    m.traiter(ev(T0, "address_flagged", {"flagged": SIGNALEE, "level": "hold", "category": "scam_report", "expires_at": T0 + 10**6}))
    m.traiter(ev(T0 + 10, "token_transfer", {"from": SIGNALEE, "to": MULE, "token": A, "amount": str(40 * 10**21)}, seq=2))
    m.traiter(ev(T0 + 20, "token_transfer", {"from": SIGNALEE, "to": PLATEFORME, "token": A, "amount": str(59 * 10**21)}, seq=3))
    m.traiter(ev(T0 + 30, "token_transfer", {"from": SIGNALEE, "to": INNOCENT, "token": A, "amount": str(10**16)}, seq=4))  # dusting : 0,01
    return m


def test_mule_freinee():
    a = moteur().traiter(prop(1, MULE, T0 + 3600))
    assert a and a["level"] == "step_up" and a["reasons"][0]["code"] == "TAINTED_FUNDS" and "40%" in a["reasons"][0]["detail"]


def test_dusting_ignore():
    assert moteur().traiter(prop(2, INNOCENT, T0 + 3600)) is None


def test_service_connu_jamais_teinte():
    assert moteur().traiter(prop(3, PLATEFORME, T0 + 3600)) is None


def test_un_seul_intermediaire():
    m = moteur()
    m.traiter(ev(T0 + 40, "token_transfer", {"from": MULE, "to": INNOCENT, "token": A, "amount": str(40 * 10**21)}, seq=5))
    assert m.traiter(prop(4, INNOCENT, T0 + 3600)) is None  # la mule n'est pas « signalée » : pas de 2e saut


def test_teinte_expire():
    assert moteur().traiter(prop(5, MULE, T0 + 8 * 86400)) is None


def test_echantillon_reel_du_relais_de_timeo():
    """T9 : sortie réelle du relais (shared/echantillons/tracage.*) : mule freinée, innocent « dusté » et plateforme ignorés."""
    import json
    from pathlib import Path
    from score.moteur import charger_services
    ech = Path(__file__).resolve().parents[2] / "shared" / "echantillons"
    roles = json.loads((ech / "tracage.roles.json").read_text())
    services = charger_services(Path(__file__).resolve().parents[2] / "shared" / "services-connus.json")
    assert roles["known_service"] in services
    m = Moteur(carnet=[roles["innocent_dusted"], roles["known_service"]] + roles["mules"], services=services)  # tous connus : seul R9 parle
    niveaux, codes = {}, {}
    for l in (ech / "tracage.events.jsonl").read_text().splitlines():
        a = m.traiter(json.loads(l))
        if a:
            niveaux[a["payment_id"]] = a["level"]
            codes[a["payment_id"]] = [r["code"] for r in a["reasons"]]
    assert niveaux.get(0) == "step_up" and codes[0][0] == "TAINTED_FUNDS"  # la mule (26 % des sorties)
    assert 1 not in niveaux and 2 not in niveaux  # innocent (0,01 mUSD) et plateforme : rien
