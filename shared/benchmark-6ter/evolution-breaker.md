# Évolution de Breaker après le benchmark concurrentiel

11 octobre 2026 — recommandations Codex à l'équipe. Source fournie : `Downloads/business-concurrence.md`, complétée par le benchmark P1, le code courant et les documentations officielles. Les recommandations ne sont pas des choix de conception déjà approuvés.

Les orientations exprimées par l'utilisateur sont : ajouter avec Timéo une capacité d'analyse/simulation et de signataire automatique ; conserver la protection sous contrainte, la lecture Web et des explications simples ; rester sur Avalanche en priorité ; laisser le prix et le multichaîne pour la suite. La question blocage/ralentissement reste ouverte.

## Positionnement recommandé

**Breaker vérifie les effets d'un paiement et son contexte, applique les règles choisies par l'équipe et organise une décision humaine protégée lorsque le risque augmente.**

La cible est pertinente mais non exclusive : Hypernative s'adresse aussi aux équipes de gouvernance et de trésorerie de protocoles. Le segment à tester est plus précis : petites équipes Avalanche, trésorerie multisig, paiements réguliers, pas de spécialiste sécurité disponible pour chaque signature. L'avantage à valider est un déploiement simple et une décision compréhensible à coût prévisible. [Hypernative pour les protocoles](https://www.hypernative.io/industry/protocols).

Ne pas concurrencer au départ une plateforme de conservation MPC, un SOC généraliste, une solution de protection de tous les contrats DeFi ou un fournisseur universel de renseignement. Ne pas demander une migration des fonds dans un nouveau coffre comme condition normale d'adoption : viser une protection intégrée au portefeuille existant. Cette intégration reste à développer et auditer.

## Pouvoir de décision des agents

Conserver la friction graduée par défaut ; permettre un refus automatique sur des violations de règles explicites. Éviter un veto permanent fondé sur une accusation Web isolée ou un score de modèle.

| Situation | Réponse proposée |
|---|---|
| Paiement compatible avec règles et simulation disponibles | Validation de la couche de sécurité ; quorum humain maintenu. |
| Nouveau bénéficiaire ou anomalie isolée | Signataire supplémentaire, alerte et vérification indépendante. |
| Risque corroboré, effets inattendus ou analyse importante indisponible | Mise en revue, attente et nouvel examen ; pas d'exécution automatique au simple terme du délai. |
| Violation certaine d'une règle adoptée par le client | Refus de l'approbation automatique ; correction ou procédure de dérogation autorisée, renforcée et journalisée. |
| Signal de contrainte | Procédure de protection/récupération distincte ; une dérogation ordinaire ne doit pas la neutraliser. |

La dernière ligne implique une revue des interactions entre dérogation et protection sous contrainte. Aucun délai chiffré ou quorum de récupération n'est fixé ici.

Blockaid décrit une règle de rejet des menaces malveillantes non dérogeable. Notre proposition ne doit donc pas être présentée comme une reproduction identique de Cosigner. [Recommended Policies](https://blockaid.io/blog/introducing-recommended-policies-for-cosigner-onchain-operational-security-powered-by-ai).

Architecture à préciser avec Timéo : **moteur EVM de simulation → faits vérifiables → agents d'analyse → moteur de règles → action et explication**. Un modèle de langage ne doit ni inventer les effets d'exécution ni manipuler directement une clé de signature. Les résultats de simulation incluent notamment traces, variations de soldes et stockage. [Tenderly](https://docs.tenderly.co/simulations/overview).

Une signature obligatoire crée un veto et une dépendance de disponibilité ; une signature facultative que le quorum habituel contourne n'apporte pas le contrôle attendu. Le contrat doit formaliser les parcours normal et de récupération. L'agent ne remplace aucun signataire humain requis. En cas de panne, ne pas afficher « sûr » et ne pas signer par défaut : activer le parcours manuel convenu, avec délai et quorum protégé.

L'avis de sécurité doit être lié à la transaction exacte, à la chaîne, au nonce, au portefeuille, à la politique appliquée, au bloc de simulation et à une expiration. Toute modification de transaction exige une nouvelle analyse ; revalider l'état avant exécution lorsque nécessaire. Plusieurs agents utilisant le même modèle et les mêmes sources ne sont pas des preuves indépendantes.

## Informations à ajouter à l'analyse

| Priorité | Données | Utilité et limite |
|---|---|---|
| 1 | Traces d'exécution, transferts effectifs, autorisations de dépense, changements d'admin/modules/signataires | Vérifier ce que l'opération permet réellement, y compris autorisations illimitées et appels indirects. Une simulation réussie n'établit pas l'intention légitime. |
| 1 | Historique propre au client, bénéficiaires approuvés, montants et rythme, opérations en attente | Comparer à l'activité habituelle et prendre en compte des séquences/bundles. Historique potentiellement contaminé : ne pas apprendre automatiquement que tout paiement exécuté est légitime. |
| 1 | Objet du paiement et confirmation authentifiée du bénéficiaire | Comparer le demandé et le simulé ; vérifier un changement d'adresse via un canal indépendant. Données d'entreprise uniquement dans un pilote autorisé, pas dans le dépôt du hackathon. |
| 2 | Code et implémentation des contrats, upgrades, changements de propriétaire, privilèges | Repérer une dépendance qui change après son approbation. Code vérifié et audit publié ne constituent pas une garantie de sûreté. |
| 2 | Avis officiels d'incident, alertes de sécurité de projets, rapports d'audit, listes publiques de risque | Enrichir le contexte ; conserver date, origine et preuve. Deux articles recopiant la même alerte représentent un même événement, pas deux confirmations indépendantes. |
| 2 | Relations on-chain avec adresses signalées | Distinguer lien direct/indirect, montants, distance et services partagés ; filtrer le dusting. Le lien seul n'établit pas une fraude. |
| 3 | Liquidité, prix attendu, slippage, état des oracles et bridges | Pour swaps et interactions DeFi seulement ; ne pas transformer Breaker en agent de placement. |

Hypernative documente déjà réputation d'adresses, traçage multi-sauts et analyse d'URL : la valeur défendable de Breaker est l'usage opérationnel de preuves explicites et contestables, pas l'exclusivité du Web2. [Screening & Intelligence](https://www.hypernative.io/product/screening-intelligence).

Tout signal possède une fraîcheur, une portée, une confiance et une provenance. Une citation vérifiée prouve que le texte existe, pas qu'il est vrai. Les textes externes restent des données, sans pouvoir d'instruire les agents.

## Explication destinée aux signataires

Afficher dans cet ordre : **conclusion → fait déterminant → marche à suivre → preuve et limite**. Exemple fictif : « Ne signez pas en l'état. Ce paiement autorise un contrat inconnu à dépenser tous vos USDC. Demandez une autorisation limitée au montant prévu, puis faites relire par un autre signataire. Voir les effets simulés. »

Réserver scores, traces et détails techniques à une vue secondaire. Afficher explicitement un échec de collecte ou de simulation. Une mise en attente n'est pas une preuve de fraude, et un avis favorable n'est pas une garantie.

## Sortie et récupération

Séparer **résiliation commerciale**, **désactivation technique** et **dérogation pour un paiement**. Le paiement de l'abonnement ne doit jamais conditionner l'accès aux fonds ou aux preuves existantes.

Recommandation : remplacement/révocation du signataire automatique ou du moniteur par une gouvernance client renforcée et temporisée ; notifications à tous ; export des politiques, preuves et journaux ; parcours utilisable sans serveur, API ou accord de Breaker. La récupération doit fonctionner même si le composant défaillant refuse toutes les transactions. Safe avertit qu'un guard cassé peut provoquer un déni de service et demande d'examiner audit et récupération. [Safe Guards](https://docs.safe.global/advanced/smart-account-guards).

**Écart du prototype :** `riskOracle` et `registry` sont immuables dans `ia-2/contracts/TreasuryGuard.sol` ; aucune fonction dédiée de remplacement/désactivation. Le recours unanime sur les paiements raccourcit le délai ordinaire mais ne retire pas ces dépendances. Les fonds peuvent suivre les chemins de paiement autorisés ; cela ne démontre pas une sortie d'urgence indépendante et robuste. Remplacement, récupération et effet de signataires indisponibles doivent être conçus/testés avant l'offre commerciale.

## Audit et preuves d'efficacité

Figer une version et ses droits ; documenter les menaces ; tests unitaires, analyse statique et tests d'invariants : aucun transfert sans quorum humain, avis non réutilisable pour un autre paiement, modèle incapable d'élargir ses droits, récupération indépendante disponible, sortie non bloquée par le fournisseur. [Slither](https://github.com/crytic/slither), [Foundry invariants](https://getfoundry.sh/forge/invariant-testing?highlight=invariant).

Puis audit externe couvrant contrats, intégration au portefeuille, signataire automatique, dérogations, récupération, protection sous contrainte et mises à jour ; corriger, faire vérifier les corrections et publier le commit audité avec les limites. Des bibliothèques auditées ne rendent pas l'assemblage audité ; un scanner ou une revue IA ne remplace pas l'audit indépendant. Le processus OpenZeppelin combine plusieurs méthodes de sécurité. [Security Center](https://contracts.openzeppelin.com/security).

Validation proposée en trois étages :

1. **Historique public horodaté** : transactions, traces, blocs, alertes connues à la date de décision. Rejouer localement incidents pertinents et opérations normales comparables. Les PoC publics peuvent aider mais les exploits de protocole ne sont pas tous des fraudes de trésorerie. [DeFiHackLabs](https://github.com/SunWeb3Sec/DeFiHackLabs).
2. **Évaluation indépendante** : politiques/modèles figés avant test, séparation temporelle et par incident, cas non vus, vérité terrain qualifiée séparément. Une absence de plainte ne prouve pas une transaction saine ; les cas inconnus restent inconnus.
3. **Pilotes d'observation autorisés après hackathon** : propositions avant signature, contexte donné par le client, suivi prospectif et aucune action automatique initiale. Comparer simulation seule, règles seules et système complet.

Mesurer rappel, précision, faux blocages, faux ralentissements, minutes de revue, latence p95/p99, indisponibilité, frais de collecte/analyse et réussite de la récupération. Publier effectifs, périodes, provenance et incertitude. « Aurait détecté avant exécution » est un résultat de rejeu, pas un montant effectivement sauvé. Les données de la démo restent publiques/synthétiques sans données personnelles réelles ; les attaques restent sur des environnements locaux propres.

## Entrée sur le marché et personnalisation

Au départ : **démo courte → diagnostic du portefeuille → pilote en observation → bilan avec le client → activation signée → abonnement**. Ne pas promettre une installation avec protections actives sur des fonds réels tant que le périmètre critique n'est pas audité. La démo doit montrer un paiement normal, une menace, un faux positif corrigé et le parcours de sortie/panne.

Proposer un formulaire court : e-mail professionnel, organisation, portefeuille/chaîne si le prospect souhaite les communiquer, objectif. Sans clé privée, sans signature sur la vitrine. La démo assistée convient au démarrage parce que le paramétrage et la confiance restent à construire ; un essai autonome peut venir après standardisation.

Personnaliser bénéficiaires et contrats habituels, types de paiement, plafonds, horaires, nombre de signatures, délais et canaux. Proposer quelques profils simples et les tester en observation ; revue humaine des suggestions avant activation. Toute baisse de protection ou nouvelle exception requiert une gouvernance client renforcée, notifications et historique. Le service ne change jamais silencieusement les règles ni l'identité des signataires.

Prix laissé ouvert conformément à la demande. B6 devra inclure collecte Web, simulation/RPC, modèles, support, audits amortis et coûts des faux positifs ; le gas seul ne représente pas le coût du service. Pas de promesse d'indemnisation ni de conformité automatique sans cadre dédié.

## Ordre proposé des travaux

1. Simulation des effets + moteur de règles + explication orientée action.
2. Définition des droits de l'agent, dérogations et récupération indépendante.
3. Intégration au portefeuille existant, audit du périmètre critique et évaluation indépendante.
4. Quelques pilotes Avalanche, validation de l'effort opérationnel et de la volonté de payer.
5. Tarification, inscription plus autonome puis extension à d'autres chaînes demandée par les clients.

Le prototype, les choix commerciaux et les travaux en cours de Timéo ne sont pas modifiés par cette note.
