# Démo de bout en bout en local (jalon de la phase 2) ✅

Testée sur le Mac de Romain le 10/10 vers 18h40 : chaîne Hardhat + contrats et relais de Timéo + moteur de score (avec R2) + oracle Bedrock + tableau de bord.

## Lancer (6 terminaux, dans cet ordre)
```bash
# 1. chaîne locale
cd ia-2 && npx hardhat node
# 2. contrats + carnet d'adresses de la démo (fournisseur habituel du scénario)
cd ia-2 && npm run deploy:local && npx hardhat run ../ia-1/integration/carnet.js --network localhost
#    (repartir de fichiers vides : rm -f ../shared/events.jsonl; : > ../shared/alerts.jsonl; : > ../shared/flags.jsonl)
# 3. relais (AVANT le moteur : il réécrit shared/events.jsonl)
cd ia-2 && npm run relay:local
# 4. moteur de score en direct, avec le modèle d'anomalie
cd ia-1 && .venv/bin/python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl \
  --carnet integration/carnet-local.json   # carnet avec 2 adresses pièges (idée 2)
  --modele modeles/anomalie.joblib --suivre --expliquer \
  --services ../shared/services-connus.json --client config/client.demo-samedi.json --notifier   # Bedrock (R3) ; R9 ; samedi ouvré ; bannière macOS à chaque hold
# 5. tableau de bord → http://localhost:8599
cd ia-1 && .venv/bin/streamlit run dashboard/app.py --server.port 8599
# (5b. l'exécuteur d'actions n'est plus nécessaire : le relais de Timéo lit shared/actions.jsonl depuis 19:53)
# 6a. scénario de Timéo : paiement normal + fraude en rafale + réponse d'un signataire
cd ia-2 && RESPOND=1 npm run scenario:local
# 6b. Web2 → Web3 : l'oracle signale une adresse (partage de connexion pour Bedrock !), puis on tente de la payer
cd ia-1 && .venv/bin/python -m oracle.oracle oracle/corpus_demo/01-forum-arnaque.html --out ../shared/flags.jsonl
cd ia-2 && ADRESSE=0x6253540229bdcc8ae009fe075005a3fa5137c352 npx hardhat run ../ia-1/integration/scenario_oracle.js --network localhost
```

## Résultats obtenus
| Étape | Sans moteur (1er passage) | Avec moteur + oracle |
|---|---|---|
| Paiement normal au fournisseur habituel (3 150 mUSD) | exécuté | **exécuté, aucune friction** |
| Fraude en rafale : 3 virements (280 500 mUSD) vers une adresse inconnue | **95 000 mUSD partis** (seul le plafond du contrat a freiné les 2 suivants) | **0 mUSD parti** : 3 × `hold` (score 0,93) inscrits sur la chaîne **dans la seconde** (délai disponible : 30 s) |
| Adresse signalée sur le Web par l'oracle, puis paiement banal de 4 800 mUSD | — | oracle : signalée `hold` (0,95), adresse de dons rejetée ; registre on-chain mis à jour ; paiement **bloqué** par le contrat (registre) **et** par le moteur (0,98) ; **0 mUSD parti** |

## Ce que l'intégration a révélé
- **Bug corrigé :** le modèle R2 enregistré par `python -m score.anomalie` ne se rechargeait pas dans le moteur (nom de module `__main__` dans la sauvegarde). Corrigé + test de non-régression.
- `OFF_HOURS` se déclenche pendant la démo du samedi (week-end) : c'est juste, mais à expliquer au jury (ou faire la démo filmée un jour de semaine, ou régler les heures ouvrées).
- `BURST` s'ajoute au paiement vers l'adresse signalée parce qu'il suit de près la rafale du scénario : artefact de démo, sans effet sur le résultat.
- Hardhat installé sur le Mac : `npm install` a demandé des réessais (réseau lent en partage de connexion).

## Après la démo : le rapport d'incident (R4)
```bash
cd ia-1 && .venv/bin/python -m score.rapport --dossier ../shared --sortie rapports/rapport-incident.md
```

## Traçage des fonds (R9/T9)
```bash
cd ia-2 && npm run tracing:local      # arnaqueur → 3 mules + plateforme + dusting, puis 3 paiements ; relais lancé à côté
# moteur avec la liste des services : ... --services ../shared/services-connus.json
```

## Rejouer la démo complète sur Fuji depuis le Mac de Romain (tableau de bord, actions, traçage)

Préparé le 10/10 à 20:15. Tout est prêt côté Mac **sauf la phrase secrète de test**, qui n'est que sur le PC de Timéo : sans elle, le relais ne démarre pas (il a besoin des clés du moniteur et de l'oracle) et rien ne peut être signé. Le Mac lit déjà Fuji sans clé (`etat-fuji.js`).

**Prérequis (une fois)**
1. `ia-2/.env` existe sur le Mac avec `FUJI_RPC_URL` rempli et `FUJI_MNEMONIC=` vide. Timéo tape la phrase de test **directement sur le Mac** (on est dans la même salle) : jamais dans Git, ni dans un message, ni dans le journal. Variante sans partage de la phrase : une phrase neuve sur le Mac (`npm run fuji:setup`), Timéo envoie 0,1 AVAX de test au nouveau déployeur, puis `npm run fuji:fund` et `npm run deploy:fuji` (nouveau déploiement, adresses à mettre à jour dans `ia-2/README.md`).
2. Partage de connexion (Bedrock) et identifiants AWS valides : `aws sts get-caller-identity --profile hackathon`.

```bash
# 0. état du portefeuille Fuji, en lecture seule (marche sans clé)
cd ia-2 && npx hardhat run ../ia-1/integration/etat-fuji.js --network fuji
cd ia-2 && npm run unfreeze:fuji          # seulement s'il est gelé par la démo précédente
# 1. relais Fuji (AVANT le moteur : il reconstruit shared/events.jsonl depuis le bloc du déploiement ;
#    il lit aussi shared/actions.jsonl : plus d'exécuteur ia-1/integration/actions.js)
cd ia-2 && npm run relay:fuji
# 2. moteur de score : carnet Fuji, modèle d'anomalie R2 (il tourne sur le Mac), explications Bedrock, services connus (R9)
cd ia-1 && .venv/bin/python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl \
  --carnet ../ia-2/deployments/fuji-carnet.json --modele modeles/anomalie.joblib \
  --services ../shared/services-connus.json --suivre --expliquer
# 3. tableau de bord → http://localhost:8599  (BREAKER_DEPLOIEMENT : sinon il prend localhost.json s'il existe)
cd ia-1 && BREAKER_DEPLOIEMENT="$PWD/../ia-2/deployments/fuji.json" .venv/bin/streamlit run dashboard/app.py --server.port 8599
# 4a. scénario de Timéo : paiement normal + fraude en rafale. SANS RESPOND=1 : c'est Romain qui gèle / annule
#     depuis le tableau de bord (barre « Je suis… »), et le relais signe. Liens Snowtrace dans le panneau « Actions ».
cd ia-2 && npm run scenario:fuji
# 4b. Web2 → Web3 : l'oracle signale l'arnaqueur du forum, puis on tente de le payer (bloqué par le registre et le moteur)
cd ia-1 && .venv/bin/python -m oracle.oracle oracle/corpus_demo/01-forum-arnaque.html --out ../shared/flags.jsonl
cd ia-2 && ADRESSE=0x6253540229bdcc8ae009fe075005a3fa5137c352 npx hardhat run ../ia-1/integration/scenario_oracle.js --network fuji
# 4c. traçage des fonds (T9 + R9) : arnaqueur → 3 mules + plateforme + poussière ; seul le paiement vers la mule est freiné
cd ia-2 && npm run tracing:fuji
# 5. rapport d'incident de la démo Fuji
cd ia-1 && .venv/bin/python -m score.rapport --dossier ../shared --sortie rapports/rapport-demo-fuji.md
```

À savoir : au démarrage, le relais rejoue toutes les lignes de `shared/flags.jsonl` (celles de la démo locale aussi) et le moteur relit les 4 paiements de la première démo Fuji (déjà annulés : le relais répond « alerte refusée », sans effet). Les délais sur Fuji : 30 s d'examen, 180 s d'attente, signalement en 5 à 6 s.

## Démo Fuji depuis le Mac (décision de Romain, 20:50)
La phrase secrète des comptes de test est dans `ia-2/.env` sur le Mac (ignoré par Git ; déployeur vérifié : `0x4EcC…8564`, 0,25 AVAX). Mêmes commandes qu'en local avec `:fuji` (`npm run relay:fuji`, `scenario:fuji`, `tracing:fuji`, `unfreeze:fuji`) et le carnet `ia-2/deployments/fuji-carnet.json`.
**Règle absolue : un seul relais Fuji à la fois** (Mac *ou* PC de Timéo), sinon chaque alerte et chaque action partent deux fois avec la même clé de moniteur. Se prévenir dans `JOURNAL.md` avant de lancer.

## Adresses pièges (idée 2, activée 10/10 21:55)
Les carnets `integration/carnet-local.json` et `integration/carnet-fuji.json` contiennent deux faux fournisseurs (`pieges`). Démo : `PIEGE=0x0bee7000000000000000000000000000000c0ffe npx hardhat run ../ia-1/integration/scenario_piege.js --network fuji` (depuis `ia-2`) → mise en attente à 0,99, « compromission probable du carnet ». Sur Fuji, lancer le moteur avec `--carnet ../ia-1/integration/carnet-fuji.json`.

## Clé d'identité froide et clé de contrainte (démo Fuji du 10/10 à 22:28)
```bash
cd ia-2 && npx hardhat run ../ia-1/integration/scenario_identite.js --network fuji     # clé volée → révoquée par la clé d'identité, seule, immédiatement
cd ia-2 && SIGNATAIRE=3 npx hardhat run ../ia-1/integration/scenario_contrainte.js --network fuji   # signature sous contrainte → inexécutable, alerte privée
```
Résultats Fuji (portefeuille v2 `0x5DfA…2Eed`) : révocation `KeyRevokedBySelf` en une transaction, voleur refusé, nouvelle clé en probation, 0 mUSD perdu ; contrainte : « 2/2 approuvé » à l'écran, non gelé officiellement, exécution refusée, 0 mUSD perdu, alerte privée `DURESS_SIGNATURE` (notification, `shared/alertes-privees.jsonl`, rien sur la chaîne).
**Après `scenario_identite`, la clé d'Emma (compte 4) est révoquée sur ce déploiement** : redéployer (`npm run deploy:fuji`) avant une démo qui l'utilise.
