# 2026-10-10 — Romain × Claude : mise en place

**Participants :** Romain, Claude (Claude Code)

## Ce qui a été fait
1. Création du repo et de sa structure : `ia-1/`, `ia-2/`, `shared/`, `JOURNAL.md`, `.gitignore`.
2. Rédaction de `CONTEXTE.md` à partir des slides du kick-off, de la page Luma et du guide candidat Notion (lu en entier).
3. Publication du repo sur GitHub (privé) : `veryromain/hackathon-ia-cyber-romain-timeo`. Invitation de Timéo (`bvtim`).
4. Installation de `gh` (GitHub CLI) et mise en place de la synchro automatique : à la fin de chaque réponse de Claude, `scripts/auto-sync.sh` récupère le travail de Timéo, commite et pousse.

## Décisions
- Track visé : **1 (Fintech) ou 2 (AI for Security)**, à confirmer au checkpoint de sam. 18:30.

## Idée sur la table
Un projet compatible avec les deux tracks : la **supervision d'agents IA qui manipulent de l'argent**.
- **IA n°1, l'agent piégé :** un agent financier connecté par MCP. Un document ou une description d'outil empoisonnée le pousse à tenter un paiement non autorisé. Il sert de générateur de scénarios d'attaque, sur notre propre environnement uniquement.
- **IA n°2, le superviseur :** une passerelle placée entre l'agent et ses outils.
  - Elle loggue chaque appel avec sa chaîne d'autorité.
  - Elle détecte les anomalies (OWASP ASI01, ASI02, ASI03, ASI07).
  - Elle attribue un score de risque, puis demande une validation humaine ou déclenche le kill switch.
  - Elle produit un rapport d'incident (DORA pour le Track 1, SIEM / NIS2 pour le Track 2).
- Le pitch s'adapte ensuite au track choisi.

## Points à vérifier
- Durée des pitchs : le guide Notion et les slides ne disent pas la même chose (à reconfirmer sur place).
- Dotation : 20 k€ selon le guide, 15 k€ selon Luma.
- Le repo devra être accessible au jury au moment du rendu.

## Prochaines étapes
- Valider l'idée avec Timéo.
- Créer le squelette de code des deux IA et un `PLAN.md` jusqu'au rendu de dim. 12:00.

---

## Mise à jour 14:10 — Plan d'action et pitch mentor
- Timéo a rejoint le bon repo (13:51). Son idée : un disjoncteur DeFi (axe 4 du track 1). Voir son compte-rendu.
- Création de `PLAN.md` :
  - le scénario de démo et l'architecture ;
  - la stack : Solidity/Hardhat, Fuji, Python, Bedrock, Streamlit ;
  - la répartition du travail et le planning heure par heure jusqu'à dim. 12:00 ;
  - les limites (attaques en une seule transaction, données synthétiques, DORA non applicable à la DeFi pure, centralisation de la pause, accès Bedrock) ;
  - les idées bonus.
- Création de `shared/pitch-mentor.md` : pitch oral pour le mentor Team1, questions à lui poser et réponses aux objections.
- **Proposition clé :** fusionner les deux idées. Le disjoncteur DeFi de Timéo arrête un agent IA de trésorerie piégé, qui reprend l'idée de Romain.
- **À décider :** valider avec Timéo et le mentor avant 15:30.

## Mise à jour 14:45 — AWS Bedrock et cadrage
- **Cadrage réglementaire :** la démo met en scène un prestataire crypto fictif agréé MiCA, avec un produit « Earn » qui repose sur notre coffre. C'est ce qui rend DORA applicable. Les protocoles DeFi purs restent un second marché, avec un post-mortem public à la place du rapport DORA.
- **Coffre de prêt validé.** Il fait apparaître des signes précurseurs (prix manipulé, rôle donné à une adresse neuve, délai supprimé, jeton douteux accepté), ce qui permet une pause avant le premier dollar sorti.
- **AWS :**
  - `aws login` a échoué : il ne gère pas les comptes Workshop Studio.
  - Les identifiants ont été récupérés via « Get AWS CLI credentials », depuis le presse-papier, sans passer par la conversation.
  - Le Wi-Fi de l'école bloque Bedrock ; ça fonctionne sur le partage de connexion du téléphone.
  - L'appel test à Claude Sonnet 5.5 a réussi.

## Mise à jour 16:35 — Pivot vers l'axe 2 + oracle Web2 → Web3
- **Retour du mentor Team1 :** ne pas faire nous-mêmes la pause (trop centralisé), alerter les signataires, forcer le renouvellement des clés.
- **Timéo propose l'axe 2** (SOC antifraude), appliqué à la trésorerie crypto des entreprises, et réécrit `PLAN.md`.
- **Décision de Romain :** axe 2 validé, **uniquement de la crypto**. **Ajout de l'oracle Web2 → Web3 :**
  - il lit le Web et repère les adresses accusées de fraude (Bedrock + citation vérifiée) ;
  - il les inscrit sur la chaîne ;
  - le garde ajoute de la friction aux paiements vers ces adresses.
- **Points de vigilance notés :** empoisonnement de l'oracle (fausses accusations), injection de prompt, RGPD et scraping (démo sur pages synthétiques), surcharge de travail de Romain (ordre de coupe défini).

## Mise à jour 16:50 — Traçage des fonds
- **Question de Romain :** peut-on bloquer une adresse sur la blockchain, voire toutes celles qui ont reçu ses fonds ?
- **Réponse :** pas au niveau du réseau public. En revanche, le contrat du client peut freiner ses propres paiements vers une adresse.
- **Ajout au plan (§4 ter, tâches T9 et R9, en bonus) :** propagation du risque aux « mules », avec les garde-fous suivants :
  - 1 intermédiaire maximum ;
  - seuil de 10 % des fonds ;
  - dusting ignoré et services connus exclus ;
  - expiration ;
  - friction seulement, jamais de blocage.
- **Écarté par Romain :** le signalement à l'émetteur du stablecoin.
- Timéo est prévenu dans le journal (T9 : événement `token_transfer`).

## Mise à jour vers 17:00 — R1 validé, R8a fait
- **R1 :** générateur de trafic et banc d'essai. Réglage sur 20 graines, test sur 90 graines jamais vues : 99-100 % des fraudes freinées ou arrêtées, 0,2-0,4 % de faux `hold`. Plusieurs bugs corrigés et nouvelles règles ajoutées (voir `shared/validation-R1.md`).
- **R8a :** oracle Bedrock avec citation vérifiée et défense contre l'injection. 6/6 pages pièges justes.
- **Incident :** les modèles 5.5 sont refusés par AWS, d'où un repli automatique sur Sonnet 4.5.

## Mise à jour vers 18:40 — Phase 2 terminée
- R2 (modèle d'anomalie), R8b (corpus de l'oracle, 100 % sur le test) et R5a (tableau de bord) faits.
- **Démo de bout en bout réussie en local : 0 mUSD perdu**, sur la fraude en rafale comme sur l'adresse signalée sur le Web.
- L'intégration a révélé un bug de rechargement du modèle R2, corrigé.
- **Décisions de Romain :**
  - phase business (B1-B8), puis phase produit commercial (P1-P8 : site vitrine et application client) après la démo ;
  - positionnement « uniquement Avalanche » ;
  - consigne modèles : Opus 5.5 ou Fable 5.1, jamais Sonnet (bloqués par le marketplace des organisateurs, d'où un repli sur Opus 4.8).
