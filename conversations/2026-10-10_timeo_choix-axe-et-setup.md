# 2026-10-10 — Timéo × Claude : choix de l'axe et mise en place

**Participants :** Timéo, Claude (Claude Code), Codex (ChatGPT) en second agent

## Ce qui a été fait
1. Lecture du guide candidat et des pages des tracks 1 et 2, résumées dans un brief (même contenu que `CONTEXTE.md`).
2. Mise en place d'un dossier de travail local partagé entre Claude Code et Codex, avec un journal de passation et un fichier de décisions.
3. Outils installés sur la machine de Timéo (Windows 11) : AWS CLI 2.37, Python 3.12. `git`, `gh` et `node` étaient déjà là. Pas de Docker.
4. Recherche d'exemples d'exploits DeFi pour nourrir l'idée de l'axe 4 (voir plus bas).
5. Raccordement à ce repo : clone dans `~/hackathon-ia-cyber`, hook Stop et boucle de synchro toutes les 5 minutes.

**Erreur à connaître :** jusqu'à 13h45, tout le travail de Timéo partait sur un autre repo, `veryromain/hackathon-ia-cyber` (sans le suffixe `-romain-timeo`), pour lequel Timéo avait reçu une invitation à 11h50. Il contient 8 commits de Timéo et rien de Romain. Rien n'a été perdu ; ce repo ne sert plus.

## Décisions de Timéo
- **Track 1 (Fintech Security)**, décidé vers 12h10. À confirmer ensemble au checkpoint de 18h30.
- Les modèles passeront par **AWS Bedrock**, avec le compte de crédits du hackathon. Aucun identifiant configuré pour l'instant ; région et modèles activés inconnus.
- **Sujet : non décidé.**

## Idée sur la table côté Timéo : axe 4 du track 1
Un « disjoncteur » on-chain relié à la conformité DORA.
- Nous déployons notre propre contrat (coffre ou pool de prêt) sur le testnet Avalanche Fuji.
- Un script joue du trafic normal, puis une attaque simulée contre ce contrat.
- Un moniteur repère les signes précurseurs et le début du vidage, puis met le contrat en pause par un rôle de gardien aux pouvoirs bornés.
- L'incident est classé selon les critères DORA et la notification est préremplie avec les preuves on-chain. La rédaction passe par un modèle Bedrock, chaque chiffre est relié à une transaction.
- La levée de la pause exige une validation humaine.

Pourquoi cet axe : Timéo a deux à trois ans de pratique intensive des cryptomonnaies sur Solana ; peu d'équipes auront cette compétence ; Team1 Avalanche est mentor du track ; la démo donne des métriques nettes (temps de détection, part des fonds sauvés, faux positifs sur le trafic normal rejoué).

Réserves :
- L'expérience de Timéo est sur Solana, Fuji est une chaîne EVM (contrats en Solidity).
- Le trafic normal et les attaques sont à fabriquer nous-mêmes.
- La détection seule existe déjà sur le marché (Forta, Hypernative, Hexagate). La partie originale est le lien entre l'incident on-chain et la déclaration DORA.
- Un disjoncteur ne sert à rien contre une attaque qui tient dans une seule transaction (Beanstalk, Euler). Le scénario de démo doit être un vidage étalé sur plusieurs transactions ou précédé de signes (Drift, Nomad, Ronin).
- Les délais de notification DORA sont cités de mémoire, à vérifier.

Exemples vérifiés par recherche web :
- Drift Protocol (Solana, 1er avril 2026, environ 280 à 285 M$) : préparation dès le 11 mars, puis 31 retraits en 12 minutes. Source : https://www.halborn.com/blog/post/explained-the-drift-hack-april-2026
- Cetus (Sui, 22 mai 2025, environ 223 M$) : les validateurs ont gelé environ 162 M$. Source : https://cointelegraph.com/news/sui-validators-freeze-majority-stolen-funds-220m-cetus-hack

Timéo a soumis cette idée à ChatGPT pour un avis critique ; retour non encore consigné.

## Autre option étudiée
Axe 1 (poste de l'analyste LCB-FT) : c'est le seul axe où un jeu de données synthétique étiqueté existe déjà (« IBM Transactions for Anti Money Laundering » sur Kaggle, licence à vérifier), donc des chiffres de détection rapidement. Moins différenciant.

## Questions ouvertes pour Romain
- **Quel sujet ?** Ton idée (supervision d'agents IA financiers, axe 3 du track 1 ou track 2) et celle de Timéo (disjoncteur DeFi, axe 4) sont deux projets différents. Il faut en choisir un avant le checkpoint de 18h30.
- **Quel track ?** Timéo a choisi le track 1 ; ton journal dit « track 1 ou 2 ». Ton idée tient dans le track 1 par l'axe 3.
- As-tu les identifiants AWS des crédits du hackathon, la région et les modèles Bedrock activés ?
- Le repo `veryromain/hackathon-ia-cyber` peut-il être supprimé ou archivé, pour éviter une nouvelle confusion ?

## Prochaines étapes
- Trancher le sujet avec Romain.
- Importer dans `ia-2/` les notes du dossier de travail local de Timéo (journal de passation, décisions).
- Configurer les identifiants AWS (hors Git) et tester un appel Bedrock.
- Squelette de code une fois le sujet choisi.
