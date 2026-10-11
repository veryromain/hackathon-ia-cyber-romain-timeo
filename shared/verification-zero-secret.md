# Vérification « zéro secret » (livrable L8)

Règle du hackathon : zéro secret dans le dépôt, le jury vérifie. Ce document dit ce qui a été vérifié, comment le refaire, et ce qui reste à faire avant de donner l'accès au jury.

## Résultat du 11 octobre, 7 h 40, sur le PC de Timéo

**Aucun secret dans les 256 fichiers suivis ni dans les 161 commits de l'historique (toutes branches).**

| Secret | Où il vit | Fichiers suivis | Historique |
|---|---|---|---|
| Clé Bedrock (`AWS_BEARER_TOKEN_BEDROCK`) | `.env` à la racine, ignoré par Git | absent | absent |
| Jeton Apify (`APIFY_TOKEN`) | `.env` à la racine, ignoré par Git | absent | absent |
| Phrase secrète des comptes Fuji (`FUJI_MNEMONIC`) | `ia-2/.env`, ignoré par Git | absente | absente |
| Clés privées des 20 premiers comptes dérivés de cette phrase | nulle part sur le disque | absentes | absentes |

Les deux seuls fichiers `.env` jamais ajoutés au dépôt sont `.env.example` et `ia-2/.env.example`, qui ne contiennent que des noms de variables sans valeur.

## Comment c'est vérifié

```bash
cd ia-2 && npm run zero-secret
```

Le script `ia-2/scripts/zero-secret.js` n'affiche jamais une valeur. Il fait cinq recherches :

1. il lit les vraies valeurs des fichiers `.env` du poste et dérive les clés privées des comptes Fuji ;
2. il cherche chaque valeur dans les fichiers suivis et dans tout l'historique (`git log --all -S`) ;
3. il liste les fichiers `.env` suivis aujourd'hui ou ajoutés un jour ;
4. il cherche des motifs génériques dans toutes les lignes ajoutées de l'historique : clés AWS et Bedrock, jetons Apify, GitHub, Telegram, Slack, Stripe, Google, clés Anthropic et OpenAI, blocs de clé privée, variables du type `PRIVATE_KEY=…` ou `SMTP_PASSWORD=…` ;
5. il cherche chaque secret par morceaux de 20 caractères, au cas où un retour à la ligne l'aurait coupé (transcription, journal).

Il sort avec le code 1 s'il trouve quoi que ce soit. Le script a été essayé sur un dépôt d'essai contenant un faux secret : il le trouve.

## Ce que cette vérification ne couvre pas

- **Les secrets du Mac de Romain.** La recherche part des valeurs du poste où elle tourne. Si le Mac a d'autres valeurs (jeton Telegram, mot de passe SMTP, autre clé Bedrock), seuls les motifs génériques du point 4 les couvrent ici. **Romain doit lancer la même commande sur le Mac.**
- **Un secret d'un format inconnu qui ne serait plus dans aucun `.env`.** Les motifs du point 4 couvrent les formats courants, pas tous.
- **GitHub lui-même** : descriptions de demandes de fusion, tickets, pages wiki. Le dépôt n'en a pas à ce jour.

## Ce qui est dans le dépôt et qui n'est pas un secret

- `ia-2/deployments/fuji-comptes.json`, `fuji.json` : adresses publiques des comptes de test et des contrats. Aucune clé.
- Les comptes de la chaîne locale Hardhat : clés de test publiques, identiques pour tout le monde, sans valeur.
- `shared/listes-publiques.jsonl`, `ia-1/oracle/sources_cache/` : listes publiques de sanctions et d'adresses de phishing.
- `conversations/` : transcriptions de nos sessions de travail. Vérifiées par la recherche ci-dessus, y compris par morceaux.

## Données personnelles (règle voisine)

Aucune adresse e-mail dans les fichiers suivis. Les jeux de données sont synthétiques. Les pages Web collectées par l'oracle restent dans `ia-1/oracle/collecte_cache/`, ignoré par Git ; `shared/flags-rejetes.jsonl` (citations de pages réelles) a été retiré du suivi le 11 octobre.

## Avant de donner l'accès au jury

1. Romain lance `npm run zero-secret` sur le Mac.
2. Relancer la commande une dernière fois après le dernier commit, juste avant midi.
3. Choisir l'accès : inviter le jury comme lecteur du dépôt privé, ou rendre le dépôt public. **Rendre public est irréversible en pratique** (le dépôt peut être copié dans la minute) et expose aussi `conversations/` et le détail de la clé de contrainte, que Timéo a voulu garder hors du site.
4. Si le dépôt devient public : activer dans GitHub « Secret scanning » et « Push protection » (réglages du dépôt, gratuits pour un dépôt public). Seul le propriétaire du dépôt, Romain, peut le faire.

## Si un secret fuit quand même

Le révoquer d'abord (une clé publiée doit être considérée comme perdue, même une minute), en générer une nouvelle, et seulement ensuite nettoyer l'historique. La clé Bedrock du hackathon expire d'elle-même au bout de quelques heures ; le jeton Apify et la phrase Fuji n'expirent pas.
