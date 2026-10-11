# B3 — Le marché, version 2 : chaque chiffre a une source ou un calcul

> Romain (avec Claude), 11/10 vers 01:50. Règle fixée par Romain : **aucun chiffre arbitraire**. Chaque nombre porte sa source (S) ou son calcul (C). Les hypothèses sont nommées H1, H2… et chacune dit pourquoi on la fait. Ce qui n'a pas de source est **exclu du calcul**, pas estimé au doigt mouillé.

## 0. Définitions (pour le deck)
- **Protocole** : une application qui tourne sur la blockchain (échange, prêt, pont, jeu…). Derrière, une **équipe** qui garde une trésorerie, souvent en multisig : notre client.
- **TVL** (valeur totale bloquée) : l'argent des *utilisateurs* déposé dans un protocole. Indicateur d'activité ; ce n'est pas la trésorerie de l'équipe.
- **TAM / SAM / SOM** : tout le marché possible / la part que notre produit sert tel qu'il est (Avalanche, libre-service) / ce qu'on peut vraiment gagner en un an avec nos moyens. Seul le SOM engage.

## 1. Les données (toutes datées du 11/10/2026)

| # | Donnée | Valeur | Source |
|---|---|---|---|
| D1 | Protocoles référencés, toutes chaînes | **8 694** ; dont TVL > 100 k$ : 2 420 ; > 1 M$ : **1 359** ; > 10 M$ : **675** | S : API DeFiLlama `api.llama.fi/protocols`, lue le 11/10 (C : comptage par seuil, script dans ce document) |
| D2 | Protocoles présents sur Avalanche | **561** ; dont TVL sur Avalanche > 100 k$ : 126 ; > 1 M$ : **71** ; > 10 M$ : **22** ; uniquement sur Avalanche : 159 | S : même API, champ `chainTvls.Avalanche` |
| D3 | TVL d'Avalanche | 616 M$ (native) ; 468 chaînes référencées | S : `api.llama.fi/v2/chains` |
| D4 | DAO suivies / DAO avec trésorerie > 1 M$ / total des trésoreries | ≈ **14 000** / ≈ **220** / ≈ 26 Md$ (T1 2026) | S : DeepDAO, repris par daotimes.com, eco.com et un rapport GitHub (pas lu sur deepdao.io directement : **à confirmer**) |
| D5 | L1 Avalanche actives / équipes servies par Ash Wallet (Safe) | > 50 L1 (Fondation Avalanche, via eco.com) / > 10 équipes de L1 depuis 2 ans | S : eco.com ; annonce Avalanche Developers (X, juin 2026) |
| D6 | Cohorte Retro9000 (subventions Avalanche) | ≈ 30 équipes | S : eco.com |
| D7 | Incidents de sécurité 2025 | **TRM (2026 Crypto Crime Report) : 2,87 Md$ volés sur ≈ 150 hacks et exploits, toutes victimes confondues (plateformes centralisées comme Bybit et Nobitex, protocoles DeFi, infrastructures) ; moyenne 19,5 M$, médiane 1,3 M$ ; 5 incidents = 70 % de la valeur, Bybit seul 51 %. Par vecteur : attaques d'infrastructure (clés privées, accès privilégiés, front-ends : notre périmètre) 45 incidents, 2,2 Md$, 76 % ; exploits de code 52 incidents, 350 M$ ; attaques de protocole 25 incidents, 277 M$.** Immunefi (protocoles DeFi seulement, exploits, hors plateformes centralisées) : médiane 1,5 M$. CertiK : 3,35 Md$, > 700 incidents dont phishing d'individus, médiane 104 k$ | S : trmlabs.com/reports-and-whitepapers/2026-crypto-crime-report ; theblock.co/post/387453 ; deepstrike.io (Immunefi) ; CertiK Hack3d 2025 (via PANews) |
| D8 | Prix de Safe Pro (lancé les 6-8 oct. 2026) | **Starter 189 €/mois** (2 Safe), **Business dès 669 €/mois** (5 à 20 Safe), Enterprise sur devis ; Safe{Wallet} reste gratuit ; Safe Shield de base gratuit | S : safe.global/pricing (lu le 11/10) |
| D9 | Prix de Fireblocks | Essentials **999 $/mois** (6 mois max), Pro / Enterprise dès 36 000 $/an | S : fireblocks.com/pricing |
| D10 | Conversion essai gratuit → payant (SaaS B2B, sans carte bancaire) | **8,9 %** (ChartMogul, 200 produits) à **18,2–18,5 %** (First Page Sage, 86 entreprises ; 1Capture, médiane B2B 2025) | S : shno.co, mailertogo.com (compilations) |
| D11 | Fonds d'investissement et fondations crypto | **Aucune source de comptage trouvée** | → exclus du calcul (le TAM est donc une borne basse) |

## 2. Le calcul du marché

**Unité** : une organisation = un multisig à protéger, avec une trésorerie d'au moins 1 M$ (en dessous, le prix ne se justifie pas face à Safe Shield gratuit).

**H1** (révisée le 11/10, décision de Romain : **toute organisation avec plus de 1 M$ de trésorerie est dans la cible et comptée**) — *Une équipe dont le protocole gère plus de 1 M$ d'actifs d'utilisateurs détient une trésorerie propre ≥ 1 M$.* Pourquoi : pour opérer à cette échelle, l'équipe a levé des fonds ou perçoit des commissions ; c'est une hypothèse, pas une mesure, et elle est plus large que l'ancienne (seuil 10 M$, qui reste la **borne prudente** : 675 protocoles toutes chaînes, 22 sur Avalanche, 62 contactables, 3 à 6 payants). **H2** — *Les DAO ≥ 1 M$ (D4) et les équipes H1 se recouvrent partiellement, de façon inconnue.* On donne donc une fourchette : recouvrement total (borne basse) ou nul (borne haute).

| Cercle | Calcul | Résultat |
|---|---|---|
| **TAM** (chaînes EVM, borne basse : fonds et fondations exclus, D11) | C : 1 359 équipes (D1, H1) + 220 DAO (D4) − recouvrement (H2) ; borne prudente au seuil 10 M$ : 675 à 895 | **1 359 à 1 579 organisations** |
| **SAM** (Avalanche, ce que le produit sert aujourd'hui) | C : équipes dont le protocole a > 1 M$ sur Avalanche : 71 (D2, H1) + équipes de L1 avec trésorerie : 10 (D5, prouvées) → borne basse ; borne haute : 71 + 50 L1 (D5) ; borne prudente au seuil 10 M$ : 32 à 121 | **81 à 121 organisations** |
| **SOM** (12 mois) | voir § 3 | **5 à 10 clients payants** par l'écosystème, plus les entrées spontanées (non chiffrables aujourd'hui) |

**Ce que ça dit, sans enjoliver** : sur Avalanche seul, on parle de **quelques dizaines à une centaine** d'organisations adressables. C'est un **marché d'amorçage**. La portabilité EVM (le contrat est en Solidity) multiplie le SAM par 11 à 19 (TAM / SAM = 1 359 / 121 à 1 579 / 81). Le TAM lui-même est une borne basse : il ignore les fonds, les fondations et les entreprises classiques qui paient en stablecoins, faute de source de comptage.

## 3. Le SOM, par un entonnoir explicite (plus de « 10 à 15 % » posés sans raison)

| Étape | Calcul | Résultat |
|---|---|---|
| Organisations contactables la 1re année via l'écosystème | C : cohorte Retro9000 (D6) 30 + équipes de L1 servies par Ash (D5) 10 + équipes > 1 M$ sur Avalanche (D2, H1) 71 = 111 ; **H3** : les présentations par Team1 et la Fondation atteignent ces 111 (c'est leur rôle, et ils sont nos mentors) | **111** |
| Entrent en mode observation gratuit (sans carte bancaire) | **H4** : la moitié accepte un essai gratuit qui ne change rien à leurs paiements (pas de source : hypothèse à **mesurer en B5** sur les équipes du hackathon) | **56** |
| Deviennent payants | C : 56 × 8,9 % à 18,5 % (D10, essai sans carte) = 5,0 à 10,4 | **5 à 10** |
| Revenu année 1 | C : 5 à 10 clients × palier Standard 449 €/mois (B6) × 12 | **27 à 54 k€** |

Ce SOM est petit et c'est normal pour un amorçage : le but de l'année 1 est **les références et les données réelles** (mode observation), pas le chiffre d'affaires. Ce qui le fait monter : le catalogue d'applications Safe (entrées spontanées, non chiffrables), et l'ouverture EVM (× 11 à 19).

## 4. Ce que le jury demandera
- **« Avalanche est-il assez grand ? »** Pour démarrer : 561 protocoles présents, 71 équipes à plus de 1 M$ d'actifs gérés (22 à plus de 10 M$), plus de 50 L1 avec leurs équipes, Safe disponible, un écosystème qui présente. Pour croître : non, et c'est pourquoi le contrat est portable EVM dès le premier jour.
- **« Combien de clients ? »** 81 à 121 organisations adressables sur Avalanche, 1 359 à 1 579 sur l'EVM en borne basse, 5 à 10 clients payants la première année par l'écosystème. Tous les calculs sont dans le dépôt.
- **« D'où viennent vos chiffres ? »** API DeFiLlama lue le 11/10, DeepDAO (à confirmer sur leur site), safe.global/pricing, CertiK, TRM. Ce qu'on n'a pas pu sourcer est exclu, pas inventé.

## 5. Reproduire D1-D3
```bash
curl -s https://api.llama.fi/protocols -o protocols.json
python3 -c "import json;P=json.load(open('protocols.json'));print(len(P), sum(1 for p in P if (p.get('tvl') or 0)>1e7), sum(1 for p in P if 'Avalanche' in (p.get('chains') or []) and (p.get('chainTvls') or {}).get('Avalanche',0)>1e7))"
```

## Sources
D1-D3 : https://api.llama.fi/protocols · https://api.llama.fi/v2/chains · D4 : https://daotimes.com/deepdao-dao-tool-report-for-2025/ · https://eco.com/support/en/articles/14799687-dao-treasury-management-onchain-governance-spend · https://cointelegraph.com/news/dao-treasuries-top-25-billion-for-the-first-time-deepdao · D5-D6 : https://x.com/AvaxDevelopers/status/2066936314247643375 · https://eco.com/support/en/articles/12168599-what-is-avalanche-avax-l1s-and-subnets-in-2026 · D7 : https://www.certik.com/blog/hack3d-the-web3-security-report-2025 · https://www.panewslab.com/en/articles/13c67393-7171-43fe-841e-172243b67bc6 · https://deepstrike.io/blog/defi-hacks-exploits-statistics · D8 : https://safe.global/pricing · D9 : https://www.fireblocks.com/pricing · D10 : https://www.shno.co/marketing-statistics/free-trial-conversion-statistics · https://resources.mailertogo.com/statistics/trial-to-paid-conversion-email-statistics-2025
