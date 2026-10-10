# Comparaison du point 7 de l'artifact Claude avec les améliorations Codex

Source lue dans l'onglet Chrome : https://claude.ai/artifact/KPSo36rrH7599DyW1LopqF (« Contrôles de Breaker », état annoncé 21h15).

Les sept idées ne sont pas les trois corrections livrées dans le commit dad965a. Elles constituent une liste complémentaire.

| Idée de l'artifact | Rapport avec notre travail |
|---|---|
| Adresses sosies | Nouvelle proposition ; pas implémentée dans ma correction. |
| Adresses pièges | Nouvelle proposition ; le gel automatique proposé contredit le rôle limité du moniteur. Préférer alerte/hold et gel humain. |
| Ce que vous signez vraiment | Recoupe la simulation/vérification avant signature proposée en feuille de route ; saisie des quatre caractères est une proposition nouvelle, non livrée. Quatre caractères ne suffisent pas pour distinguer un sosie qui copie le suffixe. |
| Immunité collective | Nouvelle proposition sur le registre existant. Une annulation ne prouve pas une fraude ; vérifier/croiser les signalements avant propagation. |
| Clé de contrainte | Nouvelle proposition ; non livrée. Un gel on-chain public ne peut pas être promis discret. |
| Empreinte comportementale des signataires | Prolonge la détection comportementale existante, mais l'apprentissage individuel décrit n'a pas été ajouté. |
| Journal d'audit chaîné | Bonus déjà évoqué dans le plan ; pas implémenté dans les corrections livrées. Un ancrage permet de détecter une modification d'un historique fourni, pas de garantir sa disponibilité ou sa complétude. |

Livré par Codex : probation de deux jours, délai de gouvernance préservé à l'unanimité, invalidation des anciens votes lors du retrait/réajout d'une adresse ; 30 tests locaux, Fuji encore sur l'ancien contrat.

L'artifact est antérieur à la correction : son statut « probation à faire » et son total de 20 tests contrats sont dépassés pour le code local. Aucune exclusivité concurrentielle (« rare », « absent », « inédit ») de ces idées n'est établie par notre comparaison ; ne pas les présenter comme démontrées.

Demande actuelle : comparaison seulement ; aucune nouvelle fonctionnalité autorisée explicitement dans ce message ou ajoutée à cette étape.
