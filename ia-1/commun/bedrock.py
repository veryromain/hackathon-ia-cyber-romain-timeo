"""Appel Bedrock commun à l'oracle et aux explications (R3/R4).

Règles de l'équipe : Opus 5.5, puis Fable 5.1, jamais Sonnet. Les deux premiers sont bloqués par le marketplace
privé de l'événement : repli automatique sur Opus 4.8. Le Wi-Fi de l'école bloque Bedrock (partage de connexion).
"""
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
MODELES_REPLI = ["us.anthropic.claude-opus-5-5", "global.anthropic.claude-opus-5-5",
                 "us.anthropic.claude-fable-5-1", "global.anthropic.claude-fable-5-1",
                 "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-5-20251101-v1:0"]
_client = None
modele_utilise = None


def client():
    global _client
    if _client is None:
        import boto3
        from dotenv import load_dotenv
        load_dotenv(RACINE / ".env")
        session = boto3.Session(profile_name=os.getenv("AWS_PROFILE") or None,
                                region_name=os.getenv("AWS_REGION", "us-west-2"))
        _client = session.client("bedrock-runtime")
    return _client


def modeles():
    prefere = os.getenv("BEDROCK_MODEL_ID")
    return [m for m in dict.fromkeys([prefere] + MODELES_REPLI) if m and "sonnet" not in m.lower()]


def converse(system: str, texte: str, outil: dict | None = None, max_tokens: int = 1200):
    """Renvoie le contenu de la réponse (liste de blocs). Essaie les modèles dans l'ordre ; sans température si refusée."""
    global modele_utilise
    c = client()
    params = dict(system=[{"text": system}], messages=[{"role": "user", "content": [{"text": texte}]}])
    if outil:
        params["toolConfig"] = {"tools": [outil], "toolChoice": {"tool": {"name": outil["toolSpec"]["name"]}}}
    erreurs = {}
    for m in modeles():
        for reglages in ({"maxTokens": max_tokens, "temperature": 0}, {"maxTokens": max_tokens}):
            try:
                r = c.converse(modelId=m, inferenceConfig=reglages, **params)
                modele_utilise = m
                return r["output"]["message"]["content"]
            except c.exceptions.ValidationException as err:
                if "temperature" in str(err):
                    continue  # ce modèle refuse le réglage : on réessaie sans
                erreurs[m] = str(err)[:120]
                break
            except c.exceptions.AccessDeniedException as err:
                erreurs[m] = str(err)[:120]
                break
    raise RuntimeError(f"aucun modèle Bedrock accessible : {erreurs}")


def texte_de(contenu) -> str:
    return "".join(b.get("text", "") for b in contenu)


def outil_de(contenu) -> dict:
    for b in contenu:
        if "toolUse" in b:
            return b["toolUse"]["input"]
    return {}
