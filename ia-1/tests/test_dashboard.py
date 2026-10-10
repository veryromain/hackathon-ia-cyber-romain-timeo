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


def test_bouton_vraie_fausse_alerte(tmp_path):
    """P6 : le jugement d'un signataire est enregistré et la précision jugée s'affiche."""
    import json
    import shutil
    d = tmp_path / "live"
    shutil.copytree(ICI / "dashboard" / "demo", d)
    dep = tmp_path / "dep.json"
    dep.write_text(json.dumps({"owners": ["0x" + "a" * 40]}))
    os.environ["BREAKER_DOSSIER"], os.environ["BREAKER_DEPLOIEMENT"] = str(d), str(dep)
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    at.button(key="v4").click().run()
    at.button(key="f3").click().run()
    at.run()  # l'indicateur se recalcule au rendu suivant (la page se rafraîchit toutes les 2 s)
    r = [json.loads(l) for l in (d / "retours.jsonl").read_text().splitlines()]
    assert [(x["payment_id"], x["verdict"]) for x in r] == [(4, "vraie"), (3, "fausse")]
    assert {m.label: m.value for m in at.metric}["Précision jugée"] == "50%"
    assert not at.exception
    del os.environ["BREAKER_DEPLOIEMENT"]


def test_signer_exige_de_retaper_la_fin_de_l_adresse(tmp_path):
    """Idée 3 : « ce que vous signez vraiment » — sans les 4 bons caractères, le bouton Valider est désactivé."""
    import json
    import shutil
    d = tmp_path / "live"
    shutil.copytree(ICI / "dashboard" / "demo", d)
    lignes = (d / "events.jsonl").read_text().splitlines()
    (d / "events.jsonl").write_text("\n".join(lignes[:-1]) + "\n")  # paiement 6 reste en cours
    dep = tmp_path / "dep.json"
    dep.write_text(json.dumps({"owners": ["0x" + "a" * 40]}))
    os.environ["BREAKER_DOSSIER"], os.environ["BREAKER_DEPLOIEMENT"] = str(d), str(dep)
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    assert at.button(key="ok6").disabled
    at.text_input(key="chk6").set_value("zzzz").run()
    assert at.button(key="ok6").disabled
    at.text_input(key="chk6").set_value("c352").run()  # 0x6253…c352
    assert not at.button(key="ok6").disabled
    at.button(key="ok6").click().run()
    assert json.loads((d / "actions.jsonl").read_text().splitlines()[0])["action"] == "approve"
    del os.environ["BREAKER_DEPLOIEMENT"]


def test_signaler_pour_tous_apres_annulation(tmp_path):
    """Idée 4 : immunité collective — une fraude annulée devient un signalement avec la transaction pour preuve."""
    import json
    import shutil
    d = tmp_path / "live"
    shutil.copytree(ICI / "dashboard" / "demo", d)
    (d / "flags.jsonl").write_text("")  # aucune adresse encore signalée
    dep = tmp_path / "dep.json"
    dep.write_text(json.dumps({"owners": ["0x" + "a" * 40]}))
    os.environ["BREAKER_DOSSIER"], os.environ["BREAKER_DEPLOIEMENT"] = str(d), str(dep)
    at = AppTest.from_file(str(ICI / "dashboard" / "app.py"), default_timeout=30).run()
    at.button(key="sig4").click().run()  # paiement 4, annulé dans l'exemple
    f = json.loads((d / "flags.jsonl").read_text().splitlines()[-1])
    assert f["address"] == "0xe98106af12431fa824188a4d4a9e1f5027dedf5a" and f["level"] == "hold" and "annulé" in f["quote"]
    assert set(f) >= {"address", "level", "category", "confidence", "sources_count", "source_url", "quote", "evidence_hash", "expires_at"}
    del os.environ["BREAKER_DEPLOIEMENT"]
