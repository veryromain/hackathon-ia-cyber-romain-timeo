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

## Variante : clé d'API Bedrock (méthode de Timéo, ajoutée le 10/10 à 15:35)
Timéo a reçu une **clé d'API Bedrock de courte durée** (elle commence par `bedrock-api-key-`) au lieu d'identifiants CLI.
1. Copier `.env.example` en `.env` à la racine du repo et coller la clé après `AWS_BEARER_TOKEN_BEDROCK=`. `.env` est ignoré par Git.
2. boto3 et l'AWS CLI lisent cette variable d'environnement tout seuls : pas de profil à configurer. En Python, charger `.env` (`python-dotenv`) puis `boto3.client("bedrock-runtime", region_name="us-west-2")`.
3. Test en ligne de commande (Git Bash) : `set -a; . ./.env; set +a` puis `aws bedrock-runtime converse --region us-west-2 --model-id us.anthropic.claude-sonnet-5-5 --messages '[{"role":"user","content":[{"text":"OK ?"}]}]'`.

- **Durée de vie :** la clé de Timéo a été émise le 10/10 à 15:28 (heure de Paris) pour 12 heures au plus, donc **elle expire vers 03:28 dimanche**, avant le rendu. Il faudra en générer une nouvelle.
- **Non validée :** testée à 15:33 depuis le Wi-Fi de l'école, l'appel échoue avec « Connection was closed », le blocage réseau décrit plus haut. À retester en partage de connexion.

### Résultat avec la clé de Timéo (2026-10-10 15:37, en partage de connexion)
- **Bedrock répond.** Appel réel réussi avec `us.anthropic.claude-opus-5-5` et avec `us.amazon.nova-lite-v1:0`.
- **Refusés avec cette clé** (`AccessDeniedException`, « private marketplace eligibility ») : `us.` et `global.anthropic.claude-sonnet-5-5`, `us.` et `global.anthropic.claude-haiku-5-5`. Romain, lui, y a accès par son rôle. Le message d'AWS suggère de réessayer après quelques minutes.
- Le `.env` de Timéo pointe donc sur `us.anthropic.claude-opus-5-5`. **Le code doit lire le modèle dans `BEDROCK_MODEL_ID`**, pas l'écrire en dur, pour tourner chez les deux.
