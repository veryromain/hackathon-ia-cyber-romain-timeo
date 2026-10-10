# Analyse du site Breaker — deuxième revue

Base : site publié https://breaker-treasury.espace-de-tr-0859.chatgpt.site/ observé dans Chrome, trois scénarios/explication consultés ; dernière source ia-2/site-vitrine/dist lue dans le dépôt ; JOURNAL, PLAN et mesures relus. Le navigateur bloque les URL file: : pas de nouvelle inspection visuelle de la version locale. Aucun site modifié ni republié à cette étape.

## Diagnostic

Le site publié est une ancienne version (65 % des montants et 1,4 % faux hold), tandis que le dépôt affiche le jeu final (91 % et 5,1 %), les incidents, les preuves Fuji et la FAQ. Première priorité : synchroniser le site publié depuis les fichiers actuels du dépôt, après vérification des preuves du nouveau déploiement Fuji en cours chez Romain. Le code source du site pointe encore sur le portefeuille v1 de 19h29 : conserver ces preuves comme historiques datées ou actualiser avec des transactions réellement observées, sans les présenter comme validation des nouvelles fonctions.

L'identité sombre/verte et la démo sont cohérentes avec les décisions de Timéo. Le principal manque est la précision produit : public cible dans le premier écran, protections distinctives, actions après alerte et accès à un pilote. Les animations ne remplacent pas ces informations.

## Priorités proposées

| Priorité | Changement | Pourquoi |
|---|---|---|
| P0 | Synchroniser la version publiée, dater/versionner les mesures et preuves | Éviter les résultats contradictoires entre vitrine et repo |
| P0 | Corriger « jamais l'accès à vos fonds » et préciser les conditions du recours unanime | Une rotation/expiration peut rendre un quorum indisponible ; les nouveaux mécanismes de contrainte ont aussi des effets sur l'exécution |
| P1 | Ajouter la cible et le produit à la première phrase | Le slogan est mémorable mais trop général seul |
| P1 | Ajouter un bloc « protections concrètes » de quatre cartes | Montrer ce que fait réellement Breaker : adresse sosie, probation, confirmation avant signature, identité froide/révocation |
| P1 | Enrichir la démo : raison précise, preuve, quorum atteint/requis, attente illustrée, prochaines actions humaines | Montrer un parcours de décision au lieu d'un simple score |
| P1 | Un vrai deuxième objectif : discuter d'un pilote avec l'équipe | Les boutons actuels renvoient tous aux sections de la même page ; aucun accès/contact au produit |
| P2 | Préciser l'intégration actuelle et future | Avalanche/Fuji maintenant, prototype autonome ; module Safe/Squads et signature navigateur dans la feuille de route |
| P2 | Ajouter une courte vidéo du dashboard réel avec une transaction vérifiable | Distinguer interface illustrative et démonstration technique |
| P2 | Alléger les répétitions et les effets sur les contenus longs | Donner priorité aux preuves et à la lecture |

## Textes proposés

Titre actuel conservé comme slogan : « Une signature ne suffit pas à faire confiance ».
Phrase produit juste dessous : « La protection antifraude des trésoreries crypto à plusieurs signataires. Pour les protocoles, DAO, startups crypto, fonds et fondations sans équipe de sécurité dédiée. »
Promesse : « Breaker repère les paiements suspects, demande une vérification supplémentaire et donne aux signataires le temps de réagir. »
Boutons : « Tester un scénario » et « Discuter d'un pilote ». Le second ne doit être activé qu'avec un vrai contact/formulaire ; aucun faux formulaire ou prise de contact effectuée à cette étape.

Formulation à remplacer : « Une fausse alerte coûte une signature et un peu de temps, jamais l'accès à vos fonds. » Proposition : « Une alerte peut imposer des signatures supplémentaires et un délai. Vos signataires gardent la décision ; l'exécution reste soumise aux règles du portefeuille. »

## Démo et nouveautés

Quorum : afficher « 2 approbations reçues · 3 requises · 5 signataires » plutôt que « 3 signatures sur 5 », qui confond votes reçus et seuil.
Ajouter une chronologie « proposition → alerte → vérification → décision », une preuve d'adresse/raison, et des actions illustratives « vérifier le fournisseur », « demander un autre signataire », « annuler ». Garder l'étiquette simulation, sans brancher de transactions sur la vitrine.
Les scénarios sosie/clé compromise seraient plus distinctifs que trois simples niveaux de risque. Ne pas ajouter sept innovations en cartes égales : quatre protections expliquées par une menace et une réponse suffisent.
Statuts à afficher : code local testé / démo Fuji datée / prévu. Ne pas annoncer 50 tests et les nouvelles fonctions comme validés sur Fuji sur la seule base du code. Le dernier journal consulté annonce 50 tests et redéploiement en cours, pas une démo nouvelle terminée.
La clé de contrainte/identité froide doit rester une explication secondaire avec ses limites de visibilité sur chaîne publique, sans promettre de discrétion absolue.

## Structure et design

Ordre proposé : promesse+cible → mini preuve datée → démo → protections distinctives → preuve réelle/méthode → intégration et contrôle humain → FAQ → contact pilote.
Garder le fond sombre, le logo et le vert des appels à l'action. Réduire les effets de verre/inclinaison sur les cartes de preuve, éviter les animations simultanées en lecture, accentuer les textes secondaires. Le code gère déjà prefers-reduced-motion : garder cette prise en charge.
Mobile : le CSS masque la navigation sous 760 px sans menu de remplacement ; proposer un petit menu accessible vers démo/preuves/questions. Pas de nouveau test visuel mobile réalisé dans cette revue.
Remplacer le tableau « avertir/bloquer/freiner » trop général par les garanties précises de Breaker ou le raccourcir. Une solution concurrente peut aussi proposer un recours humain : ne pas suggérer que toutes bloquent définitivement.

## À conserver

Cibles startups crypto/fonds/fondations ; cas protocoles/dApps pour leur trésorerie ; entreprises stablecoins en perspective ultérieure. Aucun logo client inventé ni prix sans décision. Réserves synthétique/non audité, sources des incidents, preuves vérifiables et distinction démonstration/production.
