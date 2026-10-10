# Instructions pour Claude — Hackathon Secure Horizons

Repo partagé entre Romain et Timéo. Le brief complet est dans `CONTEXTE.md`.

## Suivi des conversations (obligatoire)
À chaque étape significative d'une conversation (décision, nouveau fichier, avancée de code) :
1. Mettre à jour (ou créer) le compte-rendu de la conversation dans `conversations/AAAA-MM-JJ_<prénom>_<sujet>.md` : ce qui a été fait, les décisions, les idées, les prochaines étapes. Rédiger un résumé, pas une copie brute de la conversation.
2. Ajouter une entrée en haut de `JOURNAL.md` si une décision ou une avancée concerne toute l'équipe.
3. La synchro avec GitHub est automatique (hook Stop → `scripts/auto-sync.sh`). Pour la forcer : `./scripts/auto-sync.sh "message"`.

## Règles
- Zéro secret dans le repo (clés API, tokens) : utiliser `.env`, qui est ignoré par git. Le jury vérifiera.
- Aucune donnée personnelle réelle : uniquement des données synthétiques ou publiques.
- Aucune action contre un système réel : les attaques sont simulées uniquement sur notre propre environnement.
- Rendu figé dim. 12:00.
