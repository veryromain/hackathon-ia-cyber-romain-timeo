# Benchmark concurrentiel pour le produit Breaker

11 octobre 2026 — tâche P1 de la phase 6 ter, complément à B4. Codex, à la demande de Timéo.

Breaker doit rendre un paiement suspect facile à examiner : ce qui part, pourquoi le risque augmente, les preuves et la décision attendue. Safe est la référence pour la coordination des signataires ; Hypernative Guardian et Blockaid Cosigner sont les concurrents les plus proches pour les contrôles avant exécution ; Fireblocks sert de référence pour les circuits d'approbation et l'offre commerciale.

Le positionnement proposé est **une protection graduée pour les petites équipes sur Avalanche, avec des signalements sourcés et contestables**. L'explication lisible, les politiques de transaction, l'IA et le traçage ne constituent pas, seuls, une exclusivité.

## Périmètre et niveau de preuve

Sites publics, débuts des parcours d'inscription et documentation officielle consultés le 11 octobre 2026, avec neuf captures conservées. Les applications privées de Hypernative, Blockaid et Fireblocks n'ont pas été utilisées avec un compte client : leurs capacités sont documentées, leurs performances et leur ergonomie en exploitation ne sont pas mesurées ici. Aucun compte créé, aucune demande de démo envoyée, aucun portefeuille connecté.

Cette livraison termine **P1**, pas toute la phase 6 ter. P3, P7, le rapport mensuel de P6 et les réglages de P8 restent des travaux distincts. Les choix proposés ci-dessous doivent être arbitrés par l'équipe ; ils ne sont pas des décisions prises par Timéo.

## Promesse et parcours commercial

| Produit | Promesse et rôle | Prix public observé | Entrée dans le produit |
|---|---|---|---|
| **Safe Wallet / Safe Pro** | Coordination de trésorerie multisig ; Safe Shield présente les contrôles de risque. | Comptes Safe gratuits ; Pro mensuel : **Starter 189 € HT/mois, 2 comptes** ; **Business dès 669 € HT/mois, 5 comptes**, jusqu'à 20 selon l'offre ; Enterprise personnalisé. Essai annoncé : 30 jours. [Tarifs](https://www.safe.global/pricing) | Bouton d'essai → application → onglets Safe Pro / My accounts → création du Workspace, étape 1 sur 4, nom de l'organisation. [Application](https://app.safe.global/welcome/spaces), captures 01–03. |
| **Hypernative Guardian / Transaction Guard** | Vérification avant signature, simulation et politiques : autoriser, refuser ou envoyer en revue. [Produit](https://www.hypernative.io/product/transaction-guard) | Aucun montant affiché sur les pages consultées ; prise de contact nécessaire. | Démo → formulaire : nom, e-mail, entreprise, région, projet, origine du contact ; Telegram proposé. Essai gratuit annoncé après démo, durée non précisée. [Parcours](https://www.hypernative.io/book-a-demo), captures 07–08. |
| **Blockaid Cosigner** | Couche de contrôle dans le processus multisig/MPC ; simulation des effets, politiques et workflows. Intégrations mises en avant : Safe, Fireblocks, Squads, Utila. [Produit](https://blockaid.io/cosigner) | Aucun montant affiché sur les pages produit et démo consultées ; demander une offre. | Formulaire de démo : nom, e-mail, entreprise, fonction, sujet ; lien de prise de rendez-vous facultatif, consentement marketing distinct. [Parcours](https://blockaid.io/demo), captures 05–06. |
| **Fireblocks** | Infrastructure de portefeuilles MPC et opérations d'entreprise ; offre plus large qu'un garde sur un multisig existant. | **Essentials 999 $/mois, jusqu'à 6 mois** ; 1 M$ de volume sortant trimestriel, 0,20 % au-delà ; 5 utilisateurs et 2 workspaces. Custom dès **36 000 $/an**. [Tarifs](https://www.fireblocks.com/pricing) | Get started → e-mail professionnel, Google ou Microsoft ; démo pour offre personnalisée, sandbox pour développeurs. Captures 04 et 09. |

Ces prix portent sur des périmètres différents. Ils donnent des repères commerciaux, pas une preuve que Breaker serait plus rentable ou moins cher à service égal. L'abonnement Safe Pro et un add-on partenaire peuvent se cumuler : le prix Pro n'est pas le tarif Guardian. [Description des services Safe Pro](https://help.safe.global/articles/4148651106-safe-pro-service-descriptions).

## Écrans et notifications

| Référence | Écrans ou mécanismes documentés | Notifications | Conséquence pour Breaker |
|---|---|---|---|
| **Safe** | Workspace : comptes, paiements en attente, membres, carnet partagé, Security Hub. Connexion e-mail/Google distincte de l'autorité de signer. [Workspace](https://help.safe.global/articles/7904066821-faq-enterprise-workspace) | Push Web configurables par compte ; demandes de confirmation soumises à une vérification du signataire. [Notifications](https://help.safe.global/articles/9750082418-how-to-start-receiving-web-push-notifications-in-the-web-wallet) | Séparer accès à l'application et signature ; ouvrir la notification sur le paiement précis, conserver les décisions de tous les collègues dans une chronologie. |
| **Safe Shield Copilot** | Contrôles intégrés à la transaction, sévérité, contexte destinataire/contrat, simulation disponible ; indisponibilité d'un contrôle signalée. [Copilot](https://help.safe.global/articles/6434169802-understanding-safe-shield-copilot) | Affichage dans le parcours d'examen ; ne pas confondre ces indicateurs avec un canal d'alerte externe. | Afficher chaque contrôle et sa fraîcheur ; différencier « aucun risque détecté » et « analyse indisponible ». |
| **Guardian** | Politiques gérées dans Hypernative, résultats dans la confirmation Safe. Installation accompagnée par transaction signée, puis configuration des règles. [Guardian](https://help.safe.global/articles/7610775969-understanding-safe-shield-guardian-by-hypernative) | Slack, Telegram, Discord, API. Même source. | Garder les règles compréhensibles et la notification proche du canal de travail de l'équipe. Commencer avec un canal fiable plutôt qu'une longue liste de connecteurs. |
| **Cosigner** | Page publique : graphe de simulation, moteur de politiques, workflows automatiques. Ce sont des visuels de présentation, pas une session client testée. [Produit](https://blockaid.io/cosigner) | Alertes automatiques annoncées ; les canaux précis de Cosigner ne sont pas établis par la page consultée. | Montrer le chemin de la décision. Ne pas présenter notre détection contextuelle comme une simulation de tous les effets de la transaction. |
| **Fireblocks** | Opérations initiées depuis la console ; approbation indépendante sur mobile, détails lisibles, simulation, biométrie/PIN. [Livre blanc sécurité, février 2026](https://www.fireblocks.com/wp-content/uploads/2026/02/Fireblocks_Security_Whitepaper_Feb2026.pdf) | Push d'approbation en temps réel ; événements API de création, statut et approbation. [Webhooks](https://fireblocks.readme.io/reference/webhooks-structures-eventtypes) | Une alerte doit préciser l'action à faire et son responsable. Prévoir l'historique de livraison et la reprise après un échec. |

## Ce qu'on reprend et ce qu'on fait autrement

| Sujet | À reprendre | Proposition pour Breaker |
|---|---|---|
| **Premier écran du site** | Promesse concrète, cible nommée, action principale visible, illustration du produit. | « Examinez les paiements suspects avant que votre trésorerie parte. » Sous-titre : équipes Avalanche, signatures supplémentaires et délai selon le risque. Bouton principal : voir la démo ; second : demander une démo. |
| **Preuves** | Études de cas et résultats associés à un scénario. | Afficher les résultats Breaker avec la mention « tests synthétiques » et un lien vers le protocole de mesure ; séparer la démo Fuji des performances attendues en production. |
| **Tarifs** | Grille lisible, limites et conditions à côté du prix. | Définir en B6 le nombre de portefeuilles, volume de recherches Web, support et frais externes inclus. Afficher « pilote sur devis » tant que le prix n'est pas validé. Ne pas annoncer une économie à périmètre incomparable. |
| **Inscription** | Étapes courtes et progrès visible ; identité applicative distincte des clés de signature. | Organisation → portefeuille Avalanche → signataires et notifications → observation → activation explicite. L'accès par e-mail ne donne jamais le droit de signer. |
| **Accueil client** | File de paiements et statut commun à l'équipe. | Priorité aux paiements à examiner, avec montant, destinataire, signatures manquantes, délai restant et personne chargée du suivi. Les graphiques viennent après. |
| **Détail du paiement** | Contexte, raisons, effets et décisions dans le même parcours. | Bloc « pourquoi » + preuve Web cliquable : URL, citation, date de collecte, sources, expiration, contestation. Puis exigences on-chain et actions signées. |
| **Alerte** | Lien direct, sévérité et action attendue. | Exemple : « Paiement de 25 000 mUSD en attente — nouveau destinataire signalé — examen par un autre signataire requis ». Lien vers le détail ; ne pas déclencher une signature depuis l'e-mail. |
| **Réglages** | Politiques et circuits d'approbation explicites. | Montrer les réglages effectifs lus sur la chaîne, les planchers et toute modification en attente de signatures. Un administrateur de l'application n'est pas un administrateur du contrat. |
| **Retour client** | Boucle d'amélioration, revue humaine. | Conserver vraie/fausse alerte, commentaire et délai de réaction. Un retour client ou une annulation seuls ne prouvent pas une fraude : une diffusion collective doit rester qualifiée, sourcée et contestable. |

Ces propositions sont une fiche produit, sans changement du site ni de l'application dans cette tâche.

## Différences à défendre et affirmations à corriger

1. **Le Web2 n'est pas une exclusivité.** Hypernative revendique des données on-chain/off-chain et la surface d'attaque Web2 ; sa gamme inclut analyse d'URL et traçage multi-sauts. Notre différence à montrer est la chaîne de preuve précise : page collectée, citation vérifiée, consolidation, hash, expiration et recours. L'absence du même mécanisme chez les concurrents n'est pas démontrée. [Plateforme Hypernative](https://www.hypernative.io/), [Screening & Intelligence](https://www.hypernative.io/product/screening-intelligence).
2. **Les politiques adaptatives et l'IA existent ailleurs.** Cosigner propose en bêta des règles suggérées à partir de l'historique, testables avant activation et approuvées par un humain. Son article du 30 juillet 2026 décrit une règle de rejet des menaces malveillantes non dérogeable : ne pas promettre une dérogation universelle chez Cosigner. [Recommended Policies](https://blockaid.io/blog/introducing-recommended-policies-for-cosigner-onchain-operational-security-powered-by-ai).
3. **Safe est aussi un concurrent produit.** Sa coordination et ses contrôles recoupent notre futur espace client ; il reste également un canal d'intégration possible. La FAQ Workspace encore présentée comme gratuite est dépassée sur le tarif par l'application, qui indique le passage à Pro le 6 octobre, et la grille actuelle. Voir captures 01–02.
4. **Distinguer les couches Safe.** Copilot fournit des indicateurs ; Guardian peut bloquer. La documentation Safenet actuelle décrit un avertissement permettant encore l'exécution, alors que la page tarifs annonce un enforcement futur. Présenter séparément ce qui est disponible et ce qui est annoncé. [Safenet](https://help.safe.global/articles/5038961301-what-safenet-checks-and-what-the-results-mean).
5. **Avalanche est notre périmètre, pas un monopole concurrentiel.** Blockaid affiche sur sa page Cosigner un témoignage Ava Labs sur son intégration Core. Le choix d'une seule chaîne réduit notre complexité ; sa valeur commerciale reste à valider auprès des clients. [Cosigner](https://blockaid.io/cosigner).
6. **Éviter « nous ne bloquons jamais » sans préciser le rôle.** La promesse défendable est que le moniteur ajoute des exigences sans signer ni déplacer les fonds. Délais, signatures, gel par les signataires et protections particulières peuvent empêcher une exécution. Le code et les droits du contrat priment sur le slogan. Référence : `ia-2/contracts/TreasuryGuard.sol` dans le dépôt commun.
7. **Ne pas revendiquer l'absence de protection humaine chez les concurrents.** Nous pouvons montrer nos protections effectivement démontrées ; aucune recherche ici ne prouve que les autres n'en ont aucune. Le mécanisme de signature sous contrainte reste hors de la vitrine, conformément à la décision de Timéo du 10 octobre à 22:46.

## Maquette et priorités après P1

Pour le hackathon, le couple utile est **site existant + écran de paiement détaillé**. À améliorer dans cet écran : le résumé du paiement, les exigences effectives, la preuve sourcée et l'état d'avancement de la recherche. Le rapport mensuel et la facturation ne doivent pas retarder la démo.

L'essai Apify du journal à 00:35 a pris **2 min 23 pour cinq pages**, au-delà du délai d'examen de 30 secondes de la démo. Afficher « recherche en cours », « résultat disponible », « sources insuffisantes » ou « service indisponible ». Une recherche vide n'est pas un certificat d'innocuité. Le rafraîchissement préalable des bénéficiaires connus et le traitement des inconnus sont à arbitrer ; aucune nouvelle règle n'est activée ici.

| Suite | Livrable proposé | Critère d'acceptation |
|---|---|---|
| **P3 — espace client** | Connexion, organisation et portefeuille, puis rôles. | Consultation possible sans clé de signature ; aucune signature permise par le seul compte applicatif. |
| **P4 — actions** | Signature navigateur et suivi de transaction. | Montant/destinataire affichés avant signature ; résultat confirmé sur la chaîne, échec visible. |
| **P5 — notifications** | Un canal opérationnel, puis escalade. | Un signataire reçoit un lien vers le bon paiement ; erreurs de livraison visibles ; délai mesuré. |
| **P6 — rapport** | Alertes, retours, délais, montants et méthode. | Distinguer montants mis en attente, annulations et pertes réellement évitées ; ne pas compter toute alerte comme une fraude. |
| **P7 — observation** | Collecte et score sans réponse automatique, puis activation. | L'écran et le relais indiquent le mode ; activation autorisée par les signataires, jamais par un réglage purement visuel. |
| **P8 — réglages** | Règles, délais, seuils et carnet de confiance. | Affichage fidèle au contrat et historique des changements. |

## Captures et limites d'inspection

| Capture | URL et observation |
|---|---|
| [01 — prix Safe](captures/01-safe-prix.jpg) | https://www.safe.global/pricing — mode mensuel, montants HT. |
| [02 — entrée Safe](captures/02-safe-entree-app.jpg) | https://app.safe.global/welcome/spaces — comptes gratuits / workspaces Pro et aperçu d'organisation. |
| [03 — création Workspace](captures/03-safe-inscription.jpg) | https://app.safe.global/welcome/create-space — étape 1/4, sans inscription. |
| [04 — prix Fireblocks](captures/04-fireblocks-prix.jpg) | https://www.fireblocks.com/pricing — Essentials et Custom, limites affichées. |
| [05 — Cosigner](captures/05-blockaid-cosigner.jpg) | https://blockaid.io/cosigner — promesse et schéma de refus avant exécution. |
| [06 — démo Blockaid](captures/06-blockaid-demo.jpg) | https://blockaid.io/demo — formulaire de qualification, non soumis. |
| [07 — Hypernative](captures/07-hypernative-accueil.jpg) | https://www.hypernative.io/ — positionnement institutionnel et illustration. |
| [08 — démo Hypernative](captures/08-hypernative-demo.jpg) | https://www.hypernative.io/book-a-demo — formulaire et essai accompagné, non soumis. |
| [09 — inscription Fireblocks](captures/09-fireblocks-inscription.jpg) | https://console.fireblocks.io/v2/signup — e-mail professionnel / Google / Microsoft, sans inscription. |

Captures desktop ; pas de validation mobile ni d'audit d'accessibilité. Les visuels marketing ne prouvent pas un comportement d'application. Un second chargement de Cosigner a renvoyé une erreur 504 ; les conclusions reposent sur la page précédemment chargée et la documentation, sans mesure de disponibilité. Certains changements de page ont produit une capture de l'écran précédent : les fichiers 01, 02, 06 et 08 ont été revérifiés/corrigés avant livraison.

