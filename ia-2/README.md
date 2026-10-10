# ia-2 : le portefeuille gardé, le registre et les données de test

Partie de Timéo dans le projet « Breaker » (voir `PLAN.md` et `SUIVI.md`). **Client visé :** une organisation qui garde des millions dans un portefeuille à plusieurs signataires sans équipe de sécurité, par exemple l'équipe d'un protocole, une DAO, une startup crypto ou un fonds (`shared/cible-et-modele-economique.md`). Ce dossier contient : les contrats sur la chaîne, le relais vers le moteur de score de `ia-1/`, et de quoi produire du trafic normal et des fraudes pour le mesurer.

## État

| Tâche | Brique | État |
|---|---|---|
| T1 | Format des fichiers échangés (`shared/format-evenements.md`) et exemples | Fait |
| T2 | Contrat `TreasuryGuard` | Fait, 20 tests passent sur la chaîne locale |
| T8 | Contrat `RiskRegistry` (adresses signalées par l'oracle) | Fait, branché au portefeuille |
| T7 | Mesure du gas (`shared/frais-gas.md`) | Fait |
| T3 | Relais entre la chaîne et les fichiers JSON Lines | Fait, testé de bout en bout sur la chaîne locale avec un faux moteur de score |
| T4 | Générateur de trafic normal | Fait : `shared/donnees/train.*`, 362 paiements sur 60 jours |
| T5 | Scénarios de fraude | Fait : `shared/donnees/test.*`, 54 paiements frauduleux, 6 variantes ; scénario de démo en direct |
| T9 | Traçage des fonds, côté données | Fait : le relais écrit les transferts sortis des adresses signalées (`token_transfer`) ; scénario `npm run tracing:local` testé en local |
| — | Actions des signataires depuis le tableau de bord | Fait : le relais lit `shared/actions.jsonl` (voir `shared/format-actions.md`), testé en local |
| T6 | Déploiement sur Avalanche Fuji | **Fait le 10 octobre à 19h30** : contrats déployés, démo rejouée sur Fuji avec le moteur de score, 0 mUSD sorti |

## Le portefeuille `TreasuryGuard` en bref

Un portefeuille de trésorerie à plusieurs signataires (2 sur 5 dans la démo), pour un seul actif (mUSD, faux dollar de test).

1. Un signataire **propose** un paiement ; sa proposition vaut première approbation.
2. Les autres **approuvent**.
3. Après un **délai d'examen** (60 secondes), un signataire **exécute** si le nombre d'approbations suffit.

Ce qui ajoute de la friction :

| Déclencheur | Effet |
|---|---|
| Le moniteur signale `StepUp` | Une signature de plus |
| Le moniteur signale `Hold` | Une signature de plus et une heure d'attente, pendant laquelle un signataire peut annuler |
| Le bénéficiaire est au registre des adresses signalées | `StepUp` ou `Hold`, appliqué dès la proposition |
| Le plafond de la période (100 000 mUSD par jour) serait dépassé | Une signature de plus |
| Remplacement d'un signataire ou changement du seuil | Toujours une signature de plus et une heure d'attente |

Ce qui protège les signataires eux-mêmes :
- **Gel** : un seul signataire suffit pour geler les paiements, il en faut trois pour dégeler.
- **Expiration des clés** : une clé de plus de 15 jours ne peut plus rien signer, et les approbations qu'elle a données ne comptent plus. Remplacer un signataire annule aussi ses approbations en cours.
- **Unanimité** : si les cinq signataires approuvent, le délai d'attente saute. Ils gardent le dernier mot.

**Le moniteur n'a qu'un pouvoir : relever le niveau de risque d'un paiement en attente.** Il ne peut ni proposer, ni approuver, ni exécuter, ni annuler, ni geler, ni abaisser un niveau. Les tests le vérifient un par un.

## Le scénario de fraude des tests

Deux signataires trompés proposent et approuvent dix paiements de 95 000 mUSD vers une adresse inconnue.

| Configuration | Résultat |
|---|---|
| Portefeuille témoin, simple 2 sur 5 | 950 000 mUSD sur 1 000 000 partent |
| Avec le garde : chaque paiement est signalé `Hold`, un signataire alerté gèle et annule | Rien ne sort |
| Garde sans moniteur : seul le plafond joue | 95 000 mUSD partent, le deuxième paiement exige une troisième signature |

## Installation et commandes

Il faut Node.js 20 ou plus récent.

```bash
cd ia-2
npm install
npm test            # compile et lance les 20 tests sur la chaîne locale de Hardhat
npm run gas         # mesure le gas des transactions
npm run export-abi  # régénère shared/abi/*.json
npm run dataset     # régénère shared/donnees/ (90 jours simulés, 15 secondes)
```

## Démo en direct sur la chaîne locale

Quatre terminaux, dans cet ordre. Le moteur de score de `ia-1/` doit tourner sur la même machine que le relais : ils se parlent par les fichiers de `shared/`.

```bash
# 1. la chaîne locale
cd ia-2 && npm run node
# 2. les contrats (délais courts par défaut : 30 s d'examen, 180 s d'attente)
cd ia-2 && npm run deploy:local
# 3. le relais : écrit shared/events.jsonl, lit shared/alerts.jsonl et shared/flags.jsonl
cd ia-2 && npm run relay:local
# 4. le moteur de score de Romain, en mode suivi (voir ia-1/README.md), puis le scénario
cd ia-2 && npm run scenario:local
```

Le scénario joue un paiement normal, puis trois virements frauduleux de 95 000 mUSD par deux signataires trompés. Avec `RESPOND=1`, un signataire alerté gèle le portefeuille et annule. Variables utiles : `REVIEW_DELAY`, `HOLD_DELAY` (au déploiement), `FRAUD_COUNT` (scénario), `RELAY_DIR` (relais).

Sous PowerShell, une variable se passe ainsi : `$env:RESPOND = "1"; npm run scenario:local`.

Les trois fichiers vivants de `shared/` et `deployments/localhost.json` sont ignorés par Git.

Pour Fuji, copier `.env.example` en `.env` et y mettre les clés de portefeuilles **de test**. `.env` est ignoré par Git.

## Déploiement sur Avalanche Fuji (T6)

**Déployé le 10 octobre 2026 à 19h29 (bloc 59275146), réseau Fuji C-Chain, identifiant de chaîne 43113.**

| Contrat | Adresse |
|---|---|
| Portefeuille `TreasuryGuard` | [`0xfDb595EA595195C149ABf2bf28892c34a1a06D9c`](https://testnet.snowtrace.io/address/0xfDb595EA595195C149ABf2bf28892c34a1a06D9c) |
| Registre `RiskRegistry` | [`0x24871b8A07a7C7B2632E760c23051661E341cC40`](https://testnet.snowtrace.io/address/0x24871b8A07a7C7B2632E760c23051661E341cC40) |
| Jeton de test `mUSD` | [`0xFF65eD05180D3f725a1DE658e0f539A3452274bD`](https://testnet.snowtrace.io/address/0xFF65eD05180D3f725a1DE658e0f539A3452274bD) |

Réglages : 2 signataires sur 5, délai d'examen de 30 secondes, mise en attente de 180 secondes, plafond de 100 000 mUSD par jour. Tout est dans `deployments/fuji.json` ; le carnet d'adresses du moteur de score est dans `deployments/fuji-carnet.json`.

### Première démo sur Fuji (19h30)

Relais et moteur de score de `ia-1/` (règles seules) lancés sur le PC de Timéo, scénario `RESPOND=1 npm run scenario:fuji`.

| Étape | Résultat | Transaction |
|---|---|---|
| Paiement normal de 3 150 mUSD à un prestataire habituel | Exécuté sans friction, 40 s après la proposition | [exécution](https://testnet.snowtrace.io/tx/0x694ff4b823b92aaa9ae0ad074d15d22b76ec41031b8eda2d56369430863d46fb) |
| Fraude n° 1, 95 000 mUSD vers une adresse inconnue | Mise en attente **6 s** après la proposition | [proposition](https://testnet.snowtrace.io/tx/0xc10d4c72af80c11696a5ec795889b261da8a77cc7b4fc24c1fa218a32f4f6555), [signalement](https://testnet.snowtrace.io/tx/0x396d108192305d1c9da8a0adbf2975c76821c46585cbf158084bcf4941a30ef1) |
| Fraude n° 2, 93 500 mUSD | Mise en attente **5 s** après | [signalement](https://testnet.snowtrace.io/tx/0x6b79fc2689a88fc31ff929b7ba4b07780199c73f89d918d8d8ff68b7644dc9bd) |
| Fraude n° 3, 92 000 mUSD | Mise en attente **6 s** après | [signalement](https://testnet.snowtrace.io/tx/0x6b03e5bbcae8409a0d27421c4c13e06de0106f88742aa86b77c68498de2e59fd) |
| Les deux signataires trompés tentent d'exécuter | Bloqués : 2 signatures sur 3 exigées | — |
| Un signataire alerté gèle puis annule | Portefeuille gelé, 3 paiements annulés | [gel](https://testnet.snowtrace.io/tx/0xadc503aceb8de75877481fccaf0f1ed312b5c2f726e005912fc65f4a7d5c857b) |

**Bilan : 0 mUSD parti chez le fraudeur sur 280 500 tentés.** Raisons inscrites sur la chaîne par le moniteur : `PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS` (score 0,88).

Coût réel constaté : environ 0,00054 AVAX pour tout le déploiement et 0,00005 AVAX pour les trois signalements du moniteur.

### Rejouer la démo sur Fuji

```bash
cd ia-2
npm run unfreeze:fuji   # si la démo précédente a gelé le portefeuille (trois signataires votent le dégel)
npm run relay:fuji      # terminal 1 ; écrit shared/events.jsonl, lit shared/alerts.jsonl et shared/flags.jsonl
# terminal 2, depuis ia-1 : le moteur de score en mode suivi, avec --carnet ../ia-2/deployments/fuji-carnet.json
npm run scenario:fuji   # terminal 3 ; RESPOND=1 pour le gel et l'annulation
```

- Les dix comptes de test et leur rôle sont dans `deployments/fuji-comptes.json` (adresses publiques seulement).
- La phrase secrète reste dans `ia-2/.env`, sur le PC de Timéo. Elle ne va ni dans Git ni dans un message.
- Pour repartir d'un portefeuille neuf : `npm run deploy:fuji`, puis mettre à jour les adresses ci-dessus. Il reste environ 0,25 AVAX de test au déployeur, de quoi redéployer des centaines de fois.

### Où lancer la démo Fuji

Sur le PC de Timéo, là où se trouve la phrase secrète. Le moteur de score de `ia-1/` y est installé (`ia-1/.venv`) et a été testé avec le relais sur la chaîne locale puis sur Fuji.

**Limite sur ce PC : le modèle d'anomalie (R2) ne tourne pas.** Le contrôle d'application de Windows (Smart App Control) bloque un fichier de scikit-learn. Le moteur fonctionne avec ses règles seules, ce qui suffit au scénario de démo. Les mesures avec le modèle se font sur le Mac de Romain.

Sous Windows, les commandes de `ia-1/README.md` s'écrivent avec `.venv/Scripts/python.exe` au lieu de `.venv/bin/python`, et avec la variable `PYTHONUTF8=1`.

## Traçage des fonds (T9)

Quand une adresse entre au registre, le relais remonte tous les transferts de mUSD qu'elle a émis depuis le déploiement et les écrit dans `events.jsonl` (type `token_transfer`), puis continue de la suivre. Le moteur de score peut ainsi freiner un paiement vers une mule dont personne ne parle sur le Web.

```bash
npm run tracing:local   # ou tracing:fuji ; le relais doit tourner à côté
```

Le scénario : un arnaqueur encaisse 100 000 mUSD, en envoie 18 000, 12 000 et 10 000 à trois mules, 30 000 à une plateforme d'échange et 0,01 à un innocent, puis l'oracle le signale. L'organisation propose ensuite trois paiements : à une mule, à l'innocent, à la plateforme. Seul le premier doit être freiné. Rôles et étiquettes : `shared/tracage-roles.json` après le passage, exemple figé dans `shared/echantillons/tracage.*`.

Le relais ne juge pas : il écrit tous les transferts sortants, poussière comprise. Écarter la poussière et les services partagés (`shared/services-connus.json`, adresses factices) est le travail du moteur de score.

## Limites connues

- Prototype non audité. Un seul actif, à 18 décimales.
- Un signataire dont la clé est volée peut geler le portefeuille ou annuler des paiements légitimes. Il ne peut pas payer seul.
- Si trop de clés expirent en même temps, il ne reste plus assez de signataires actifs pour agir : le renouvellement doit être étalé.
- Si tous les signataires établis sont trompés à la fois, l'unanimité peut raccourcir le délai d'attente des paiements au délai d'examen. Elle ne raccourcit jamais le délai de gouvernance.
- Le moniteur doit rendre son verdict pendant le délai d'examen. S'il est en panne, seuls le plafond et le registre jouent.
- En production, ces règles seraient un module greffé sur le portefeuille que le client utilise déjà (Safe sur les chaînes EVM, Squads sur Solana), pas un portefeuille écrit de zéro. C'est aussi le canal de distribution prévu.

## Probation et gouvernance (correction du 10 octobre, testée en local)

Une clé remplacée attend **deux jours** avant de compter dans tout quorum renforcé : paiement risqué, dépassement du plafond, remplacement d'une autre clé, changement de seuil et dégel. Elle reste utilisable pour les paiements ordinaires. Les clés initiales sont établies au déploiement. Le retrait/réajout d'une adresse invalide ses anciens votes. L'unanimité ne permet plus de contourner le délai de gouvernance.

Lectures ajoutées à l'ABI : KEY_PROBATION, keyTrustedAfter, keyEpoch, isEstablishedOwner ; événement OwnerProbationStarted. La structure Config et les interfaces déjà utilisées par le relais sont conservées.

**30 tests locaux passent**, dont 10 nouvelles régressions. **Le portefeuille Fuji actuel n'a pas été redéployé : il n'applique pas cette probation.** Un redéploiement est nécessaire pour activer la correction sur Fuji ; coordonner l'arrêt du relais puis mettre à jour le carnet, les adresses et les liens de preuves.

Étaler les rotations pour conserver assez de clés établies, et utiliser une durée de validité supérieure à deux jours. Aucun mécanisme indépendant de récupération n'est ajouté. Détail, sources concurrentes, gas et limites : [améliorations après bilan](../shared/ameliorations-apres-bilan.md).
