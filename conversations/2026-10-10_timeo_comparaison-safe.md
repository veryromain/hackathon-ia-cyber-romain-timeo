# Notre garde comparé à Safe — 10 octobre 2026, 17h50

Question de Timéo : en quoi notre système de sécurité est-il similaire à Safe ?

## Ce qui est pareil

- **La base.** Un contrat détient les fonds et n'exécute un paiement qu'avec M signatures sur N. Ni Safe ni nous ne gardons les fonds du client.
- **Le point de contrôle avant exécution.** Safe prévoit depuis sa version 1.3.0 un « guard » : un contrat consulté avant et après chaque transaction, en plus des signatures. Notre moniteur et notre registre jouent ce rôle.
- **Un score calculé hors chaîne, appliqué sur la chaîne.** C'est le schéma de Safe Shield avec Guardian de Hypernative (annoncé le 20 novembre 2025) : chaque transaction est comparée à des règles, puis laissée passer, signalée ou bloquée par un guard.
- **Les changements de signataires et de seuil** sont votés par les signataires eux-mêmes.
- **Plafond et délai** existent autour de Safe sous forme de modules (limites de dépense, modificateur Delay de Zodiac). Ces deux points viennent de ma connaissance de Safe, pas de la recherche d'aujourd'hui.

## Ce qui diffère

| Point | Safe | Notre `TreasuryGuard` |
|---|---|---|
| Signatures | Hors chaîne, réunies puis envoyées en une transaction | Sur la chaîne, une transaction par étape : le moniteur voit le paiement dès sa proposition |
| Ce qu'il exécute | N'importe quel appel de contrat, tout actif | Le transfert d'un seul jeton |
| Réponse au risque | Le guard laisse passer ou bloque | Signature en plus, puis attente d'une heure ; jamais de blocage |
| Panne ou compromission du contrôle | Un guard défaillant peut verrouiller les fonds (avertissement de la documentation Safe) | Le moniteur ne peut que relever un niveau ; l'unanimité fait sauter l'attente |
| Délai, gel, expiration des clés | Absents du contrat de base | Intégrés |
| Maturité | Audité, des dizaines de milliards | Prototype de 396 lignes, non audité |

## Correction à faire dans nos documents

Nous écrivons que Safe « ne surveille rien par défaut ». C'est dépassé : Safe Shield analyse chaque transaction dans l'interface de Safe (signaux de Blockaid, Tenderly et Hypernative, simulation, destinataire comparé au carnet d'adresses).

La phrase se trouve dans `PLAN.md` (section 1 bis), `shared/cible-et-modele-economique.md` (lignes 29 et 53), `SUIVI.md` (B4) et deux entrées du journal.

Formulation proposée, à valider par Timéo et Romain : Safe Shield avertit mais n'agit pas (c'est écrit dans l'aide de Safe) ; Guardian agit, mais il bloque, et il est vendu aux grandes trésoreries par un commercial, sans prix public. Nous visons les petites organisations avec une réponse graduée qui ne peut pas verrouiller les fonds, et un oracle qui lit le Web.

Non confirmé : la gratuité de Safe Shield pour tous les utilisateurs, et le prix de Guardian.

## Conséquence pour la feuille de route

Chez Safe, un paiement en attente de signatures n'apparaît pas sur la chaîne. Notre module pour Safe devra lire le service de transactions de Safe, ou s'appuyer sur un guard et un module de délai. Le relais actuel, qui écoute les événements du contrat, ne suffira pas tel quel.

## Sources

- Safe Shield, analyse : https://help.safe.global/articles/6434169802-understanding-safe-shield-copilot
- Safe Shield, Guardian de Hypernative : https://help.safe.global/articles/7610775969-understanding-safe-shield-guardian-by-hypernative
- Annonce du partenariat : https://safe.global/blog/safe-partners-with-hypernative-to-launch-enterprise-security-integration
- Guards de Safe : https://docs.safe.global/reference-smart-account/guards/setGuard

Aucun code ni document de positionnement n'a été modifié.
