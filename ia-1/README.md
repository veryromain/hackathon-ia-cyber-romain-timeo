# ia-1 : détection, oracle Web2 → Web3, dashboard (Romain)

## Installation (Mac)
```bash
cd ia-1
~/.local/bin/uv venv --python 3.12 .venv && ~/.local/bin/uv pip install -p .venv -r requirements.txt
```
Configuration Bedrock : `.env` à la racine du repo (voir `shared/aws-bedrock.md`). **Le Wi-Fi de l'école bloque Bedrock : partage de connexion.**

## R1 — Moteur de score ✅
Lit `events.jsonl` (format : `shared/format-evenements.md`) et écrit `alerts.jsonl`.
```bash
.venv/bin/python -m score.moteur --events ../shared/echantillons/events.exemple.jsonl --out alerts.jsonl --carnet config/carnet.exemple.json
.venv/bin/python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl --suivre   # en direct, avec le relais de Timéo
.venv/bin/python eval/comparer.py alerts.jsonl ../shared/echantillons/labels.exemple.jsonl            # évaluation
.venv/bin/python -m pytest -q tests
```

**Règles (`score/regles.py`)** — chaque raison a un poids, combinés en « OU bruité » :

| Code | Déclencheur | Poids |
|---|---|---|
| `FLAGGED_ADDRESS` | destinataire inscrit au registre par l'oracle, non expiré | 0,90 (hold) / 0,50 (step_up) |
| `NEW_RECIPIENT` | jamais payé (le carnet d'adresses du client évite le démarrage à froid) | 0,35 |
| `AMOUNT_OUTLIER` | ≥ 3 × le paiement médian exécuté | 0,15 × log2(ratio), max 0,6 |
| `BURST` | autre proposition dans les 10 dernières minutes | 0,40 |
| `URGENCY_MEMO` | libellé pressant ou secret (« urgent », « confidentiel », « nouveau RIB »…) | 0,30 |
| `OFF_HOURS` | hors 7h–20h (Paris) ou week-end | 0,15 |
| `RECENT_OWNER_CHANGE` | signataire remplacé dans les 7 jours | 0,30 |
| `THRESHOLD_LOWERED` | seuil de signatures abaissé dans les 7 jours | 0,50 |

Niveaux : score ≥ 0,70 → `hold` ; ≥ 0,30 → `step_up` ; sinon rien.
**Résultat sur l'exemple de Timéo :** 3/3 fraudes mises en attente, 0/3 faux positif, le nouveau fournisseur légitime en `step_up`.

**Limites connues :** poids réglés à la main (à recalibrer sur le trafic d'entraînement de T4, R2) ; l'explication est un texte à trous (Bedrock en R3).

## À venir
R2 modèle d'anomalie · R8 oracle · R3/R4 Bedrock · R5 dashboard · R6 évaluation · R9 traçage des fonds
