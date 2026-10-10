# Prompt à coller dans le Claude Code de Timéo (boucle de débrief, miroir de celle de Romain)

```
/loop 15m Débrief d'équipe. 1) git pull --rebase dans ~/hackathon-ia-cyber, puis lis shared/debrief-romain.md (section « Dernier quart d'heure ») et les commits de Romain (veryromain) depuis le dernier débrief (git log, git diff --stat, ses entrées dans JOURNAL.md). Écris-moi UN PARAGRAPHE en français (5 à 8 lignes) sur ce que Romain a avancé côté business, ce qu'il a décidé, ce qu'il demande, et ce que je pourrais ne pas comprendre ou pourrais lui proposer ; s'il n'y a rien de nouveau, une ligne. 2) Dans le sens inverse, mets à jour shared/debrief-timeo.md (section « Dernier quart d'heure », datée) avec UN PARAGRAPHE sur ce que j'ai avancé côté technique depuis le dernier débrief (harnais de clés API, oracle, site, contrat…), pour que le Claude de Romain le lise ; puis commit "[shared] débrief Timéo HH:MM" et push. Ne modifie rien d'autre.
```
