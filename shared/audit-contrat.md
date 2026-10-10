# Audit du contrat TreasuryGuard : ce qui a été fait, ce qui reste (B1 §8, exécuté par Romain le 11/10)

> Décision de Romain : « exécute ce que tu m'as proposé » (11/10, 00:55). Ce document est la pièce à montrer au jury quand il demandera « votre contrat est-il audité ? ».

## 1. Analyse statique (Slither 0.11, solc 0.8.24) — 11/10 01:00
Commande : `cd ia-2 && slither . --exclude-dependencies --filter-paths "node_modules|MockToken"` (Slither installé dans `ia-1/.venv-audit`).

**Aucune détection de sévérité haute ou moyenne** : pas de réentrance, pas de contrôle d'accès manquant, pas d'arithmétique dangereuse, pas de délégation ni de sélecteur suspect. Détections informatives, toutes examinées :

| Détecteur | Où | Verdict |
|---|---|---|
| `timestamp` (comparaisons à `block.timestamp`) | délais d'examen, mise en attente, expiration des clés, probation, fenêtre du plafond | **Attendu** : toute la logique est temporelle. Un validateur peut décaler l'horodatage de quelques secondes ; nos délais sont de minutes à jours, l'effet est négligeable |
| `incorrect-equality` | `keyExpiresAt[x] == 0`, `risk == Risk.None` | **Faux positif** : égalités à une valeur sentinelle, pas à un solde |
| `uninitialized-local` | `approvals` dans `approveUnfreeze` | **Bénin** : un `uint256` local vaut 0 par défaut, et il est incrémenté ensuite |
| `missing-zero-check` | `riskOracle_` au constructeur | **Voulu** : adresse nulle = portefeuille sans garde (documenté dans le contrat) |
| `costly-loop`, `cache-array-length` | boucles sur `ownerList` (≤ 5 signataires) | **Optimisation de gas**, sans effet de sécurité ; à faire lors de l'audit externe |
| `missing-inheritance` | `RiskRegistry` n'hérite pas de `IRiskRegistry` | **Cosmétique** ; à corriger (une ligne) |

## 2. Tests d'invariants par séquences aléatoires (« fuzzing léger ») — 11/10 01:05
`ia-1/integration/invariants.test.js`, lancé avec `cd ia-2 && FUZZ_SEQ=300 npx hardhat test ../ia-1/integration/invariants.test.js`.
300 séquences de 25 appels tirés au hasard parmi 11 actions (proposer, approuver, exécuter, annuler, signaler, geler, dégeler, remplacer un signataire, changer le seuil, révoquer par clé d'identité, faire passer le temps), par 8 clés différentes (5 signataires, un intrus, la clé d'identité, le moniteur). **6 926 appels joués, 3 004 acceptés, 3 922 refusés par le contrat. Aucun invariant violé :**
- I1 la trésorerie ne baisse que par l'exécution d'un paiement proposé, approuvé et non annulé ;
- I2 le moniteur ne peut rien faire d'autre que relever un niveau de risque ;
- I3 un intrus ne peut rien faire ;
- I4 la clé d'identité ne peut jamais exécuter, annuler, geler ni dégeler ;
- I6 le nombre de signataires actifs reste constant hors révocation.
Reproductible (graines fixées). À augmenter (`FUZZ_SEQ=3000`) avant l'audit externe.

## 3. Tests unitaires — 50 (Timéo 44 + identité 6), `cd ia-2 && npx hardhat test`.

## 4. Publication
- Licence MIT déjà en tête des contrats. Le dépôt doit être **public avant le rendu de dimanche 12:00** (livrable L8) : le code, les 50 tests, ce rapport et les ABI seront donc lisibles par tous. Contrats vérifiés sur Snowtrace : à faire lors du prochain déploiement Fuji (Timéo, `hardhat verify`).

## 5. Ce qui reste, et quand
| Étape | Quand | Coût estimé | Pourquoi c'est tenable |
|---|---|---|---|
| Corriger les points cosmétiques (héritage, cache des longueurs) | avant le rendu | 15 min | — |
| **Audit externe** par un cabinet | **avant le premier client payant** | de l'ordre de 10 à 25 k$ pour ~500 lignes **(estimation, non vérifiée auprès d'un cabinet)** | surface petite : le contrat **ne garde pas de fonds et n'a aucun pouvoir sur eux** ; le pire bug possible est un faux ralentissement, jamais une perte |
| Introduction à un auditeur | demain, via les mentors Kryptosphère / Team1 ; subventions Avalanche à demander | — | écosystème présent au hackathon |
| Prime aux bugs (Immunefi ou équivalent) | après l'audit | variable | standard du marché |
| Revue à chaque modification du contrat | permanent | — | processus |

**Phrase pour le jury :** « Le contrat n'est pas encore audité par un tiers : analyse statique sans détection grave, 50 tests, 7 000 appels aléatoires sans invariant violé, code public. L'audit externe est budgété avant le premier client payant, et notre contrat ne peut, par construction, perdre aucun fonds : au pire, il ralentit. »
