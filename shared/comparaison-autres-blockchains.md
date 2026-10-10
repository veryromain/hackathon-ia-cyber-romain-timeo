# Breaker face aux solutions d'autres blockchains

Recherche du 10 octobre 2026 par Codex, demandée par Timéo. Sources officielles ; leurs capacités sont déclarées par les éditeurs, sans test indépendant. Complément fonctionnel de B4, pas une étude commerciale complète.

## Notre référence

Selon PLAN.md, SUIVI.md et le code : garde de trésorerie multisig sur Avalanche, score comportemental, signatures supplémentaires et attente selon le risque, oracle Web avec citation vérifiée et registre expirant. Le moniteur ne signe pas les paiements. Contrats, relais, score, oracle et dashboard ont des validations locales documentées. Le journal de Romain à 18:41 rapporte une démo intégrée réussie en local ; une production auditée reste à établir. T9/R9 sont des bonus prévus : traçage limité à un intermédiaire et protections contre les petits transferts parasites.

## Cibles à conserver dans le benchmark

Précision de Timéo : la comparaison couvre toutes les cibles déjà décidées.

| Priorité | Organisations | Besoin visé |
|---|---|---|
| Maintenant | Équipes de protocoles, dApps et DAO | Protéger la trésorerie de leur équipe et les décisions de ses signataires. Drift sur Solana est un exemple du besoin ; le PoC reste sur Avalanche. |
| Maintenant | Startups crypto, fonds et fondations ayant ce profil | Beaucoup de fonds en crypto, plusieurs signataires, pas d'équipe de sécurité dédiée. |
| Plus tard | Entreprises classiques qui paient en stablecoins | Besoin jugé fort par Timéo, marché encore jeune. |

Pour chaque concurrent, vérifier son adéquation à ces organisations : installation, paramétrage, prix par portefeuille, alertes lisibles et gestion des faux positifs. Les dApps sont visées pour la trésorerie de leur équipe.

## Comparaison

| Projet / écosystème | Capacités documentées | Lecture pour Breaker |
|---|---|---|
| Safe Shield / Ethereum et EVM | Détection du risque dans le parcours de signature. | Le multisig et l'avertissement ne sont pas notre nouveauté. [Safe](https://safe.global/wallet) |
| Hypernative Guardian / Safe, EVM | Politiques avant exécution, revue ou blocage, exigences de plusieurs signataires, alertes et piste d'audit. | Concurrent le plus proche. Ne pas le réduire à un blocage binaire. Notre borne de pouvoir et l'intégration de preuves Web sont à comparer plus précisément. [Documentation](https://help.safe.global/articles/7610775969-understanding-safe-shield-guardian-by-hypernative) |
| Squads / Solana | Multisig, délai global sur les transactions ; limites autorisant des dépenses déléguées sans approbation complète. | Le délai n'est pas nouveau. Notre intérêt est de l'adapter au risque de chaque paiement ; ne pas confondre leur délégation plafonnée avec notre plafond déclenchant des signatures supplémentaires. [Délais](https://docs.squads.so/main/navigating-your-squad/settings/time-locks), [limites](https://docs.squads.so/main/navigating-your-squad/settings/spending-limits) |
| Forta Firewall / Ink, OP Stack | Contrôle au séquenceur avant inclusion ; modules choisis par la chaîne, filtrage des transactions. | Même objectif préventif, autre niveau : infrastructure de chaîne chez Forta, trésorerie cliente chez nous. [Déploiement Ink](https://forta.org/blog/forta-firewall-on-op-enterprise-a-sequencer) |
| Chainalysis / multichaîne | Évaluation du risque des adresses et de leur exposition directe ou indirecte. | T9/R9 sont une version restreinte du traçage existant ; notre valeur serait son utilisation dans le parcours des signataires. [Wallet screening](https://www.chainalysis.com/glossary/wallet-screening/) |

Squads a aussi annoncé des hooks d'approbation dynamique et des délais adaptatifs dans v5. Cette page décrit un développement annoncé : elle ne suffit pas à établir sa disponibilité actuelle. [Annonce v5](https://squads.xyz/blog/squads-protocol-v5).

## Ce qui peut nous distinguer

- Un parcours destiné aux équipes de protocoles, dApps et DAO, aux startups crypto, fonds et fondations Avalanche ayant une forte trésorerie sans équipe de sécurité dédiée. C'est notre cible ; l'absence de concurrents sur ce segment n'est pas démontrée.
- Une preuve Web compréhensible, vérifiée dans sa source, contestable et expirante, qui déclenche une friction dans le portefeuille. La citation prouve la présence de la phrase, pas la véracité de l'accusation. L'exclusivité de cette combinaison n'est pas démontrée.
- Un moniteur aux pouvoirs limités : il ne déplace pas les fonds. Cela ne prouve pas que tout verrouillage est impossible : gel, expiration des clés, indisponibilité des signataires et répétition de signalements restent à analyser.
- Un prix simple et une installation facile seraient des avantages commerciaux ; aucun prix compétitif ni intégration à Safe en production n'est démontré aujourd'hui.

Avalanche est un choix de spécialisation et de distribution, pas une barrière technique : des mécanismes Solidity similaires peuvent être portés à d'autres réseaux EVM.

## Formulation de pitch proposée

« Breaker protège les trésoreries des équipes de protocoles et dApps, des DAO, startups crypto, fonds et fondations de l'écosystème Avalanche sans équipe de sécurité dédiée : il combine les habitudes de paiement et des signalements Web sourcés pour demander une signature supplémentaire ou laisser un délai de vérification, sans donner au moniteur le pouvoir de transférer les fonds. »

Ne pas dire : premier multisig intelligent, seul outil de signatures adaptatives, invention du traçage, ou protection infaillible contre le verrouillage.

## Information à conserver

L'ancien oracle de sanctions Chainalysis illustre le pont données externes → contrat, mais il est déprécié et n'a plus reçu de mise à jour après le 18 mars 2026. Ne pas le recommander comme service actif. [Avis officiel](https://go.chainalysis.com/chainalysis-oracle-docs.html).

## Prochaines vérifications de B4

Prix et offres exactes, réseaux pris en charge par chaque fonctionnalité, installation réelle, pouvoir du fournisseur et retrait du garde, expérience des petites équipes, notifications et parcours d'inscription. Les résultats de nos tests synthétiques ne sont pas comparables à des métriques commerciales sur trafic réel.