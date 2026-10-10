"""Le tableau de bord s'affiche sans erreur sur la démo et montre les bons chiffres."""
import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

ICI = Path(__file__).resolve().parents[1]


def test_dashboard_demo():
    os.environ["BREAKER_DOSSIER"] = str(ICI / "dashboard" / "demo")
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    assert not at.exception
    m = {x.label: x.value for x in at.metric}
    assert m["🛑 Mis en attente"] == "3" and m["✋ Signature en plus"] == "1"
    assert m["Montant protégé"].startswith("292 500")
    assert any("GELÉ" in e.value for e in at.error)


def test_dashboard_dossier_vide(tmp_path):
    os.environ["BREAKER_DOSSIER"] = str(tmp_path)
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    assert not at.exception


def test_boutons_ecrivent_les_actions(tmp_path):
    """R5b : un clic écrit une ligne au format de shared/format-actions.md ; contester écrit dans flags.jsonl."""
    import json
    import shutil
    d = tmp_path / "live"
    shutil.copytree(ICI / "dashboard" / "demo", d)
    lignes = (d / "events.jsonl").read_text().splitlines()
    (d / "events.jsonl").write_text("\n".join(lignes[:-1]) + "\n")  # on retire l'annulation du paiement 6 : il reste « en cours »
    dep = tmp_path / "dep.json"
    dep.write_text(json.dumps({"owners": ["0x" + "a" * 40, "0x" + "b" * 40]}))
    os.environ["BREAKER_DOSSIER"], os.environ["BREAKER_DEPLOIEMENT"] = str(d), str(dep)
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    assert not at.exception
    at.button(key="no6").click().run()  # annuler le paiement 6
    at.button(key="ct0x6253540229bdcc8ae009fe075005a3fa5137c352").click().run()  # contester le signalement
    actions = [json.loads(l) for l in (d / "actions.jsonl").read_text().splitlines()]
    assert actions[0]["action"] == "cancel" and actions[0]["payment_id"] == 6 and actions[0]["by"] == "0x" + "a" * 40
    assert json.loads((d / "flags.jsonl").read_text().splitlines()[-1]) == {"address": "0x6253540229bdcc8ae009fe075005a3fa5137c352", "remove": True}
    assert not at.exception
    del os.environ["BREAKER_DEPLOIEMENT"]
