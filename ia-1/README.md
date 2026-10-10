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

## R2 — Modèle d'anomalie ✅
Isolation Forest appris sur le **trafic normal** de Timéo (`shared/donnees/train`), en complément des règles : raison `ANOMALY_MODEL` (0,25 au-delà du 99e centile de l'entraînement, 0,40 au-delà du maximum).
```bash
.venv/bin/python -m score.anomalie --events ../shared/donnees/train.events.jsonl --carnet ../shared/donnees/carnet.json --sortie modeles/anomalie.joblib
.venv/bin/python -m score.moteur ... --modele modeles/anomalie.joblib
.venv/bin/python -m eval.evaluer_donnees --modele    # évaluation train → test
```
9 caractéristiques (montant, écart à l'habitude du destinataire, heure, week-end, rythme, rafale, changement de signataire, libellé, répétition). **La nouveauté du destinataire est volontairement exclue** (déjà comptée par `NEW_RECIPIENT` ; essai sur train : +50 % de nouveaux fournisseurs mis en attente).
**Test de Timéo :** fraudes arrêtées 63 % → **69 %**, montants en attente 89 % → **94 %**, faux `hold` **inchangés (0,9 %)**.

## R8a — Oracle Web2 → Web3 (cœur) ✅
```bash
.venv/bin/python -m oracle.oracle oracle/corpus_demo/*.html --out ../shared/flags.jsonl     # Bedrock (partage de connexion !)
.venv/bin/python -m oracle.oracle oracle/corpus_demo/*.html --out flags.jsonl --sans-llm      # repli par mots-clés
```
Page → texte visible (le **texte caché est écarté** : vecteur d'injection) → adresses `0x…` → Bedrock (sortie forcée par un outil à schéma fixe, température 0, consigne anti-injection) → **citation vérifiée mot pour mot par le code** → `flags.jsonl` (acceptés, format de Timéo) + `flags-rejetes.jsonl` (rejetés, avec la raison : `quote_not_found`, `mention`, `denial`, `low_confidence`, `not_analysed`).
Seuils : confiance ≥ 0,6 pour signaler, ≥ 0,8 pour `hold`. Expiration 30 jours.
**Modèles :** `BEDROCK_MODEL_ID`, puis repli automatique (Sonnet 4.5, Opus 4.5…) si l'accès est refusé.

**Corpus de démo (`oracle/corpus_demo/`, 6 pages) — résultat Bedrock, stable sur 3 passages :**

| Page | Piège | Résultat |
|---|---|---|
| 01 forum | vraie accusation + adresse de dons sur la même page | arnaque signalée `hold` (0,9-0,95) ; dons rejetés (`mention`) ✅ |
| 02 démenti | « n'est pas une arnaque » | rejeté (`denial`) ✅ |
| 03 rapport | adresse de dons | rejeté (`mention`) ✅ |
| 04 injection cachée | ordre en `display:none` | texte écarté avant lecture ✅ |
| 05 accusation retirée | « c'était une erreur » | rejeté (`denial`) ✅ — **le repli par mots-clés se fait piéger** |
| 06 injection visible | « ordre de la police », adresse d'un concurrent | rejeté (`mention`) ✅ |

Tests hors ligne (`tests/test_oracle.py`) : hallucination de citation rejetée, adresse inventée ignorée, confiance faible rejetée, format `flags.jsonl`.

## À venir
R2 modèle d'anomalie · R8b corpus · R8c croisement des sources · R3/R4 Bedrock · R5 dashboard · R6 évaluation · R9 traçage des fonds
