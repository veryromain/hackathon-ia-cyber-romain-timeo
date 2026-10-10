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
