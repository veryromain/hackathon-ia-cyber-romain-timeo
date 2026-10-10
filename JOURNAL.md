# Journal d'avancement

Ajouter les entrées les plus récentes en haut.

## Modèle d'entrée

### AAAA-MM-JJ HH:MM — ia-1 / ia-2
- **Fait :**
- **En cours :**
- **Bloquant :**
- **Prochaine étape :**

---

### 2026-10-10 16:31 — ia-2 / Timéo (avec Claude)
- **Fait :** nouveau `PLAN.md`, rédigé à la demande de Timéo pour l'**axe 2 du track 1** : garde antifraude pour une trésorerie d'entreprise tenue par un portefeuille à plusieurs signataires. **Romain, c'est une proposition : lis-la et dis ce que tu changes.** Ton plan de l'axe 4 est archivé tel quel dans `shared/archive/PLAN-axe4.md`.
- **Répartition proposée (consigne de Timéo : le plus technique côté blockchain pour lui) :** Timéo → contrat `TreasuryGuard`, relais chaîne/fichiers, trafic normal, scénarios de fraude, Fuji. Romain → moteur de score, explication et rapport par Bedrock, tableau de bord, évaluation, livrables écrits.
- **Interface entre les deux :** deux fichiers JSON Lines, `events.jsonl` (Timéo vers Romain) et `alerts.jsonl` (Romain vers Timéo). Romain n'a pas besoin de la blockchain pour avancer.
- **En cours :** format des événements et fichier d'exemple (tâche T1), puis le contrat.
- **Bloquant :** accord de Romain sur le plan ; formulaire du checkpoint à 18:30 (texte proposé en section 8 du plan).

### 2026-10-10 16:26 — ia-2 / Timéo (avec Claude)
- **Annonce de Timéo :** après l'échange avec le mentor, il veut passer de l'axe 4 à l'**axe 2 du track 1** (SOC antifraude à l'ère de l'IA générative : prise de contrôle de compte, arnaques au paiement, fraude au président ; réponse graduée par authentification renforcée, mise en attente, gel, alerte). **Accord de Romain non confirmé ici ; `PLAN.md` n'est pas modifié.**
- **Lecture proposée par Claude, à confirmer par Timéo :** l'axe 2 appliqué à une **trésorerie d'entreprise sur la chaîne**, pas à la fraude bancaire classique. Le client est une entreprise qui gère ses fonds par un portefeuille à plusieurs signataires. Chaque transaction proposée est notée avant son exécution (destinataire jamais vu, montant hors habitudes, rafale, signatures anciennes, changement récent des signataires ou du seuil). Réponse appliquée par le portefeuille du client lui-même : signatures supplémentaires exigées, mise en attente avec délai, gel par les signataires, alerte. Plafond par période sans autorisation supplémentaire et expiration des clés, les deux idées du mentor. L'outil ne peut qu'ajouter de la friction ; il ne valide, ne bloque ni ne déplace rien.
- **Pourquoi cette lecture :** elle garde notre avantage crypto, le cas Drift (signataires trompés, soit une fraude au président version crypto), Avalanche, Hardhat, Bedrock et le format des événements. La version bancaire classique (voix clonées, faux documents KYC) nous ferait repartir de zéro, sans données pour mesurer la détection.
- **Coût du changement :** le coffre de prêt `BreakerVault` (environ deux heures de travail) ne sert plus tel quel ; `ia-1/` ne contient pas encore de code. La grille de notation est la même pour tous les axes du track 1.
- **Bloquant :** confirmation de Timéo sur la lecture (trésorerie sur la chaîne ou fraude bancaire classique) et accord de Romain, avant le checkpoint de 18:30.

### 2026-10-10 16:23 — ia-2 / Timéo (avec Claude)
- **Correction :** j'avais mal lu la note du mentor. Timéo, présent, précise sa conclusion : **nous ne faisons pas nous-mêmes la transaction de pause** (trop centralisé) ; on **alerte les signataires** du protocole ; on **impose un renouvellement périodique de leurs clés** (quinze jours par exemple).
- **Proposition de Claude, non décidée** (détail en section 4 de `shared/retour-mentor-team1.md`) : garder la pause mais la laisser aux mains du protocole. Le moniteur alerte et prépare la transaction, les signataires la valident ; le protocole choisit entre alerte seule, pause validée par ses signataires, ou pause automatique qu'il délègue lui-même. Ajouter au contrat une expiration des rôles pour forcer le renouvellement des clés.
- **Pourquoi ne pas tout enlever :** le guide cite la pause du contrat dans le playbook de l'axe 4, la réponse pèse 20 %, et l'alerte seule existe déjà sur le marché.
- **Bloquant :** décision de Romain et Timéo sur ce cadrage avant de toucher au contrat. **Romain, ta lecture de l'échange avec le mentor ?**

### 2026-10-10 16:18 — ia-2 / Timéo (avec Claude)
- **Fait :** note Granola du mentor Team1 lue et confrontée au plan dans `shared/retour-mentor-team1.md`. Frais de gas mesurés (`npm run gas` dans `ia-2/`) : une pause coûte environ 34 000 gas, soit **0,002 $** au prix relevé à 16h17.
- **Ce que le mentor confirme :** l'architecture en deux composantes, Drift comme cas de référence, la transaction sur la chaîne (c'est notre `escalate`).
- **Proposition, à valider à deux :** ajouter un **plafond de sorties permanent** dès le niveau Normal (idée du mentor, 10 % par période). **Refuser** le déplacement automatique des fonds : il casse notre règle « le gardien ne touche jamais aux fonds » et contredit le conseil MiCA du même mentor.
- **Attention pitch :** ne pas dire qu'Avalanche aurait empêché Drift (faux, un expert le relèvera) ; dire que la pause y est définitive en une à deux secondes pour une fraction de centime. Chiffre de Drift : 280 à 285 M$ d'après nos sources, pas 255 M$.
- **À confirmer avec le mentor KPMG :** le cadrage DORA (client régulé exposé au coffre, nous comme prestataire tiers de services TIC).
- **Prochaine étape :** plafond permanent dans le contrat si validé, puis scripts de déploiement, de trafic et d'attaque.

### 2026-10-10 15:37 — ia-2 / Timéo (avec Claude)
- **Fait :** en partage de connexion, **Bedrock fonctionne chez Timéo** avec sa clé d'API : appel réel réussi sur `us.anthropic.claude-opus-5-5`.
- **Écart avec Romain :** `claude-sonnet-5-5` et `claude-haiku-5-5` sont refusés avec la clé de Timéo (« private marketplace eligibility »). Détail dans `shared/aws-bedrock.md`.
- **Pour Romain :** dans le module DORA, lire le modèle dans la variable `BEDROCK_MODEL_ID` (valeur par défaut au choix) au lieu de l'écrire en dur.
- **Rappel :** la clé de Timéo expire vers 03:28 dimanche.

### 2026-10-10 15:34 — ia-2 / Timéo (avec Claude)
- **Diagnostic Bedrock chez Timéo :** la clé est en place, c'est bien le réseau qui bloque. Sur le Wi-Fi de l'école, le nom `bedrock-runtime.us-west-2.amazonaws.com` se résout, mais la connexion TLS est coupée (« Connection was reset »), alors que `sts.us-west-2.amazonaws.com` répond. Même constat que Romain.
- **Bloquant :** Timéo doit passer en partage de connexion pour que je valide sa clé. Je n'ai pas cherché à contourner le filtrage de l'école.

### 2026-10-10 15:33 — ia-2 / Timéo (avec Claude)
- **Fait :** clé d'API Bedrock de Timéo rangée dans `.env` à la racine du repo (ignoré par Git, vérifié par `git check-ignore`). Modèle `.env.example` ajouté à la racine ; `.gitignore` complété par `!.env.example`, car la règle `.env.*` ignorait aussi les modèles (celui de `ia-2/` n'était jamais parti). Méthode décrite dans `shared/aws-bedrock.md`.
- **Bloquant :** l'appel de test échoue depuis le Wi-Fi de l'école (« Connection was closed »), comme l'a vu Romain. La clé n'est donc **pas encore validée**. Elle expire vers **03:28 dimanche** : à renouveler avant le rendu.
- **À savoir :** Timéo a collé cette clé dans sa conversation avec Claude. Elle n'est dans aucun fichier suivi par Git.
- **Prochaine étape :** retester Bedrock en partage de connexion ; côté code, script de déploiement, trafic normal et attaque autonome.

### 2026-10-10 14:45 — Romain (avec Claude)
- **Fait :** accès AWS de l'événement configuré chez Romain (profil local `hackathon`, région us-west-2). **Bedrock fonctionne** : appel réel réussi avec `us.anthropic.claude-sonnet-5-5`. Procédure dans `shared/aws-bedrock.md`.
- **Bloquant découvert :** le Wi-Fi de l'école bloque `bedrock*.amazonaws.com`. Il faut passer par le partage de connexion du téléphone (ou CloudShell). À signaler aux organisateurs.
- **Décision :** coffre **de prêt** validé (plus de signes précurseurs, donc une pause avant le premier dollar sorti). Cadrage réglementaire : client fictif agréé MiCA exposé au coffre (voir `PLAN.md`).
- **Pour Timéo :** récupérer tes propres identifiants dans Workshop Studio (voir `shared/aws-bedrock.md`), ne pas partager les clés.

### 2026-10-10 14:15 — ia-2 / Timéo (avec Claude)
- **Fait :** projet Hardhat dans `ia-2/` avec les contrats `BreakerVault` (coffre de prêt, disjoncteur à trois niveaux Normal / Limited / Paused, rôles séparés), `SimplePool` (pool d'échange qui sert d'oracle de prix) et `MockToken`. **13 tests passent** sur la chaîne locale (`cd ia-2 && npm install && npm test`).
- **Scénario rejoué dans les tests**, inspiré de Drift : faux jeton au prix gonflé, prise du rôle de configuration, délai de sécurité ramené à zéro, listing, puis vidage en 31 emprunts. Sans disjoncteur le coffre est vidé ; pause après 3 emprunts : plus de 90 % des fonds restent ; pause au listing : rien ne sort.
- **Écart par rapport à `PLAN.md`, à valider par Romain :** coffre **de prêt** plutôt que simple coffre de dépôts et retraits. Raison : cela donne au moniteur des signes précurseurs avant le premier retrait (rôle accordé à une adresse neuve, délai abaissé, collatéral à liquidité dérisoire). La pause, le plafond de sorties et le gardien borné du plan sont là.
- **Pour Romain :** `shared/format-evenements.md` (proposition de format des événements et des alertes, à amender), `shared/abi/` (ABI pour web3.py), `shared/dora-notes.md` (délais et critères DORA : la notification initiale sous 4 h après classement et 24 h après prise de connaissance est confirmée ; le reste est à lire dans les textes).
- **Synchro :** la boucle automatique a committé mon travail en cours de route (commits `[auto]` de 14:09 et 14:14) ; rien de cassé, mais les messages de commit ne disent pas ce qu'ils contiennent.
- **Bloquant :** identifiants AWS ; portefeuilles de test et AVAX du faucet pour Fuji.
- **Prochaine étape :** script de déploiement (local puis Fuji), générateur de trafic normal et script d'attaque autonome qui écrivent les événements au format proposé.

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
