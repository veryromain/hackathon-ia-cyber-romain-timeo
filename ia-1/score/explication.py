"""Explication d'une alerte pour un signataire non expert (R3), rédigée par Bedrock.

Principe « trust but verify » : le modèle reçoit UNIQUEMENT les faits établis par le moteur (raisons, montant,
destinataire, libellé, niveau) et doit les reformuler en clair. Il ne décide de rien. Sa sortie est vérifiée :
pas d'adresse ni de montant inventés, longueur bornée ; sinon on garde le texte à trous du moteur.
"""
import re
import time

from .regles import fmt

CONSIGNE = """Tu rédiges, pour un signataire d'un portefeuille de trésorerie qui n'est pas expert en sécurité,
l'explication d'une alerte émise par un garde antifraude. Règles strictes :
- utilise UNIQUEMENT les faits fournis, n'ajoute aucun chiffre, aucune adresse, aucune hypothèse sur l'identité du destinataire ;
- 2 à 4 phrases, en français simple, sans jargon ni code, sans liste ;
- première phrase : ce qui est inhabituel ; dernière phrase : ce que le signataire doit faire maintenant
  (pour une mise en attente : vérifier la demande par un autre canal, par exemple un appel au demandeur sur son numéro
  habituel, avant de signer ; pour une signature en plus : un signataire qui n'a pas proposé le paiement vérifie avant de signer) ;
- ton calme et factuel : pas « fraude », mais « inhabituel », « à vérifier », sauf si une raison dit que le destinataire
  est signalé sur le Web, auquel cas dis-le clairement.
Réponds par le texte seul."""

NIVEAU = {"hold": "mise en attente : délai d'attente, et il faut une signature de plus que d'habitude (pas une « seconde » signature)",
          "step_up": "il faut une signature de plus que d'habitude (pas une « seconde » signature)"}


def faits(alerte: dict, paiement: dict) -> str:
    lignes = [
        f"Niveau décidé par le garde : {NIVEAU.get(alerte['level'], alerte['level'])}.",
        f"Montant : {fmt(int(paiement['amount']))}.",
        f"Libellé du paiement : « {paiement.get('memo') or '(aucun)'} ».",
        f"Destinataire : {paiement['to'][:6]}…{paiement['to'][-4:]}.",
        "Raisons relevées :",
    ] + [f"- {r['detail']}" for r in alerte["reasons"]]
    return "\n".join(lignes)


def verifier(texte: str, paiement: dict) -> bool:
    if not texte or len(texte) > 900 or texte.count("\n") > 4:
        return False
    adresses = set(re.findall(r"0x[a-fA-F0-9]{6,}", texte))
    if adresses - {paiement["to"][:6]}:  # une adresse complète ou étrangère : refusé
        return False
    return True


def _appel(system: str, texte: str) -> str:
    from commun import bedrock
    return bedrock.texte_de(bedrock.converse(system, texte, max_tokens=400)).strip()


PAUSE_APRES_PANNE_S = 60
_panne_jusqua = 0.0


def expliquer(alerte: dict, paiement: dict, secours: str) -> str:
    """Renvoie l'explication Bedrock si elle passe la vérification, sinon le texte de secours du moteur."""
    global _panne_jusqua
    if time.time() < _panne_jusqua:
        return secours  # Bedrock en panne il y a moins d'une minute : on n'attend pas, l'alerte doit partir vite
    try:
        texte = _appel(CONSIGNE, faits(alerte, paiement))
    except Exception:
        _panne_jusqua = time.time() + PAUSE_APRES_PANNE_S
        return secours  # réseau coupé, modèle refusé… : l'alerte part quand même, avec le texte à trous
    return texte if verifier(texte, paiement) else secours
