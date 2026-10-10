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

**Règles (`score/regles.py`)** — 11 raisons explicables, poids combinés en « OU bruité ». Niveaux : `hold` ≥ 0,75 ; `step_up` ≥ 0,30.
`FLAGGED_ADDRESS`, `NEW_RECIPIENT`, `AMOUNT_OUTLIER` (vs historique du destinataire, ou 90e centile si inconnu), `BURST` (destinataires inconnus), `URGENCY_MEMO`, `PAYMENT_FRAUD_PATTERN`, `RAPID_REPEAT`, `OFF_HOURS` (nuit plus forte), `NEW_OWNER_PROPOSES`, `RECENT_OWNER_CHANGE`, `THRESHOLD_LOWERED`.

**Validation complète : [`shared/validation-R1.md`](../shared/validation-R1.md)** — sur 90 graines jamais vues : 99-100 % des fraudes freinées ou arrêtées, 0,2-0,4 % de mises en attente à tort. Banc d'essai : `.venv/bin/python -m eval.banc --graines 101-130`.

## À venir
R2 modèle d'anomalie · R8 oracle · R3/R4 Bedrock · R5 dashboard · R6 évaluation · R9 traçage des fonds
