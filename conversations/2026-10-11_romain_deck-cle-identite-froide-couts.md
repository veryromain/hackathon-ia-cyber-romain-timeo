# 2026-10-11 — Romain — Deck : clé d'identité froide, chiffres de la diapo 5, coûts

## Fait
- Diapo 4 : bandeau encadré « Clé d'identité froide » (seconde clé hors ligne, révocation sans quorum, même coffre gelé), sans retirer la clé de contrainte, la probation, le flux ni les trois verbes. Notes orateur enrichies avec la preuve Fuji. Même nom sur la diapo 6 et l'annexe. `generer_deck.py`, `Breaker-pitch.pptx`, `breaker-deck.html` mis à jour ; rendu contrôlé via LibreOffice.

## Réponses données à Romain
- « 280 500 tentés, zéro sorti » : trois virements frauduleux de 95 000, 93 500 et 92 000 mUSD (jeton de test, 18 décimales, Fuji) par deux signataires trompés, mis en attente 5 à 6 s après proposition, bloqués à 2/3, gelés puis annulés. Unité : mUSD, pas des euros. Sans le garde : 95 000 seraient sortis.
- Coût variable par client ≈ 1,2 $/mois (20 alertes, 2 rapports, 50 pages d'oracle) + 5 à 15 € d'infra partagée → < 20 €/client/mois. Coût par paiement examiné ≈ 0 ; par alerte ≈ 0,013 $ ; côté client ≈ 0,024 $ de gas par paiement complet.
- Argument « 449 € = 5 %, 990 € = 10 % de la perte annuelle évitée » : à présenter comme règle d'achat du RSSI (prix ≤ 10 % du risque évité), preuve que le prix vient de la valeur et non du coût, et marge de sécurité (le prix tient même si la perte évitée est 5 fois plus faible).

## Prochaines étapes
- Relecture par Timéo de la diapo 4 (c'est sa diapo). Éventuellement ajouter l'unité « mUSD » au titre de la diapo 5.

## Suite (2026-10-11 10:25) — cible élargie au seuil 1 M$
- Explication des 5 % : perte annuelle attendue évitée = 9,5 % × 1,3 M$ × 91 % = 112 385 $/an ; 449 € × 12 = 5 388 €/an = 4,8 % ; 990 € × 12 = 11 880 € = 10,6 %.
- Romain décide d'inclure toute organisation > 1 M$ de trésorerie : H1 révisée, 111 contactables, 56 en observation, 5 à 10 payants, point mort T2-T3 2027. Diapos 3 et 7, HTML, business-marche, mise-sur-le-marché, prix, pitch-final mis à jour (détail dans JOURNAL).
