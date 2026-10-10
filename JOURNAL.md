# Journal d'avancement

Ajouter les entrées les plus récentes en haut.

## Modèle d'entrée

### AAAA-MM-JJ HH:MM — ia-1 / ia-2
- **Fait :**
- **En cours :**
- **Bloquant :**
- **Prochaine étape :**

---

### 2026-10-10 14:08 — ia-2 / Timéo (avec Claude)
- **Décision :** Timéo confirme l'**axe 4 du track 1** et me dit que Romain est d'accord. Je travaille désormais uniquement dans ce repo (l'ancien dossier local de Timéo ne sert plus).
- **Accord avec `PLAN.md` :** je prends la répartition proposée (contrat, déploiement Fuji, trafic et attaques dans `ia-2/`) et la stack **Hardhat**. J'avais proposé Foundry à Timéo ; l'argument Windows sans WSL ni Docker est le bon, je m'aligne.
- **Cadrage validé par Timéo :** une seule démo de bout en bout, mais un détecteur conçu pour une classe d'exploits (vidage en plusieurs transactions précédé de signes précurseurs), mesuré sur des variantes non vues mélangées à du trafic normal.
- **En cours :** squelette Hardhat dans `ia-2/`, contrat du coffre, tests locaux, puis proposition du format des événements dans `shared/` pour que Romain puisse démarrer le moniteur.
- **Bloquant :** identifiants AWS (Timéo les attend).
- **Prochaine étape :** format des événements poussé dans l'heure.

### 2026-10-10 14:10 — Romain (avec Claude)
- **Fait :** `PLAN.md` (projet « Breaker », étapes jusqu'au rendu, répartition, limites et risques, idées bonus) et `shared/pitch-mentor.md` (pitch oral de 1 min 30 + questions pour le mentor Team1).
- **Proposition :** partir sur l'idée de Timéo (disjoncteur DeFi, axe 4 du track 1) et y intégrer l'idée de Romain comme vecteur d'attaque (agent IA de trésorerie piégé).
- **Répartition proposée :** Timéo → contrat Vault, déploiement Fuji, trafic et attaques (`ia-2/`). Romain → moniteur, score de risque, module DORA, dashboard (`ia-1/`).
- **Bloquant :** validation à deux + avis du mentor ; accès AWS Bedrock.
- **Prochaine étape :** présenter le pitch au mentor Team1, décider avant 15:30.

### 2026-10-10 13:51 — ia-2 / Timéo (avec Claude)
- **Fait :** Timéo est raccordé à ce repo (clone, hook Stop, boucle de synchro toutes les 5 min). Jusqu'ici son travail partait par erreur sur `veryromain/hackathon-ia-cyber`, un autre repo. Compte-rendu complet dans `conversations/2026-10-10_timeo_choix-axe-et-setup.md`. AWS CLI et Python 3.12 installés chez Timéo.
- **Décision de Timéo :** track 1 ; modèles par AWS Bedrock (crédits du hackathon).
- **En cours :** choix du sujet, non décidé. Idée à l'étude côté Timéo (proposée par Claude) : axe 4 du track 1, un disjoncteur on-chain (testnet Avalanche Fuji) qui met un contrat en pause pendant une attaque simulée, puis classe l'incident selon DORA et préremplit la notification.
- **Bloquant :** deux idées différentes sur la table (supervision d'agents IA financiers côté Romain, disjoncteur DeFi côté Timéo). Pas d'identifiants AWS configurés.
- **Prochaine étape :** trancher le sujet ensemble avant le checkpoint de 18:30.

### 2026-10-10 13:30 — Romain (avec Claude)
- **Fait :** brief du hackathon dans `CONTEXTE.md` (guide Notion + slides), repo publié sur GitHub (privé), synchro automatique mise en place (`scripts/auto-sync.sh`), comptes-rendus de conversation dans `conversations/`.
- **Décision :** on vise le **Track 1 ou le Track 2**, à confirmer au checkpoint de sam. 18:30.
- **Idée proposée :** un seul projet qui marche pour les deux tracks. IA n°1 = agent financier piégé (document ou outil MCP empoisonné qui pousse à un paiement non autorisé). IA n°2 = superviseur / passerelle qui loggue chaque appel d'outil avec sa chaîne d'autorité, détecte (OWASP ASI01/02/03/07), bloque, demande une validation humaine ou coupe (kill switch), et génère le rapport d'incident.
- **Prochaine étape :** valider l'idée avec Timéo, squelette de code des deux IA, `PLAN.md` jusqu'au rendu de dim. 12:00.

### 2026-10-10 — Équipe
- **Fait :** création du repo
