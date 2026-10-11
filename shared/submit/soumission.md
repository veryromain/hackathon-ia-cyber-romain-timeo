# Texte de soumission

**Projet :** Breaker

**Équipe :** Romain et Timéo

**Track :** 1 - Fintech Security, axe 4 - détection et réponse aux incidents DeFi

**Dépôt :** https://github.com/veryromain/hackathon-ia-cyber-romain-timeo

**Vidéo :** à compléter dès réception du lien final ; 2-3 minutes.

## Problème et solution

Un portefeuille multisignature peut exécuter une fraude si les personnes qui signent ont été trompées. Breaker analyse les paiements avant leur sortie, explique le risque en français et déclenche une réponse graduée : signature supplémentaire ou délai de vérification. Le mode Cosignataire ajoute un agent capable de signer les paiements jugés sûrs ; son refus peut être dépassé par un quorum humain renforcé après délai. Le client conserve le dernier recours.

## Démonstration

Le prototype tourne sur Avalanche Fuji avec des jetons fictifs. Un paiement habituel passe ; une rafale frauduleuse vers un nouveau bénéficiaire déclenche une mise en attente et permet l'annulation. L'oracle rapproche les adresses de preuves Web vérifiées. Le dashboard présente l'explication et la marche à suivre. Clés de contrainte et d'identité complètent la protection des signataires.

## IA, mesures et preuves

Moteur de règles, Isolation Forest appris sur le trafic normal, simulation ERC-20 par eth_call, agent Bedrock et lecture de pages Web avec citations contrôlées. Sur le jeu final synthétique de 274 paiements : 40 frauduleux et 234 normaux ; 95 % des fraudes freinées ou mises en attente, 78 % mises en attente, 91 % des montants frauduleux en attente, 5,1 % de faux hold. Ces résultats sont propres au corpus de l'équipe ; freiner ne garantit pas empêcher un vol. Tests Python et Solidity, analyse statique et invariants reproductibles dans le dépôt.

## Limites et suite

Contrat non audité indépendamment ; aucun fonds réel. Le contrat de démonstration tient lieu du coffre client : le Guard Safe reste à développer. Simulation partielle, sources Web imparfaites et latences réseau variables. Prochaines étapes : intégration Safe, audit externe et pilotes mesurés chez des organisations volontaires. Pas de certification réglementaire ni de qualification hors garde acquise.

**Pièces :** deck relu (8 slides principales, annexes), fiche de défense d'une page, playbook et support conformité. Le README explique l'installation, les tests hors ligne et la démonstration locale.
