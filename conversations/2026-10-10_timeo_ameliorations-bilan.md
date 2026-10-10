# Améliorer Breaker à partir du bilan et des concurrents

Timéo demande de s'appuyer sur le bilan récent de Romain pour corriger les faiblesses à partir des documentations concurrentes.

Lecture du bilan, du plan et du journal. Les règles de détection sont déjà corrigées et mesurées ; la priorité restante pour le hackathon est la probation des clés neuves. Recherche officielle Squads (time locks), Safe (guards/récupération), Fireblocks (politiques/revue), Blockaid (cosignature indépendante et recours humain).

Implémentation : deux jours de probation pour les quorums renforcés et le dégel ; délai de gouvernance non contournable par unanimité ; numéro d'incarnation pour empêcher une adresse retirée/réajoutée de retrouver ses anciennes approbations. Compatibilité conservée avec le relais, export ABI.

Validation : npm test, 30 réussites dont 10 régressions ; export-abi et gas locaux réussis. Résultats et limites : shared/ameliorations-apres-bilan.md. Bilan, README, SUIVI et journal actualisés. Aucun dataset, moteur, site, secret ou déploiement Fuji modifié.

Reste : activer les corrections via un nouveau déploiement Fuji coordonné ; observation, entretiens pour les faux positifs, simulation avant signature et récupération auditée selon la feuille de route. Ne pas annoncer la nouvelle probation sur le contrat de la démo existante.
