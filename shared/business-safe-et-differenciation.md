# Safe, le catalogue d'applications, la « garde », et pourquoi un client paie Breaker

> Romain (avec Claude), 11/10 vers 08:10. Réponse à trois questions de Romain : qu'est-ce qu'un Safe ? qu'est-ce que le catalogue d'applications Safe et « s'installer sur un Safe » ? en quoi sommes-nous différents et pourquoi un client paierait ? Chaque affirmation porte sa source (S) ou sa preuve dans le dépôt (P). Rédigé pour être repris tel quel dans le pitch et les réponses au jury.

## 1. Qu'est-ce qu'un Safe ? (3 lignes pour le deck)
Un **Safe** est le coffre-fort numérique standard des organisations crypto : un programme sur la blockchain qui garde les fonds et n'exécute un paiement que si **plusieurs personnes** l'ont signé (par exemple 3 sur 5). Il est gratuit, open source, existe depuis 2017, et c'est lui que nos clients utilisent déjà : **35,25 Md$ sécurisés, 61 millions de comptes, plus d'un tiers de tout l'argent de la DeFi sur les chaînes EVM** (S : rapport trimestriel Safe Foundation T1 2026, 23 avril 2026). La Fondation Ethereum y a mis toute sa trésorerie (S : The Block). Il est disponible sur plus de 40 réseaux (S : safe.global) dont **Avalanche C-Chain** (S : eco.com, guide 2026 ; **à vérifier en ouvrant app.safe.global** : sélecteur de réseau), et pour les L1 Avalanche via Ash Wallet (S : build.avax.network/integrations/gnosis-safe).

**Pourquoi c'est central pour nous :** notre cible a *déjà* un Safe. On ne lui demandera jamais de déplacer sa trésorerie pour nous essayer : ce serait la fin de l'essai gratuit (décision « entrée sur le marché », 10/10).

### 1 bis. Safe, Safe Foundation, Safe Labs : qui est qui ?
Quand on dit « Safe », on parle d'un seul produit porté par deux entités :
- **Safe Foundation** (ex-Safe Ecosystem Foundation) : fondation à but non lucratif, elle gouverne le protocole open source, le jeton SAFE et les subventions (S : safefoundation.org).
- **Safe Labs GmbH** (Berlin) : **filiale commerciale à 100 % de la fondation**, créée le 5 juin 2025, dirigée par Rahul Rumalla ; c'est elle qui développe et exploite Safe{Wallet}, a pris le contrôle direct de l'interface en octobre 2025, et vend **Safe Pro et Safe Shield** (S : safefoundation.org, CoinDesk 11/06/2025, The Defiant). Objectif annoncé : 10 M$ de revenu récurrent en 2025, 100 M$ visés en 2030 (S : GlobeNewswire 03/02/2026).

**Conséquence pour nous :** notre interlocuteur **commercial** (catalogue d'applications, partenariat, Safe Pro comme prix de référence) est **Safe Labs** ; notre interlocuteur **technique** (contrats, mécanisme Guard, subventions) est la **Safe Foundation**. Et Safe Labs est désormais une entreprise qui cherche du revenu : c'est elle qui pourrait un jour vendre de la détection ; voir § 7, première question.

## 2. Le catalogue d'applications Safe (Safe Apps)
Dans l'interface Safe{Wallet} (app.safe.global), un onglet « Apps » liste des applications tierces que l'utilisateur ouvre **sans quitter son coffre** : elles s'affichent dans la page et proposent des transactions que les signataires approuvent comme d'habitude. Safe publie un SDK pour les développer (S : github.com/safe-global/safe-apps-sdk : « Client-side SDKs to create third-party Safe Apps »). Un développeur peut aussi donner l'adresse de son application à un utilisateur, qui l'ajoute lui-même (« custom app »).

**Ce que ça nous apporte :** une **distribution gratuite, en libre-service**, au seul endroit où nos clients sont tous : l'application Breaker (tableau de bord, activation de l'observation, réglage des profils) peut être ouverte depuis le Safe du client. C'est la façon concrète de tenir « libre-service, observation gratuite, friction ensuite ».

## 3. « S'installer sur un Safe » : le mécanisme Guard
Safe prévoit, depuis sa version 1.3.0, un point de branchement appelé **Guard** : un contrat que le Safe **appelle avant chaque transaction** et qui peut **la refuser**. S (doc officielle Safe, « Safe Guards ») : « Safe Guards are used when there are restrictions on top of the n-out-of-m scheme » ; « a Safe Guard has full power to block Safe transaction execution ». La même doc avertit : « a broken Guard can cause a denial of service for a Safe […] Make sure to audit the Guard code and pay attention to recovery mechanisms. »

**Où nous en sommes, honnêtement.** Aujourd'hui `TreasuryGuard` (P : `ia-2/contracts/TreasuryGuard.sol`) est un **multisig complet** avec la garde intégrée : c'est ce qu'on démontre sur Fuji. Pour tenir la promesse « se branche sur votre Safe », il faut **porter la garde en Safe Guard** : la logique (délai de revue, mise en attente, signature en plus, gel, clé d'identité) devient le contrat appelé par le Safe du client. C'est en feuille de route (B7), chantier de Timéo, pas pour ce week-end. **À dire au jury :** « démontré sur notre multisig, portage en Safe Guard en feuille de route ; l'avertissement de Safe sur les Guards est exactement pourquoi notre garde ne peut jamais bloquer définitivement : l'unanimité des signataires lève toute attente » (P : `approveUnfreeze`, invariant I5 dans `ia-1/integration/invariants.test.js`).

## 4. Ce que Safe vend lui-même, et ce qu'il ne fait pas
| Produit Safe | Ce qu'il fait | Ce qu'il ne fait pas | Source |
|---|---|---|---|
| Safe{Wallet} (gratuit) | le coffre multi-signatures | aucune analyse du paiement | safe.global |
| Safe Shield (de base, gratuit) | vérifie que la transaction fait ce qu'elle affiche (simulation, adresses malveillantes connues) | ne connaît pas l'historique du client, ne ralentit rien, n'alerte pas les autres signataires | safe.global/pricing |
| Safe Pro Business (dès 669 €/mois) | **politiques** : listes blanches, plafonds, délais **que le client écrit** | ne détecte rien que le client n'ait pas prévu dans sa règle | safe.global/pricing |

## 5. Les six différences de Breaker, chacune avec sa preuve
| # | Différence | Pourquoi Safe Pro ne le fait pas | Preuve dans le dépôt |
|---|---|---|---|
| 1 | **Détecte l'imprévu** : montant hors norme *pour ce client*, bénéficiaire nouveau, précipitation, mémo d'urgence, nouveau signataire qui pousse un gros paiement | une politique ne connaît que ce qu'on y a écrit ; nous apprenons l'historique du client | `ia-1/score/regles.py` ; 95 % des fraudes freinées sur des formes jamais vues (`shared/mesures.md`) |
| 2 | **Explique en français** à des gens sans équipe sécurité, et ne bloque pas : il **ralentit et demande une signature en plus** | Safe Pro refuse ou accepte, sans phrase | `ia-1/score/explication.py` ; modes Step-up / Hold du contrat |
| 3 | **Vérifie le bénéficiaire sur le Web** (adresse sosie, fonds souillés par traçage, listes OFAC / ScamSniffer, pièges) | Safe Shield : adresses connues seulement, pas de traçage ni de lecture de sources | `ia-1/oracle/`, `shared/listes-publiques.jsonl`, `RiskRegistry` |
| 4 | **Protège la personne, pas seulement la clé** : clé d'identité pour révoquer sa propre clé volée seul, clé de contrainte pour signer « oui » sous menace tout en gelant | inexistant chez Safe | `revokeMyKey`, `setDuressKey` ; démos Fuji `scenario_identite.js`, `scenario_contrainte.js` |
| 5 | **Jamais dépositaire, jamais bloquant pour toujours** | les dépositaires (Fireblocks) gardent les clés ; Guardian signe à votre place | invariants I1-I6, 0 violation sur 6 926 appels ; `approveUnfreeze` |
| 6 | **Né sur Avalanche**, portable EVM | Safe Pro est sans spécificité Avalanche ; les concurrents de surveillance sont Ethereum-first | déployé Fuji ; Solidity standard |

## 6. Pourquoi un client paie (l'argument en une phrase, puis les chiffres)
« Vous avez déjà le coffre. Il vous manque **quelqu'un qui regarde chaque paiement** et vous dit, en français, quand quelque chose ne colle pas, avant que l'argent parte. » C'est le travail d'un SOC antifraude, que nos cibles n'ont pas (décision cible : organisations sans équipe sécurité).
- Ce qu'il évite : perte annuelle attendue ≈ 22 à 112 k$/an selon le périmètre (C : `shared/business-prix.md` § 1.B, à partir de TRM et de nos mesures).
- Ce qu'il paie : 449 €/mois Standard = 5,4 k€/an = **5 à 25 %** de la perte évitée.
- Ce que le marché accepte déjà de payer pour moins : 669 €/mois à Safe pour des règles à écrire soi-même (S : safe.global/pricing), 999 $/mois à Fireblocks (S : fireblocks.com/pricing).

## 7. Questions du jury et réponses courtes
- **« Safe peut faire la même chose demain. »** Safe vend une infrastructure neutre et des règles ; depuis 2017 il n'a pas fait de détection comportementale (S : grille Safe Pro d'octobre 2026). S'il le fait, le mécanisme Guard est ouvert à tous et le client choisit ; notre avance est l'historique client, l'oracle et la protection de la personne.
- **« Pourquoi pas un Safe Guard dès maintenant ? »** Parce qu'en 36 h on a préféré démontrer la logique de bout en bout sur une chaîne réelle (Fuji) plutôt qu'une intégration ; le portage est un chantier d'ingénierie, pas un risque de concept : la doc Safe le prévoit.
- **« Un Guard cassé bloque le Safe. »** Oui, et c'est pourquoi aucune attente n'est définitive chez nous : l'unanimité des signataires lève tout (invariant I5), et la garde ne touche jamais aux fonds (I1).

## Sources
- Safe Labs : https://safefoundation.org/blog/safe-labs-launch-rahul-rumalla-ceo · https://www.coindesk.com/tech/2025/06/11/safe-establishes-new-development-firm-to-attract-institutions-and-tackle-cryptos-cyber-warfare-era · https://thedefiant.io/news/infrastructure/safe-labs-takes-the-reins-of-popular-multi-signature-wallet · https://www.globenewswire.com/news-release/2026/02/03/3231251/0/en/Safe-Project-Reports-10M-Revenue-Targets-Break-Even-and-100M-ARR-Path-by-2030.html · https://safe.global/imprint
- Safe Foundation, rapport T1 2026 (23/04/2026) : https://safefoundation.org/blog/safe-q1-2026-quarterly-report
- safe.global (40+ réseaux, 9+ ans, 18+ audits) : https://safe.global/ · prix : https://safe.global/pricing
- Doc Safe Guards : https://docs.safe.global/advanced/smart-account-guards
- Safe Apps SDK : https://github.com/safe-global/safe-apps-sdk
- Safe sur Avalanche : https://build.avax.network/integrations/gnosis-safe (L1 via Ash Wallet) · https://eco.com/support/en/articles/15254042-safe-wallet-deep-dive-2026-multisig-and-smart-accounts (C-Chain, secondaire)
- Fondation Ethereum → Safe : https://www.theblock.co/press-releases/375708/just-in-ethereum-foundation-moves-entire-650m-treasury-to-safe-multisig
- Fireblocks : https://www.fireblocks.com/pricing
