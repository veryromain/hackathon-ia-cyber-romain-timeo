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

## R1 bis — Corrections après le jeu de généralisation (10/10, 20:00) ✅
Guidées par la **forme** des fraudes jamais vues, sans regarder leurs chiffres ; mesure finale sur un 4ᵉ jeu de Timéo. Nouvelles raisons : `NEW_OWNER_LARGE_PAYMENT` (clé < 7 j + gros montant vers un inconnu → hold), `NEW_OWNER_APPROVES` (une clé neuve apporte la signature manquante à un paiement déjà signalé vers un inconnu → re-notation), `RECENT_RECIPIENT` / `RECENT_RECIPIENT_SPIKE` (destinataire récent = < 30 j et < 3 paiements ; > 5 × ce qu'il a reçu → hold), `DAILY_CAP_RECIPIENT` / `DAILY_CAP_RECENT` (cumul du jour : ≥ 3 propositions vers le même destinataire à ≥ 5 × sa médiane, ou ≥ 3 adresses récentes au-dessus des gros paiements habituels), `AMOUNT_OUTLIER_EXTREME` (≥ 10 × l'habitude → hold seul).
**Jeu de test, règles + R2 :** fraudes arrêtées 69 → **80 %**, montants en attente 94 → **97 %**, faux `hold` 0,9 → 1,6 % (gros premiers paiements à de nouveaux fournisseurs : assumé, seuil réglable).

## R9 — Traçage des fonds (règle) ✅
Événement `token_transfer` (`from`, `to`, `token`, `amount`) : les sorties d'une adresse **signalée** teintent ses destinataires à hauteur de leur **part** des sorties. Raison `TAINTED_FUNDS` (0,50 → `step_up`) si part ≥ 10 %, 1 intermédiaire seulement, 7 jours, jamais pour une adresse de `shared/services-connus.json` (`--services`). Le dusting (0,01 mUSD) est ignoré. 6 tests, dont un sur la **sortie réelle du relais de Timéo** (`shared/echantillons/tracage.*`) : la mule qui a reçu 26 % des fonds est freinée, l'innocent « dusté » (0,01 mUSD) et la plateforme d'échange ne le sont pas. `--services ../shared/services-connus.json` (format de Timéo : `{"services": [{"address": …}]}`).

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

## R8b — Corpus de l'oracle et mesure ✅
```bash
.venv/bin/python -m oracle.corpus --graine 7 --n 40 --sortie oracle/corpus      # 40 pages, 63 adresses, moitié dev / moitié test
.venv/bin/python -m eval.evaluer_oracle --jeu test                                # Bedrock (partage de connexion)
.venv/bin/python -m eval.evaluer_oracle --jeu test --sans-llm                     # repli mots-clés, pour comparer
```
Pages écrites par **gabarits** (pas par un LLM, pour ne pas faire juger un corpus par la famille de modèles qui l'a écrit) : accusations FR/EN (arnaque, phishing, fraude au président, rug pull…), mentions (dons, contrats, tutoriels), **questions** (« c'est une arnaque ? »), **démentis et accusations retirées**, **injections visibles et cachées**, 1 à 3 adresses par page.

| Jeu test (20 pages, 35 adresses) | Bedrock (Opus 4.8) | Mots-clés |
|---|---|---|
| Précision | **100 %** | 67 % |
| Rappel | **100 %** | 36 % |
| Fausses accusations | **0 / 24** | 2 / 24 |

**Limite honnête :** des gabarits sont plus réguliers que le vrai Web (ironie, fautes, captures d'écran, langues variées). Le chiffre réel sera plus bas ; le corpus sert surtout à prouver que les pièges sont déjoués.

## R5 — Tableau de bord des signataires (v1) ✅
```bash
.venv/bin/python -m dashboard.preparer_demo                                   # démo hors chaîne (exemple de Timéo + moteur + oracle)
.venv/bin/streamlit run dashboard/app.py -- --dossier dashboard/demo
.venv/bin/streamlit run dashboard/app.py                                      # en direct : lit ../shared/ (relais de Timéo)
```
Rafraîchi toutes les 2 s. Indicateurs (proposés, en attente, signature en plus, **montant protégé**, adresses signalées), bandeau « portefeuille gelé », **paiements à examiner** (niveau, score, explication en clair, raisons avec liens vers l'explorateur Fuji), **adresses signalées par l'oracle** (citation, source, hash de preuve, expiration), journal de la chaîne. Écrit pour des signataires non experts.
Tests sans navigateur : `tests/test_dashboard.py` (AppTest de Streamlit).
**v2 (R5b) ✅ :** barre latérale « Je suis… » (signataire choisi parmi ceux du déploiement), boutons **✅ Valider / 🛑 Annuler** sur chaque paiement en cours, **🧊 Geler / 🔓 Dégeler**, **⚖️ Contester** un signalement, et un panneau « Actions des signataires » (en attente / fait avec lien / erreur). Le dashboard n'a aucune clé : un clic écrit dans `shared/actions.jsonl` (format : `shared/format-actions.md`), l'exécuteur signe. En local : `npx hardhat run ../ia-1/integration/actions.js --network localhost` (depuis `ia-2`). Sur Fuji : à intégrer dans le relais de Timéo. Contester écrit `{"address", "remove": true}` dans `flags.jsonl`, déjà géré par le relais. Testé en direct : annulation du paiement 4 et retrait du signalement, visibles sur la chaîne. **Depuis 19:53, le relais de Timéo lit `actions.jsonl` (local et Fuji)** : l'exécuteur `integration/actions.js` ne sert plus. Action `execute` (bouton ▶️) ajoutée par Timéo.

## R3 — Explication des alertes par Bedrock ✅
```bash
.venv/bin/python -m score.moteur ... --expliquer     # ajoute l'explication Bedrock ; sinon texte à trous
```
`score/explication.py` : le modèle reçoit **uniquement les faits du moteur** (niveau, montant, libellé, destinataire abrégé, raisons) et les reformule en 2 à 4 phrases pour un signataire non expert, avec l'action à faire. **Garde-fous vérifiés par le code** : aucune adresse étrangère ou complète, longueur bornée, sinon repli sur le texte à trous ; après une panne Bedrock, pause de 60 s sans appel pour que les alertes partent sans délai. Appel commun dans `commun/bedrock.py` (Opus 5.5 → Fable 5.1 → Opus 4.8, jamais Sonnet). 6 tests hors ligne. **Validé en direct** (Opus 4.8, ≈ 6 s par alerte, sous les 30 s du délai d'examen) : les 4 alertes de l'exemple reformulées sans fait inventé, avec l'action à faire.

## P6 — Bouton « vraie / fausse alerte » et précision jugée ✅
Sur chaque alerte, 👍 / 👎 par le signataire → `shared/retours.jsonl` ; indicateur **« Précision jugée »** en tête du tableau de bord. C'est la condition de vente décidée en B1 §4 : la précision se mesure chez le client (mode observation, rapport mensuel), pas sur nos données.

## P5 — Notification à chaque mise en attente (version minimale) ✅
`score/notifier.py`, option `--notifier` du moteur. Canaux cumulables, configurés dans `.env` (jamais dans Git) : **bannière macOS** (démo, sans réglage), **e-mail** (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIF_EMAIL_TO`), **Telegram** (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Trace dans `shared/notifications.jsonl`. Un canal en panne ne bloque jamais le moteur. 2 tests.

## R4 — Rapport d'incident ✅
```bash
.venv/bin/python -m score.rapport --dossier ../shared --sortie rapports/rapport-incident.md   # [--sans-llm]
```
`score/rapport.py` : les **faits sont établis par le code** à partir de `events.jsonl` / `alerts.jsonl` / `flags.jsonl` (paiements signalés, délai de signalement, montants tentés / sortis / protégés, gel, annulations, signalements Web), puis Bedrock rédige une **synthèse en 3 paragraphes à partir de ces faits seulement**, vérifiée (aucun montant hors des faits, aucun hash), sinon synthèse écrite par le code. Le rapport contient les preuves (hash de transaction) et la chronologie complète. Exemple généré sur la démo de ce soir : `rapports/rapport-demo-locale.md` (285 300 mUSD protégés, 0 sorti, signalement en ≤ 1 s). 5 tests.

## Sources publiques en lecture seule (décision B1 §3) ✅
`oracle/sources_publiques.py` : **OFAC** (adresses de la liste SDN, extraction publique 0xB10C, 120 adresses) et **ScamSniffer** (base publique de phishing, 2 530 adresses). Aucun scraping : listes publiées pour être réutilisées, citées, datées, expirées à 30 jours. Lues **hors chaîne** par le moteur (`--listes-publiques ../shared/listes-publiques.jsonl`, sans gas) ; `--publier N` en inscrit N par source au registre on-chain pour la démo. Testé sur Fuji : un paiement vers une adresse réellement sanctionnée est mis en attente, source officielle affichée. 2 tests.

## R8c — Croisement des sources de l'oracle ✅
Une adresse n'est publiée dans `flags.jsonl` que si la **somme des réputations des sources distinctes ≥ 0,8** (`oracle/sources.json` ; source inconnue = 0,4 ; identité = hôte de l'URL, ou nom du site dans le `<h1>` d'une page locale). Une source réputée suffit ; deux sites inconnus indépendants aussi ; **la même source répétée compte une fois**. Les accusations insuffisantes vont dans `flags-rejetes.jsonl` (`single_low_reputation_source`), en attente d'autres sources.

| Scénario (`oracle/corpus_demo/`) | Résultat |
|---|---|
| **Empoisonnement** : 3 pages du même « Blog anonyme » accusent le fournisseur CloudNova | ⏸ **en attente, non publiée** (1 source, poids 0,40) |
| Forum réputé (0,8) accuse l'arnaqueur | ✓ publiée |
| Même accusation sur 2 sites inconnus différents | ✓ publiée (2 sources) |

`--sans-croisement` pour l'ancien comportement. 4 tests.

## À venir
rien côté règles ; mesure finale sur le 4ᵉ jeu de Timéo
