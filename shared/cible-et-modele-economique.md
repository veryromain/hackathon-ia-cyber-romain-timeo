# Cible et modèle économique

> **Décision de Timéo, samedi 10 octobre vers 17h30.** Rédigé par Claude (côté Timéo) pour Romain et son Claude : c'est la matière des slides « cible » et « business model » du deck (livrable L3) et du formulaire du checkpoint.
> Les chiffres de marché viennent d'une recherche web du même jour. Ceux marqués « à vérifier » ne doivent pas aller sur une slide sans contrôle.

## 1. La décision

**Nous visons des organisations réelles qui gardent des millions dans un portefeuille à plusieurs signataires, sans équipe de sécurité pour surveiller ces signataires.** Nous ne protégeons plus le contrat d'une dApp, et nous ne visons pas les grandes plateformes.

| Priorité | Qui | Pourquoi eux |
|---|---|---|
| **1** | **Les équipes de protocoles et les DAO** | Dix à trente personnes, une trésorerie de plusieurs millions tenue par quelques fondateurs. Drift entre dans ce cas. Ils paient des audits de code, mais rien ne surveille leurs signataires |
| **1** | **Les startups crypto, les fonds et les fondations** | Même profil : beaucoup d'argent, pas d'équipe de sécurité |
| **Plus tard** | **Les entreprises classiques qui paient en stablecoins** | Le besoin est fort, mais le marché est encore jeune |

**Les dApps restent donc clientes pour le portefeuille de leur équipe, plus pour leur contrat.**

## 2. Qui nous ne visons pas, et pourquoi

**Les grandes plateformes (Bybit, Coinbase).** Elles ont des équipes de sécurité, des outils comme Fireblocks et des cycles d'achat de plusieurs mois. Elles ne signeront pas avec une startup de deux personnes.

Elles servent d'argument, pas de client : en février 2025, Bybit a perdu environ 1,46 Md$ parce que 3 de ses 6 signataires ont validé une transaction que leur interface affichait falsifiée. Si cela arrive à une plateforme équipée, une équipe de vingt personnes est encore plus exposée.

**La fraude bancaire classique** (virements SEPA, voix clonées, faux documents KYC) reste hors périmètre, comme décidé à 16h35.

## 3. Pourquoi c'est rentable

1. **Un coût par client presque nul.** Environ 0,002 $ de gas par alerte et 0,004 $ par adresse inscrite au registre (mesures dans `shared/frais-gas.md`), plus quelques centimes de Bedrock par explication. Lire la blockchain ne coûte rien. La marge d'un abonnement est donc très élevée.
2. **Un trou dans les prix.** Safe, le portefeuille à plusieurs signataires le plus utilisé, est gratuit mais ne surveille rien par défaut. Fireblocks, l'outil des grands comptes, démarre plusieurs centaines de dollars par mois et monte à des dizaines de milliers par an. Entre les deux, les petites organisations n'ont rien d'abordable qui surveille leurs signataires.
3. **Une distribution peu coûteuse.** En production, notre garde est un module à installer dans Safe (ou dans Squads sur Solana), là où les clients sont déjà. Pas besoin de leur faire changer de portefeuille.
4. **Un produit qui s'améliorerait avec le nombre de clients** (idée de la feuille de route, pas encore construite) : chaque fraude déjouée chez un client alimenterait le registre des adresses signalées, qui protège tous les autres.

### Hypothèse de prix (à discuter)

Abonnement mensuel **par portefeuille protégé**, de quelques centaines d'euros, gas compris, comme le suggérait le mentor Team1. Prestations en plus : paramétrage des règles, revue après incident.

Exemple de calcul, **inventé pour fixer les idées et non tiré d'une étude de marché** : à 500 € par mois, 100 clients font 600 000 € de revenu annuel.

## 4. Repères de marché

| Repère | Valeur | Confiance |
|---|---|---|
| Actifs sécurisés par Safe | Plus de 60 Md$ selon Safe ; 35 Md$ selon un suivi tiers | Chiffre déclaré, sources en désaccord : à vérifier |
| Comptes Safe créés | Plus de 61 millions | La plupart sont minuscules : **ce n'est pas la taille du marché** |
| Revenu annualisé de Safe | Plus de 10 M$, annoncé en février 2026 | Annonce de la fondation Safe |
| Trésorerie de la fondation Ethereum passée sur Safe | Environ 650 M$, octobre 2025 | Presse spécialisée |
| Entrée de gamme de Fireblocks | 699 à 999 $ par mois | Comparateurs qui ne s'accordent pas : à confirmer sur leur site |
| Offres entreprise de Fireblocks | À partir d'environ 36 000 $ par an | Un seul comparateur : à vérifier |
| Nombre d'organisations avec une trésorerie importante en multisig | **Pas trouvé** | Ne pas inventer de chiffre ; le dire si le jury demande |

## 5. La concurrence, à citer honnêtement

- **Safe** : gratuit, standard du marché, mais sans surveillance par défaut. C'est notre canal de distribution plus qu'un concurrent.
- **Hypernative, Blockaid** : contrôles avant signature pour les portefeuilles à plusieurs signataires. Cité de mémoire, **non vérifié aujourd'hui**.
- **Fireblocks** : moteur de règles complet, pour les grands comptes.

**Ce qui nous distingue :** l'oracle qui lit les signalements de fraude du Web et les rend utilisables sur la chaîne ; la friction appliquée par le portefeuille du client lui-même, sans que nous détenions de pouvoir sur ses fonds ; des alertes expliquées en clair à des signataires qui ne sont pas des experts en sécurité ; un prix à la portée d'une équipe de vingt personnes.

## 6. Ce que cette décision change dans le projet

| Élément | État | À faire |
|---|---|---|
| Contrats, relais, moteur de score, oracle | **Rien à changer** : ils servent n'importe quelle organisation qui a un portefeuille à plusieurs signataires | — |
| Formulaire du checkpoint (R7a) | Le texte parlait d'« entreprises » en général | Texte mis à jour en section 8 de `PLAN.md` |
| Deck (L3), fiche de défense (L4) | À écrire | Reprendre les sections 1 à 5 de ce document |
| Jeu de données : l'entreprise fictive NovaTreasury paie un loyer, des cotisations sociales et la TVA en stablecoin | **Peu crédible pour la nouvelle cible**, et aucune administration n'accepte ces paiements aujourd'hui | Timéo relibellera en trésorerie d'une équipe de protocole (contributeurs, auditeurs, infrastructure, subventions, primes de bug) à la prochaine régénération du jeu. La structure et les fraudes ne changent pas ; les adresses et les hash changeront. **Romain sera prévenu avant** |
| Slide conformité (L6) | À écrire | La cible prioritaire n'est en général pas une entité financière régulée : l'angle DORA devient secondaire. Angles à faire valider par le mentor KPMG : filtrage des contreparties (LCB-FT), AI Act et supervision humaine, traçabilité des décisions sur la chaîne |

## Sources

- Safe, chiffres déclarés : https://www.safe.global/security
- Fondation Safe, revenu annualisé : https://safefoundation.org/blog/safe-10m-revenue-100m-target-2030
- Trésorerie de la fondation Ethereum sur Safe : https://www.theblock.co/post/375708/just-in-ethereum-foundation-moves-entire-650m-treasury-to-safe-multisig
- Suivi tiers des actifs de Safe : https://altfins.com/crypto-screener/safe-safe
- Tarifs de Fireblocks (comparateurs) : https://costbench.com/software/crypto-custody/fireblocks et https://www.rfp.wiki/crypto/payments-commerce/crypto-b2b-payments/infinite/fireblocks-payments
- Piratage de Bybit : https://www.nccgroup.com/research/in-depth-technical-analysis-of-the-bybit-hack/
- Piratage de Drift : https://www.halborn.com/blog/post/explained-the-drift-hack-april-2026
