"""Agent autonome : testé sans réseau (simulation, modèle et Web remplacés par des faux)."""
import json

from agent import agent as module
from agent.agent import Agent, plancher
from score import regles
from score.moteur import Moteur

T0 = 1_760_000_000  # un lundi à 10h53, heure de Paris : aucune règle d'horaire
CONNU, INCONNU, AGENT = "0x" + "c0" * 20, "0x" + "ab" * 20, "0x" + "a9" * 20
PORTEFEUILLE, JETON = "0x" + "aa" * 20, "0x" + "bb" * 20


def proposition(to, pid=1, montant=1_000):
    return {"type": "payment_proposed", "timestamp": T0, "tx_hash": "0x" + "11" * 32, "address": PORTEFEUILLE,
            "data": {"payment_id": pid, "to": to, "token": JETON, "amount": str(montant * regles.UNITE), "memo": "Facture",
                     "proposer": "0x" + "01" * 20}}


def lancer(tmp_path, monkeypatch, to, mode="protection", part=0.01, modele=None, web=None, montant=1_000):
    monkeypatch.setattr(module, "simuler", lambda *a: {"part_de_la_tresorerie": part, "transfert_reussirait": True})
    sorties = {n: tmp_path / f"{n}.jsonl" for n in ("alertes", "actions", "decisions", "flags")}
    a = Agent(Moteur([CONNU]), mode, AGENT if mode == "cosignataire" else None, "http://noeud.test", raisonner=modele is not None,
              web=web is not None, sortie_alertes=sorties["alertes"], sortie_actions=sorties["actions"],
              sortie_decisions=sorties["decisions"], sortie_flags=sorties["flags"])
    if modele is not None:
        monkeypatch.setattr(a, "avis_du_modele", lambda dossier: modele)
    if web is not None:
        monkeypatch.setattr(a, "lire_le_web", lambda adresse: web)
    avis = a.traiter(proposition(to, montant=montant))
    a.file_web.shutdown(wait=True)
    lire = lambda n: [json.loads(l) for l in sorties[n].read_text(encoding="utf-8").splitlines()] if sorties[n].exists() else []
    return avis, {n: lire(n) for n in sorties}


def test_cosignataire_signe_un_paiement_sans_histoire(tmp_path, monkeypatch):
    avis, f = lancer(tmp_path, monkeypatch, CONNU, "cosignataire")
    assert avis == "laisser" and f["alertes"] == []
    assert [(x["action"], x["by"], x["payment_id"]) for x in f["actions"]] == [("approve", AGENT, 1)]


def test_cosignataire_ne_signe_pas_et_freine_un_destinataire_inconnu(tmp_path, monkeypatch):
    avis, f = lancer(tmp_path, monkeypatch, INCONNU, "cosignataire")
    assert avis == "freiner" and f["actions"] == []
    assert f["alertes"][0]["level"] == "step_up" and "ne signe pas" in f["alertes"][0]["explanation"]


def test_protection_n_ecrit_jamais_de_signature(tmp_path, monkeypatch):
    _, f = lancer(tmp_path, monkeypatch, CONNU, "protection")
    assert f["actions"] == [] and f["alertes"] == []


def test_la_simulation_refuse_un_paiement_qui_vide_la_tresorerie(tmp_path, monkeypatch):
    avis, f = lancer(tmp_path, monkeypatch, CONNU, "cosignataire", part=0.62)
    assert avis == "refuser" and f["actions"] == []
    assert f["alertes"][0]["level"] == "hold" and f["alertes"][0]["reasons"][0]["code"] == "SIM_TREASURY_SHARE"


def test_le_modele_peut_durcir_mais_jamais_adoucir(tmp_path, monkeypatch):
    dur = {"avis": "refuser", "confiance": 0.9, "explication": "Le libellé contredit le destinataire.", "modele": "faux"}
    avis, f = lancer(tmp_path, monkeypatch, CONNU, modele=dur)
    assert avis == "refuser" and f["alertes"][0]["reasons"][0]["code"] == "AGENT_JUDGMENT"
    doux = {"avis": "laisser", "confiance": 0.99, "explication": "Tout va bien.", "modele": "faux"}
    avis, f = lancer(tmp_path / "..", monkeypatch, INCONNU, modele=doux)
    assert avis == "freiner"  # les règles disaient freiner : le modèle ne peut pas lever le frein


def test_le_web_accuse_le_destinataire_l_agent_refuse_apres_coup(tmp_path, monkeypatch):
    accusation = {"address": INCONNU, "category": "scam_report", "sources_count": 2, "quote": "cette adresse a volé nos fonds",
                  "source_url": "https://chainabuse.com/report/1", "level": "hold"}
    web = {"pages_lues": 2, "accusations_confirmees": [accusation], "accusations_a_confirmer": []}
    _, f = lancer(tmp_path, monkeypatch, INCONNU, "cosignataire", web=web)
    assert [x["level"] for x in f["alertes"]] == ["step_up", "hold"]  # d'abord freiné, puis refusé une fois le Web lu
    assert f["alertes"][1]["reasons"][0]["code"] == "WEB_ACCUSATION" and f["actions"] == []
    assert [d["phase"] for d in f["decisions"]] == ["immédiate", "après Web"]


def test_un_niveau_ne_redescend_jamais_et_chaque_decision_garde_son_dossier(tmp_path, monkeypatch):
    web = {"pages_lues": 1, "accusations_confirmees": [], "accusations_a_confirmer": []}
    _, f = lancer(tmp_path, monkeypatch, INCONNU, web=web)
    assert len(f["alertes"]) == 1  # le Web ne trouve rien : pas de seconde alerte, et le frein reste
    for d in f["decisions"]:
        assert d["dossier"]["simulation"] and d["dossier"]["regles"]["niveau"] == "step_up" and d["plancher_sans_modele"] == "freiner"


def test_plancher_sans_rien_laisse_passer():
    assert plancher(None, None, None) == ("laisser", [])


def test_au_demarrage_en_direct_les_vieux_paiements_ne_sont_pas_redecides(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "simuler", lambda *a: {"part_de_la_tresorerie": 0.01, "transfert_reussirait": True})
    a = Agent(Moteur([CONNU]), "cosignataire", AGENT, "http://noeud.test", raisonner=False, sortie_actions=tmp_path / "actions.jsonl", fenetre_s=600)
    assert a.traiter(proposition(CONNU)) is None and not (tmp_path / "actions.jsonl").exists()  # T0 est vieux de plusieurs mois


def test_cosignataire_ne_signe_pas_si_simulation_indisponible(tmp_path, monkeypatch):
    def indisponible(*a):
        raise TimeoutError("faux échec RPC")
    monkeypatch.setattr(module, "simuler", indisponible)
    actions, alertes = tmp_path / "actions.jsonl", tmp_path / "alertes.jsonl"
    agent = Agent(Moteur([CONNU]), "cosignataire", AGENT, "http://noeud.test", raisonner=False,
                  sortie_actions=actions, sortie_alertes=alertes)
    try:
        assert agent.traiter(proposition(CONNU)) == "freiner"
        assert not actions.exists()
        assert "SIM_UNAVAILABLE" in alertes.read_text(encoding="utf-8")
    finally:
        agent.file_web.shutdown(wait=True)


def test_simulation_detecte_un_retour_erc20_false(monkeypatch):
    class Reponse:
        def raise_for_status(self): pass
        def json(self):
            return [{"id": i, "result": "0x" + format(0 if i == 3 else 100000, "064x")} for i in range(4)]
    import httpx
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Reponse())
    sim = module.simuler("http://noeud.test", PORTEFEUILLE, JETON, CONNU, 100)
    assert sim["transfert_reussirait"] is False
    assert plancher(None, sim, None)[0] == "freiner"
