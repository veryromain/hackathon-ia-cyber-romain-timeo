# Journal d'avancement

Ajouter les entrées les plus récentes en haut.

## Modèle d'entrée

### AAAA-MM-JJ HH:MM — ia-1 / ia-2
- **Fait :**
- **En cours :**
- **Bloquant :**
- **Prochaine étape :**

---

### 2026-10-10 13:55 — ia-2 / Timéo (avec Claude)
- **Fait :** Timéo est raccordé à ce repo (clone, hook Stop, boucle de synchro toutes les 5 min). Jusqu'ici son travail partait par erreur sur `veryromain/hackathon-ia-cyber`, un autre repo. Compte-rendu complet dans `conversations/2026-10-10_timeo_choix-axe-et-setup.md`. AWS CLI et Python 3.12 installés chez Timéo.
- **Décision de Timéo :** track 1 ; modèles par AWS Bedrock (crédits du hackathon).
- **En cours :** choix du sujet. Timéo penche pour l'axe 4 du track 1 : un disjoncteur on-chain (testnet Avalanche Fuji) qui met un contrat en pause pendant une attaque simulée, puis classe l'incident selon DORA et préremplit la notification.
- **Bloquant :** deux idées différentes sur la table (supervision d'agents IA financiers côté Romain, disjoncteur DeFi côté Timéo). Pas d'identifiants AWS configurés.
- **Prochaine étape :** trancher le sujet ensemble avant le checkpoint de 18:30.

### 2026-10-10 13:30 — Romain (avec Claude)
- **Fait :** brief du hackathon dans `CONTEXTE.md` (guide Notion + slides), repo publié sur GitHub (privé), synchro automatique mise en place (`scripts/auto-sync.sh`), comptes-rendus de conversation dans `conversations/`.
- **Décision :** on vise le **Track 1 ou le Track 2**, à confirmer au checkpoint de sam. 18:30.
- **Idée proposée :** un seul projet qui marche pour les deux tracks. IA n°1 = agent financier piégé (document ou outil MCP empoisonné qui pousse à un paiement non autorisé). IA n°2 = superviseur / passerelle qui loggue chaque appel d'outil avec sa chaîne d'autorité, détecte (OWASP ASI01/02/03/07), bloque, demande une validation humaine ou coupe (kill switch), et génère le rapport d'incident.
- **Prochaine étape :** valider l'idée avec Timéo, squelette de code des deux IA, `PLAN.md` jusqu'au rendu de dim. 12:00.

### 2026-10-10 — Équipe
- **Fait :** création du repo
