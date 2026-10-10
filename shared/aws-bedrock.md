# AWS Bedrock : accès et usage

> Aucun identifiant dans ce fichier ni dans le repo. Chacun récupère les siens depuis Workshop Studio.

## État (vérifié le 10/10 à 14:45 par Romain)
- Compte de l'événement : rôle `WSParticipantRole`, région **us-west-2**.
- Modèle validé par un appel réel : **`us.anthropic.claude-sonnet-5-5`** (API `converse`). Il connaît le délai DORA de 4 h / 24 h.
- Aussi disponibles : `us.anthropic.claude-opus-5-5`, `us.anthropic.claude-haiku-5-5`, ainsi que les versions `global.*`.

## ⚠️ Le Wi-Fi de l'école bloque Bedrock
Toutes les adresses `bedrock*.amazonaws.com` sont coupées sur le réseau du hackathon (erreur TLS / « Connection was closed »). Le reste d'AWS passe.
→ **Passer sur le partage de connexion du téléphone** pour tout ce qui appelle Bedrock. Le signaler aux organisateurs.
→ Plan B : AWS CloudShell (dans la console) ou rapport par template sans LLM.

## Se connecter (à refaire quand les identifiants expirent)
1. Workshop Studio → page de l'événement → **Get AWS CLI credentials** → onglet *Mac or Linux* (ou *Windows* pour Timéo) → copier.
2. Ranger les identifiants dans `~/.aws/credentials` sous un profil `[hackathon]`, avec `region = us-west-2` dans `~/.aws/config`. **Jamais dans le repo ni dans un message.**
3. Vérifier : `aws sts get-caller-identity --profile hackathon`.

## Appel minimal en Python (boto3)
```python
import boto3
br = boto3.Session(profile_name="hackathon", region_name="us-west-2").client("bedrock-runtime")
r = br.converse(modelId="us.anthropic.claude-sonnet-5-5",
                messages=[{"role": "user", "content": [{"text": "Bonjour"}]}],
                inferenceConfig={"maxTokens": 300})
print(r["output"]["message"]["content"][0]["text"])
```
