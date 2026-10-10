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
| T6 | Déploiement sur Avalanche Fuji | À faire |

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

## Limites connues

- Prototype non audité. Un seul actif, à 18 décimales.
- Un signataire dont la clé est volée peut geler le portefeuille ou annuler des paiements légitimes. Il ne peut pas payer seul.
- Si trop de clés expirent en même temps, il ne reste plus assez de signataires actifs pour agir : le renouvellement doit être étalé.
- Si tous les signataires sont trompés à la fois, l'unanimité fait sauter le délai d'attente.
- Le moniteur doit rendre son verdict pendant le délai d'examen. S'il est en panne, seuls le plafond et le registre jouent.
- En production, ces règles seraient un module greffé sur le portefeuille que le client utilise déjà (Safe sur les chaînes EVM, Squads sur Solana), pas un portefeuille écrit de zéro. C'est aussi le canal de distribution prévu.
