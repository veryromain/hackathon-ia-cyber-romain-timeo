# Validation du moteur de score (R1)

## ★ Résultat principal : test indépendant sur le jeu de Timéo (`shared/donnees/`, vrais contrats, fraudes conçues par Timéo)

Réglage sur `train` (60 jours, trafic normal seul) et sur mon générateur. **Évaluation unique sur `test`** (30 jours, 54 paiements frauduleux en 15 épisodes, 6 formes) :

| Fraude (test) | n | Arrêtée (`hold`) | Freinée (`step_up`) | Rien |
|---|---|---|---|---|
| Rafale « à la Drift » (signataires trompés) | 21 | 95 % | 5 % | 0 % |
| Seuil abaissé puis vidage | 9 | 89 % | 11 % | 0 % |
| Adresse signalée par l'oracle | 3 | 100 % | 0 % | 0 % |
| Clé volée (libellé copié) | 2 | 50 % | 50 % | 0 % |
| Redirection de facture (nouvelle adresse) | 3 | 33 % | 67 % | 0 % |
| Goutte-à-goutte | 16 | 6 % | 94 % | 0 % |
| **Total** | **54** | **63 %** | **37 %** | **0 %** |

- **Montants :** 2 285 715 mUSD mis en attente sur 2 565 065 proposés (**89 %**), **100 % freinés ou en attente**. Sans moniteur, les règles du portefeuille laissaient sortir 971 240 mUSD.
- **Paiements normaux (train + test, n = 564) :** **0,9 % mis en attente à tort**, 14,2 % avec une signature de plus. Sur les 60 signatures en plus vers des fournisseurs récurrents du test, **56 tombent dans les 7 jours qui suivent une baisse du seuil par l'attaquant** : c'est voulu (on rétablit une signature pendant une attaque). Hors attaque, les fournisseurs récurrents passent sans friction.

**Ce que le test indépendant a corrigé** (réglé sur `train`, jamais sur `test`) : Timéo renouvelle les clés tous les 14 jours (conseil du mentor). `NEW_OWNER_PROPOSES` ne vaut donc que vers une adresse inconnue (45 % de friction → 0 % sur les récurrents en `train`). Les adresses du carnet ne sont jamais « récentes » (`RAPID_REPEAT`). Le libellé urgent seul ne suffit plus (0,20), le schéma « inconnu + urgent » pèse 0,55.

### + R2 (modèle d'anomalie, appris sur `train`) — même test

| | Règles seules | Règles + R2 |
|---|---|---|
| Fraudes arrêtées (`hold`) | 63 % | **69 %** (clé volée, seuil abaissé, goutte-à-goutte en hausse) |
| Montants frauduleux mis en attente | 89 % | **94 %** |
| Fraudes freinées ou arrêtées | 100 % | 100 % |
| Faux `hold` sur les normaux | 0,9 % | **0,9 %** |

Variante choisie sur `train` seulement (sans les caractéristiques de nouveauté), évaluée une seule fois sur `test`.

---

Première validation (10/10 vers 17h00) sur des données synthétiques générées par `ia-1/eval/generateur.py`, en attendant le trafic de Timéo (T4/T5) qui servira de **test indépendant**.

## Protocole
- **Trafic normal sur 45 à 90 jours :** salaires mensuels, 8 fournisseurs récurrents, nouveaux fournisseurs légitimes (dont certains repayés), grosses factures annuelles (6 à 12 × l'habitude), 5 % de paiements tardifs, un remplacement légitime de signataire.
- **8 fraudes par graine :**
  - signataires trompés en rafale ;
  - clé volée (la nuit) ;
  - goutte-à-goutte ;
  - seuil de signatures abaissé puis paiement ;
  - signataire remplacé puis vidage ;
  - adresse signalée par l'oracle ;
  - fraude au président ;
  - usurpation de fournisseur (« nouveau RIB »).
- **Réglage sur les graines 1-20** (entraînement), **évaluation sur 90 graines jamais vues**, avec des montants × 0,3 à × 3 et des durées de 45 à 90 jours.
- « Arrêtée » = `hold` (mise en attente) ; « freinée » = `step_up` (une signature de plus).

## Résultats sur les données de test (jamais vues)

| Test | Fraudes arrêtées | Fraudes freinées ou arrêtées | Paiements normaux mis en attente à tort | Paiements normaux avec une signature de plus |
|---|---|---|---|---|
| A — graines 101-130, montants × 1, 60 j | 63 % | **100 %** | **0,3 %** | 24,6 % |
| B — graines 131-160, montants × 3, 90 j | 64 % | **99 %** | **0,2 %** | 21,3 % |
| C — graines 161-190, montants × 0,3, 45 j | 63 % | **99 %** | **0,4 %** | 27,5 % |

**Hors goutte-à-goutte, ≈ 98 % des fraudes sont arrêtées (`hold`).** Le goutte-à-goutte (petits montants habituels, heures ouvrées) n'est que freiné (`step_up` à 98 %) : c'est le cas le plus difficile, à dire au jury.

**D'où vient la « signature de plus » sur les paiements normaux :**
- **le 1er paiement à un nouveau fournisseur**, voulu : c'est la vérification de tout nouveau bénéficiaire ;
- **les grosses factures annuelles** ;
- **les paiements faits juste après une baisse du seuil par l'attaquant**, voulu : on rétablit une signature pendant une attaque.

Les paiements récurrents habituels passent sans friction dans environ 85 % des cas.

## Améliorations apportées pendant la validation
1. **Montant comparé à l'historique du destinataire** (et non à la médiane globale) ; un destinataire inconnu est comparé au 90ᵉ centile. Résultat : la friction sur les salaires est passée de 88 % à 10 %.
2. **Bug corrigé :** un destinataire du carnet sans historique était traité comme inconnu.
3. **`BURST` limité aux destinataires inconnus** (les paiements groupés de fin de mois sont normaux).
4. **Remplacement de signataire :** le poids est faible si le changement est légitime, et fort (`NEW_OWNER_PROPOSES`) si c'est le nouveau signataire qui propose.
5. **Nouvelles règles :**
   - `PAYMENT_FRAUD_PATTERN` (nouveau destinataire + libellé pressant ou changement de coordonnées) : la fraude au président passe de 40 % à 100 % arrêtée, l'usurpation de fournisseur de 10 % à 100 % ;
   - `RAPID_REPEAT` (goutte-à-goutte) : 47 % de fraudes passaient, contre 1-2 % maintenant ;
   - nuit plus pénalisée que soir.
6. **Seuils choisis par recherche en grille sur l'entraînement :** `hold` ≥ 0,75 (faux `hold` divisé par 2), `step_up` ≥ 0,30.
7. **Bug corrigé :** les seuils étaient copiés à l'import, ce qui rendait le réglage inopérant.
8. **Mémoire bornée :** seules les propositions des 3 derniers jours sont gardées.

## Robustesse et performance
- **11 tests automatiques** (`cd ia-1 && .venv/bin/python -m pytest -q tests`) : exemple de Timéo, ligne JSON malformée, type d'événement inconnu, adresse en majuscules, libellé absent, montant nul, signalement expiré, événement incomplet (ignoré, le moteur continue).
- **Vitesse :** environ 400 000 événements/s ; latence p99 de 0,2 ms par événement, quand le délai d'examen laisse 60 000 ms.

## Limites honnêtes
- Le générateur et le moteur sont écrits du même côté : **les chiffres définitifs doivent venir du trafic de Timéo (T4/T5)**, produit indépendamment.
- Poids réglés à la main, avec des règles explicables. Le modèle d'anomalie (R2) viendra en complément.
- Si les signataires trompés sont aussi ceux qui ajoutent la signature demandée, un `step_up` ne suffit pas : seul `hold` (délai + vérification par un autre canal) protège vraiment.
