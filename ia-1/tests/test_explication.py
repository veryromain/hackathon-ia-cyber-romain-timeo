"""Tests hors ligne de R3 : les garde-fous autour de l'explication Bedrock."""
import score.explication as E

P = {"amount": "95000000000000000000000", "memo": "URGENT confidentiel", "to": "0xe98106af12431fa824188a4d4a9e1f5027dedf5a"}
A = {"level": "hold", "score": 0.9, "reasons": [{"code": "NEW_RECIPIENT", "detail": "premier paiement vers cette adresse"}]}


def test_faits_contiennent_niveau_montant_et_raisons():
    f = E.faits(A, P)
    assert "mise en attente" in f and "95 000 mUSD" in f and "premier paiement" in f and "0xe981…df5a" in f


def test_texte_bedrock_valide_est_garde(monkeypatch):
    monkeypatch.setattr(E, "_appel", lambda s, t: "Ce paiement est inhabituel. Vérifiez par un autre canal avant de signer.")
    assert E.expliquer(A, P, "secours").startswith("Ce paiement est inhabituel")


def test_adresse_inventee_rejetee(monkeypatch):
    monkeypatch.setattr(E, "_appel", lambda s, t: "Le destinataire 0xdeadbeefcafe est un escroc connu.")
    assert E.expliquer(A, P, "secours") == "secours"


def test_texte_trop_long_rejete(monkeypatch):
    monkeypatch.setattr(E, "_appel", lambda s, t: "bla " * 300)
    assert E.expliquer(A, P, "secours") == "secours"


def test_panne_bedrock_repli_silencieux(monkeypatch):
    def plante(s, t):
        raise RuntimeError("réseau")
    monkeypatch.setattr(E, "_appel", plante)
    assert E.expliquer(A, P, "secours") == "secours"


def test_apres_une_panne_on_n_attend_plus(monkeypatch):
    appels = []

    def plante(s, t):
        appels.append(1)
        raise RuntimeError("réseau")
    monkeypatch.setattr(E, "_appel", plante)
    E._panne_jusqua = 0
    E.expliquer(A, P, "secours")
    E.expliquer(A, P, "secours")
    assert len(appels) == 1  # le second appel est sauté pendant la pause
    E._panne_jusqua = 0
