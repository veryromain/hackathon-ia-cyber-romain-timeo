# B4 — Concurrence : produit, prix, cible, mise sur le marché

> Romain (avec Claude), 11/10 vers 00:25. Sources vérifiées par recherche Web le 11/10 ; ce qui n'a pas pu être confirmé est marqué **(non confirmé)**. Base : `shared/concurrents-et-inspiration.md` et `shared/analyse-site-v2.md` de Timéo.

## 1. Le tableau comparatif

| | **Hypernative Guardian** (dans Safe) | **Blockaid Cosigner** | **Safe Shield** (natif Safe{Wallet}) | **Fireblocks** | **Breaker** |
|---|---|---|---|---|---|
| **Ce que ça fait** | Politiques de transaction appliquées par un *guard* Safe : plafond de montant, liste blanche de contreparties, contrats non vérifiés signalés, signataires en plus pour certaines actions ; **blocage** des transactions à haut risque | Un **signataire automatique** (portefeuille 1-sur-2) ajouté au multisig : simule la transaction sur le *calldata* réel, et **refuse de cosigner** si elle viole la politique, même si tous les humains ont approuvé | Analyse avant exécution (Blockaid) et simulation (Tenderly) dans l'interface Safe : **avertit**, alerte sur les adresses sosies, n'agit pas | Plateforme de garde MPC complète : moteur de règles, circuits d'approbation, rôles, approbation mobile | Garde qui **freine sans jamais bloquer** (signature en plus, délai), explication en clair, oracle Web2→Web3, traçage, clé d'identité froide |
| **Réponse à une transaction suspecte** | Bloquée (ou signataires en plus) | **Refusée** par le cosignataire ; dérogation humaine possible | Avertissement seulement | Bloquée par la politique | Ralentie ; les signataires décident ; jamais verrouillée |
| **Cible** | Gestionnaires d'actifs, institutions, fonds ; client cité : Ethena | Grandes trésoreries, plateformes (intégré chez Utila ; cité après l'incident Bitget de sept. 2026) | Tous les utilisateurs de Safe | Entreprises, plateformes d'échange, banques | **Équipes de protocoles, DAO, startups crypto, fonds et fondations sans équipe de sécurité**, sur **Avalanche** |
| **Prix** | **Non public** : « contactez votre représentant Safe » ; arrangement négocié | **Non public** | Inclus dans Safe ; couverture « selon le plan » (Safe Pro) **(non confirmé)** | **Essentials 999 $/mois** (6 mois max, 1 M$ de volume trimestriel, 0,20 % au-delà) ; **Pro/Entreprise à partir de 36 000 $/an** | Hypothèse : quelques centaines d'euros par mois et par portefeuille (B6) |
| **Chaînes** | EVM (Safe) | Safe, Fireblocks, Squads | Safe | Multichaîne | Avalanche uniquement (choix) |
| **Signataire sous contrainte / personne protégée** | Non | Non | Non | Non | **Oui** (clé d'identité froide) |
| **Lecture du Web pour signaler des adresses** | Non (listes de risque internes) | Non (threat intel propriétaire) | Non | Non | **Oui** (IA + citation vérifiée + sources publiques) |
| **Explication en clair pour un non-expert** | Partielle (motif du risque) | Motif du risque | Avertissement technique | Oui, pour des équipes formées | **Oui**, 2 à 4 phrases + action à faire |
| **Verrou de sortie** | Retirer le guard : timelock de 24 h | Retirer le cosignataire | — | Contrat annuel | Le client garde tous les pouvoirs ; nous n'en avons aucun |

Autres acteurs, plus éloignés : **Fordefi** (simulation des effets avant signature, pour institutions), **Utila** (gestion de trésorerie MPC, intègre Cosigner), **Squads** (multisig Solana avec délais et limites, hors périmètre Avalanche), **Forta Firewall** (protection au niveau de la chaîne, pas du portefeuille), **Chainalysis** (score de risque des adresses, direct et indirect, fournisseur de données).

## 2. Ce qu'il faut dire honnêtement
- **Les briques ne sont pas uniques :** plafonds, signataires en plus, simulation, listes d'adresses existent chez Guardian, Cosigner et Fireblocks. Timéo l'a écrit dans `shared/comparaison-autres-blockchains.md` ; on ne prétend pas avoir inventé le multisig surveillé.
- **Le concurrent le plus proche est Blockaid Cosigner**, pas Guardian : il vise exactement la signature en aveugle (Bybit) et cite Drift comme cas. Sa philosophie est l'inverse de la nôtre : **un robot qui refuse de signer** ; nous, **des humains qui décident avec du temps et des explications**.
- **« Ne pas prétendre être seuls à conserver un recours humain »** (note de Timéo) : Cosigner a une voie de dérogation. Notre différence est que nous **ne pouvons pas bloquer**, par construction.

## 3. Ce qu'on fait mieux (nos trois différences défendables)
1. **La friction sans blocage, pour des équipes sans RSSI.** Guardian et Fireblocks sont vendus à des institutions, sans prix public, par des commerciaux. Une équipe de 20 personnes avec 5 M$ en multisig n'a aujourd'hui que Safe Shield (qui avertit) ou rien.
2. **Le pont Web2 → Web3 et le traçage** : des signalements lus sur le Web (citation vérifiée, croisement des sources), des listes publiques (OFAC, ScamSniffer), les mules. Les concurrents utilisent leur propre threat intel, fermée.
3. **La protection de la personne, pas seulement de la clé** : clé d'identité froide (révocation immédiate, signature sous contrainte), « ce que vous signez vraiment », adresses pièges. Aucun des quatre ne le fait.

## 4. Ce qu'on fait moins bien (à assumer)
- Pas de simulation de la transaction (Blockaid, Tenderly, Fordefi) : on note le *contexte* du paiement, pas ses *effets* on-chain. À ajouter en feuille de route.
- Une seule chaîne, un seul actif, un contrat non audité, pas d'intégration Safe encore.
- Pas de données réelles : nos chiffres viennent de jeux synthétiques (mode observation prévu).

## 5. Comment ils abordent le marché (sites et applications)
- **Guardian, Cosigner, Fordefi, Utila : vente institutionnelle.** Pas de prix, « demander une démo », études de cas avec de gros noms, intégrations (Safe, Fireblocks, Squads) mises en avant. Le produit s'installe *dans* le portefeuille que le client a déjà.
- **Fireblocks : prix affiché pour l'entrée de gamme** (999 $/mois), essai limité à 6 mois, puis montée en gamme. Modèle SaaS classique.
- **Safe : gratuit, standard du marché**, protections intégrées fournies par des partenaires. C'est le **canal de distribution** à viser (module / guard), pas un concurrent.
- **À reprendre pour Breaker** (site vitrine P2, déjà entamé par Timéo) : promesse en une phrase, le problème avec Bybit et Drift, « comment ça marche » en trois étapes, les chiffres de la démo, **un prix affiché** (notre différence face aux institutionnels), « réserver une démo ». À éviter : promettre « zéro fraude ».

## Sources
- Safe × Hypernative : https://safe.global/blog/safe-partners-with-hypernative-to-launch-enterprise-security-integration · https://www.hypernative.io/insights/blog/safe-and-hypernative-partner-to-bring-enterprise-grade-security-to-multisig · https://help.safe.global/articles/7610775969-understanding-safe-shield-guardian-by-hypernative
- Blockaid Cosigner : https://blockaid.io/cosigner · https://www.blockaid.io/blog/cosigner-the-onchain-security-layer-your-multisig-is-missing-blind-signing · https://blockaid.io/blog/285m-gone-how-blockaids-cosigner-could-have-protected-drift-protocol · https://utila.io/blog/utila-integrates-blockaid-cosigner/
- Safe Shield : https://safe.global/security · https://www.blockaid.io/blog/safe-wallet-gets-even-safer-introducing-blockaid-integration · https://help.safe.global/articles/3861480988-what-is-address-poisoning-and-how-does-safewallet-battle-it
- Fireblocks : https://www.fireblocks.com/pricing · https://breet.io/business/research/reviews/fireblocks
- Avis indépendant sur Safe + Guardian : https://www.onchainden.com/blog/safe-wallet-review
