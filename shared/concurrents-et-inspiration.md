# Concurrents et références pour le produit Breaker

Complément B4/P1, 10 octobre 2026. Capacités vérifiées dans les sources officielles ; suggestions d'inspiration à valider par inspection des interfaces, pas un audit de leur UX.

| Référence | Rapport avec Breaker | Inspiration proposée |
|---|---|---|
| [Hypernative Guardian / Safe](https://help.safe.global/articles/7610775969-understanding-safe-shield-guardian-by-hypernative) | Concurrent direct : politiques de transaction, revue, blocage et signatures multiples, EVM. | Écran des règles, état de la transaction, alertes et piste d'audit. |
| [Blockaid Cosigner](https://blockaid.io/blog/cosigner-the-onchain-security-layer-your-multisig-is-missing-blind-signing) | Concurrent direct : signataire automatique qui simule et analyse avant de cosigner ; voie de dérogation humaine. | Effets attendus du paiement, motif du risque et parcours de dérogation. Ne pas prétendre être seuls à conserver un recours humain. |
| [Safe Wallet](https://safe.global/wallet) | Portefeuille et couche d'intégration potentielle dans les écosystèmes EVM. | Paiements à approuver, signataires, historique et parcours de signature. |
| [Squads / Solana](https://docs.squads.so/main/navigating-your-squad/settings) | Alternative pour trésoreries multisig, avec délais et limites. | Gestion des membres, seuils et délais pour petites équipes. |
| [Fireblocks](https://www.fireblocks.com/platforms/governance-and-policies) | Plateforme multichaîne de contrôle des opérations avec politiques et circuits d'approbation. | Rôles, montants, destinataires autorisés et séparation des responsabilités. |
| [Fordefi](https://docs.fordefi.com/developers/simulate-transactions) | Simulation des effets, risques et approbateurs requis avant signature. | Résumé lisible de ce qui va sortir du portefeuille et des autorisations accordées. |
| [Utila](https://utila.io/product/treasury-management) | Gestion de trésorerie institutionnelle via portefeuille MPC. | Vue des portefeuilles, opérations et organisation de la trésorerie. |
| [Forta Firewall / Ink](https://forta.org/blog/forta-firewall-on-op-enterprise-a-sequencer) | Protection au niveau de la chaîne, plus éloignée de notre portefeuille client. | Présenter clairement les étapes détection → décision → application de la règle. |
| [Chainalysis](https://www.chainalysis.com/glossary/wallet-screening/) | Évaluation du risque direct et indirect des adresses, multichaîne. | Provenance des fonds et affichage des éléments justifiant le risque. |

Blockaid est déjà présent sur Avalanche via [Core](https://blockaid.io/blog/blockaid-bolsters-security-on-avalanche-with-core-integration). La spécialisation Avalanche n'établit pas une absence de concurrence.

Ordre proposé pour concevoir le site et le dashboard : Safe et Squads pour le parcours multisig ; Hypernative et Blockaid pour la présentation des contrôles et des preuves ; Fireblocks pour les réglages. Fordefi sert de référence pour la lisibilité avant signature.

Conserver toutes nos cibles : équipes de protocoles/dApps et DAO, startups crypto, fonds et fondations sans équipe de sécurité ; entreprises en stablecoins plus tard. Drift sur Solana illustre le besoin, sans être un concurrent ni un support annoncé de Breaker.

À vérifier ensuite : prix réels, fonctionnalités par réseau, installation, retrait du contrôle, écrans et parcours client. Les différences commerciales de Breaker restent des hypothèses.