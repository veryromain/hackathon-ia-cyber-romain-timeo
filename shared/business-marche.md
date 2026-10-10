# B3 — Le marché : combien d'organisations, combien de trésorerie, et Avalanche est-il assez grand ?

> Romain (avec Claude), 11/10 vers 01:35. **Brouillon chiffré avec hypothèses explicites.** Les sources trouvées sont secondaires et se contredisent ; chaque chiffre porte son niveau de confiance. **À vérifier avant la slide sur trois sources primaires :** le tableau de bord DeepDAO, le service de transactions Safe sur Avalanche (nombre de Safe au-dessus d'un seuil), l'annuaire de l'écosystème de la Fondation Avalanche.

## 1. Les repères qu'on a (et ce qu'ils valent)

| Repère | Valeur | Confiance |
|---|---|---|
| Trésoreries des DAO, toutes chaînes | **≈ 25 à 35 Md$** gérés par **≈ 4 700 à 13 000 DAO** selon les agrégateurs (DeepDAO suit ≈ 5 000 organisations listées, 300 suivies de près) | Faible à moyenne : agrégateurs, chiffres contradictoires |
| Concentration | Les plus grosses trésoreries sont surtout leur propre jeton : ≈ 88 % pour Arbitrum, 78 % ENS, 70 % Aave ; Optimism et Uniswap ≈ 3 Md$ chacun | Moyenne |
| Safe (le multisig standard) | > 100 Md$ sécurisés sur plus de 30 réseaux ; environ 68 % des DAO l'utiliseraient (une seule source, non vérifiable) ; **Safe est disponible sur la C-Chain et les L1 Avalanche** ; Ash Wallet (fournisseur Safe) sert plus de 10 équipes de L1 Avalanche pour leur trésorerie depuis 2 ans (annonce Avalanche Developers, juin 2026) | Moyenne (Safe), bonne (annonce Avalanche) |
| Avalanche : activité | **653 protocoles** référencés (DeFiLlama), TVL native ≈ 0,6 à 0,76 Md$, TVL pontée ≈ 4,9 Md$ ; **> 50 L1 actives** ; ≈ 30 équipes dans la première cohorte Retro9000 ; 134 développeurs à temps plein, 419 actifs mensuels (Electric Capital, août 2026) | Bonne (DeFiLlama, Electric Capital), les TVL varient avec les prix |
| Marché « logiciels de gestion de trésorerie crypto » | ≈ 1,7 à 1,8 Md$ en 2026 selon des cabinets, avec des périmètres différents | Faible : projections commerciales |
| Configuration type d'une trésorerie de 1 à 50 M$ | multisig 3-sur-5 ou 4-sur-7 | Moyenne (guides) |

## 2. Taille de marché, par la méthode « nombre d'organisations × prix » (hypothèses visibles)

**Unité :** une organisation = un portefeuille multisig protégé. **Prix retenu pour le calcul :** 500 € / mois (hypothèse B6, à confirmer).

| | Qui | Nombre (hypothèse) | Revenu annuel potentiel à 500 €/mois |
|---|---|---|---|
| **TAM** (toutes chaînes EVM) | DAO, équipes de protocoles, startups crypto, fonds et fondations tenant ≥ 1 M$ en multisig | DAO : 10 à 15 % des ≈ 5 000 DAO suivies, soit **500 à 750** ; équipes de protocoles et startups hors DAO : ordre de grandeur comparable, **500 à 1 000** ; fonds et fondations : **200 à 400**. **Total ≈ 1 200 à 2 100 organisations** | **≈ 7 à 13 M€ / an** |
| **SAM** (Avalanche d'abord) | Les mêmes, dont la trésorerie principale est sur la C-Chain ou une L1 Avalanche | 653 protocoles référencés, 50 L1, cohortes de subventions : **≈ 100 à 300 organisations** avec une trésorerie significative | **≈ 0,6 à 1,8 M€ / an** |
| **SOM** (12 premiers mois) | Clients atteignables par l'écosystème (Team1, Fondation, Kryptosphère, hackathons) et le catalogue Safe | **10 à 25 clients payants**, après 30 à 60 en mode observation gratuit | **≈ 60 à 150 k€** |

**Lecture honnête :** Avalanche seul est un **marché d'amorçage**, pas un marché final : de l'ordre du million d'euros par an au mieux, à ce prix. C'est suffisant pour un lancement (références, données réelles, écosystème qui aide), **pas pour une entreprise**. D'où deux leviers déjà décidés : **« né sur Avalanche, portable EVM »** (le contrat est en Solidity : l'extension à Ethereum, Base, Arbitrum multiplie le SAM par 10 ou plus) et **un prix par palier de trésorerie** (une fondation à 50 M$ ne paie pas 500 €, voir B6).

## 3. Ce que le jury demandera, et la réponse
- **« Avalanche est-il assez grand ? »** Pour démarrer, oui : 653 protocoles, plus de 50 L1 avec leurs équipes, Safe disponible, un écosystème qui nous présente des clients. Pour croître, non : d'où la portabilité EVM, décidée dès le départ.
- **« Combien de clients ? »** Entre 100 et 300 organisations adressables sur Avalanche selon nos hypothèses, 1 200 à 2 100 sur l'EVM. Ce sont des ordres de grandeur, pas des comptages : on les affinera avec les données Safe et DeepDAO.
- **« Pourquoi paieraient-ils ? »** Parce que les pertes se comptent en centaines de millions (Bybit, Drift) et qu'aucune offre n'existe pour les équipes sans équipe de sécurité (B4). La réponse définitive vient des entretiens (B5).

## 4. À faire pour durcir ces chiffres (avant la slide, si possible demain matin)
1. DeepDAO : nombre de DAO avec trésorerie > 1 M$ (filtre direct sur le tableau de bord).
2. Safe sur Avalanche : nombre de Safe avec solde > 100 k$ (service de transactions Safe ou Dune).
3. Annuaire de la Fondation Avalanche : nombre d'équipes et de L1 actives.
4. Demander au mentor Team1 une estimation du nombre d'équipes Avalanche avec trésorerie multisig : c'est la source la plus crédible pour le jury.

## Sources (secondaires sauf mention)
- DAO : https://coinlaw.io/decentralized-autonomous-organizations-statistics/ · https://sqmagazine.co.uk/decentralized-autonomous-organizations-statistics/ · https://eco.com/support/en/articles/14799687-dao-treasury-management-onchain-governance-spend
- Safe sur Avalanche : https://x.com/AvaxDevelopers/status/2066936314247643375 (annonce Ash Wallet, juin 2026) · https://build.avax.network/integrations
- Avalanche : https://defillama.com/chain/avalanche · https://defillama.com/chains · https://eco.com/support/en/articles/12168599-what-is-avalanche-avax-l1s-and-subnets-in-2026
- Marché logiciels : https://www.intelmarketresearch.com/crypto-treasury-management-for-corporates-market-44493 · https://www.persistencemarketresearch.com/market-research/crypto-asset-management-market.asp
- Multisig : https://withernode.com/benefits-of-multisig-for-dao-treasury
