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
