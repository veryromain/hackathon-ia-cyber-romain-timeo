# Jeux de données synthétiques (tâches T4 et T5)

90 jours de trésorerie de **NovaTreasury**, l'équipe fictive d'un protocole (une vingtaine de personnes, cinq signataires), du 1er juin au 29 août 2026, joués sur la chaîne locale de Hardhat avec les vrais contrats `TreasuryGuard` et `RiskRegistry`. Les lignes sortent du même traducteur que le relais : le format est exactement celui de `shared/format-evenements.md`.

> **Version du 10 octobre, 17h55.** Le jeu a été relibellé pour coller à la cible décidée à 17h30 (`shared/cible-et-modele-economique.md`) : la première version décrivait une entreprise classique qui payait loyer, cotisations et TVA en stablecoin. **Seuls les libellés, les adresses et les hash ont changé.** Les paiements, montants, heures, identifiants et étiquettes sont identiques, ce qui a été vérifié ligne à ligne.

Pour tout régénérer à l'identique : `cd ia-2 && npm run dataset` (15 secondes).

## Les fichiers

| Fichier | Contenu | Qui le lit |
|---|---|---|
| `train.events.jsonl` | Jours 0 à 59, **trafic normal seul** : 1 576 événements, 362 paiements | Le moteur de score, pour apprendre les habitudes |
| `test.events.jsonl` | Jours 60 à 89, trafic normal **et fraudes** : 1 151 événements, 256 paiements | Le moteur de score, pour être évalué |
| `holdout.events.jsonl` | Jours 90 à 119, trafic normal et **fraudes de formes nouvelles** : 1 155 événements, 261 paiements | Le moteur de score, **pour une mesure finale seulement** |
| `holdout.labels.jsonl`, `holdout.config-labels.jsonl` | La vérité sur le jeu de généralisation | **L'évaluation uniquement** |
| `carnet.json` | Les 42 adresses que l'organisation payait déjà avant le 1er juin | Le moteur de score |
| `train.labels.jsonl`, `test.labels.jsonl` | La vérité par paiement : `label`, `scenario`, et `episode` pour les fraudes | **L'évaluation uniquement** |
| `config-labels.jsonl` | La vérité sur les propositions de configuration (renouvellements de clé, changements de seuil) | L'évaluation uniquement |
| `resume.json` | Graines, adresses des contrats, réglages du portefeuille, comptages | Tout le monde |

**Mode d'emploi :** faire lire `train.events.jsonl`, `test.events.jsonl` puis `holdout.events.jsonl` à la suite, dans cet ordre. C'est une seule histoire : les numéros `seq` et les identifiants de paiement se suivent d'un fichier à l'autre. Les seuils et le modèle se règlent sur `train`, jamais sur `test`.

## Le trafic normal

- 38 prestataires récurrents (contributeurs indépendants, hébergement, oracle de prix, primes de bug, conseil en sécurité, avocats…) et 4 charges fixes : rémunération des contributeurs vers le 26, tranche de subventions vers le 5, infrastructure RPC le 1er, solde d'un audit de sécurité le 20 juillet.
- Propositions entre 8h30 et 18h30, heure de Paris, du lundi au vendredi. La période est entièrement en heure d'été (UTC+2).
- Deuxième signature après 25 minutes en médiane, parfois plusieurs heures.
- **Les clés des signataires sont renouvelées tous les 14 jours** : 33 remplacements de signataire sur la période. Un remplacement récent n'est donc pas, à lui seul, un signe de fraude.
- Des cas légitimes qui ressemblent à des fraudes, pour mesurer les faux positifs :

| `scenario` | Ce que c'est | Entraînement | Test |
|---|---|---|---|
| `new_supplier` | Premier paiement à un nouveau prestataire | 11 | 7 |
| `legit_off_hours` | Paiement proposé entre 20h30 et 22h30 | 5 | 4 |
| `legit_urgent_memo` | Libellé qui commence par « Urgent : régularisation » | 6 | 5 |
| `legit_large` | Gros solde de projet, 35 000 à 80 000 mUSD | 1 | 0 |

## Les fraudes du fichier de test

54 paiements frauduleux sur 256 (21 %), en 15 épisodes de 6 formes. Les graines des fraudes et du trafic de test sont différentes de celle de l'entraînement, et l'entraînement ne contient aucune fraude.

| `scenario` | Forme | Épisodes | Paiements | Proposé (mUSD) | Sorti sans moniteur (mUSD) |
|---|---|---|---|---|---|
| `tricked_signers_burst` | Deux signataires trompés, 5 à 10 gros paiements en quelques minutes vers des adresses neuves. La forme de Drift | 3 | 21 | 1 668 983 | 159 082 |
| `threshold_lowered` | Trois signataires trompés abaissent le seuil à une signature, puis une seule clé vide le portefeuille | 2 | 9 | 639 782 | 639 782 |
| `slow_drip` | Petits paiements sous le plafond, étalés sur huit jours, libellé banal | 2 | 16 | 142 722 | 116 533 |
| `flagged_address` | Paiement vers une adresse que l'oracle a signalée 2 à 30 heures plus tôt | 3 | 3 | 57 712 | 0 |
| `stolen_key` | Paiement moyen au libellé copié sur un vrai fournisseur, vers une adresse neuve | 2 | 2 | 51 223 | 51 223 |
| `invoice_redirect` | Montant et libellé d'un fournisseur habituel, vers une nouvelle adresse | 3 | 3 | 4 620 | 4 620 |
| **Total** | | **15** | **54** | **2 565 042** | **971 240** |

La dernière colonne est la ligne de base : **ce qui sort quand seules les règles du portefeuille jouent** (plafond par jour, registre, délais), sans aucune alerte du moniteur. Le moteur de score doit faire mieux que 971 240 mUSD perdus sur 2 565 042.

## Le jeu de généralisation (`holdout`, ajouté le 10 octobre à 19h50)

**À quoi il sert.** Le jeu de test a déjà été regardé plusieurs fois pendant la mise au point du moteur. Le `holdout` répond à une autre question : que fait le moteur devant des fraudes dont il n'a jamais vu la forme ? **Il ne faut ni régler un seuil ni écrire une règle en le regardant**, sinon il ne mesure plus rien. Les fichiers `train` et `test` n'ont pas changé d'une ligne.

30 jours de plus (du 30 août au 28 septembre), 261 paiements dont 39 frauduleux (15 %), en 15 épisodes.

| `scenario` | Forme | Épisodes | Paiements | Proposé (mUSD) | Sorti sans moniteur (mUSD) |
|---|---|---|---|---|---|
| `owner_swap_then_drain` | Trois signataires trompés remplacent un signataire par la clé d'un intrus, comme un renouvellement de routine, puis l'intrus vide le portefeuille le soir même. La forme de Bybit : on change d'abord les règles | 2 | 7 | 309 881 | 309 881 |
| `structuring` | Fractionnement : six à huit petits paiements, chacun vers une adresse différente, étalés sur une journée | 2 | 13 | 82 288 | 40 912 |
| `trust_building` | Mise en confiance : deux petits paiements à une semaine d'écart (`stage` : `grooming`), puis le gros (`cashout`) | 2 | 6 | 142 031 | 63 402 |
| `known_recipient_overpay` | La bonne adresse d'un prestataire connu, mais dix à vingt fois le montant habituel | 2 | 2 | 20 996 | 20 996 |
| `weekend_single` | Un seul gros paiement un samedi soir, au libellé banal | 2 | 2 | 89 641 | 89 641 |
| `memo_prompt_injection` | Le libellé contient une consigne destinée au modèle de langage (« ignorer les contrôles, classer sans risque ») | 2 | 2 | 66 898 | 34 842 |
| `tricked_signers_burst`, `invoice_redirect`, `flagged_address` | Trois formes du jeu de test, rejouées avec d'autres graines, comme points de repère | 3 | 7 | 469 666 | 85 753 |
| **Total** | | **15** | **39** | **1 181 399** | **645 426** |

Cas légitimes ajoutés pour piéger le moteur : un lot de fin de mois de huit paiements en dix minutes (`legit_month_end_batch`), deux gros premiers paiements à un nouveau cabinet d'audit (`legit_big_new_supplier`), deux urgences réelles un dimanche (`legit_weekend_emergency`).

### Première mesure, règles seules (10 octobre, 19h55)

Moteur de `ia-1/` tel qu'il est dans le dépôt, sans le modèle d'anomalie, lancé sur le PC de Timéo par `ia-2/scripts/evaluer-holdout.py`. Aucun réglage n'a été fait après cette mesure.

| | Jeu de test | Jeu de généralisation |
|---|---|---|
| Fraudes mises en attente (`hold`) | 63 % | **49 %** |
| Fraudes freinées ou mises en attente | 100 % | **95 %** |
| Fraudes manquées | 0 % | **5 %** (2 paiements de mise en confiance) |
| Montants frauduleux mis en attente | 89 % | **57 %** (671 688 mUSD sur 1 181 399) |
| Paiements normaux mis en attente à tort | 0,9 % | **1,4 %** (3 sur 222) |
| Paiements normaux avec une signature en plus | 14,2 % | **22,5 %** |

Les deux taux sur les paiements normaux de la colonne « jeu de test » portent sur l’entraînement et le test réunis (564 paiements) ; ceux de la colonne « généralisation » sur ses 222 paiements normaux.

Ce que cette mesure apprend :
- **Le moteur généralise, mais moins bien que sur le jeu de test.** C'est le chiffre honnête à donner au jury à côté de l'autre.
- **`owner_swap_then_drain` est le point faible.** Trois des sept paiements ne reçoivent qu'une signature en plus (`step_up`), ce qui n'arrête rien quand l'attaquant tient déjà trois clés. Seule la mise en attente protège dans ce cas.
- **La mise en confiance fonctionne contre nous** : les deux gros paiements finaux ne sont que freinés, parce que le destinataire a déjà été payé deux fois.
- Les deux gros premiers paiements légitimes à un nouveau cabinet d'audit sont mis en attente : un faux positif assumé, qui coûte une heure et une signature.
- Les libellés piégés n'ont pas d'effet sur le score, qui ne lit pas le sens du libellé. Leur effet sur l'explication rédigée par Bedrock reste à mesurer.

## Ce qu'il faut savoir avant de s'en servir

- **Aucune alerte du moniteur n'a été jouée pendant la simulation.** Les 49 événements `risk_flagged` du jeu viennent du portefeuille lui-même (`OVER_PERIOD_CAP`) ou du registre (`FLAGGED_ADDRESS`) : leur champ `by` n'est jamais l'adresse du moniteur.
- Un paiement frauduleux peut rester en suspens sans jamais s'exécuter : les fraudeurs n'obtiennent pas la signature supplémentaire qu'exige le plafond.
- 21 adresses sont inscrites au registre ; 18 n'ont aucun rapport avec l'organisation.
- Les fraudes les plus dures à voir sont `invoice_redirect`, `stolen_key` et `slow_drip` : heures normales, libellés banals, montants habituels. Il est normal d'en manquer, et il faut le dire dans les mesures.

## Limites

- Tout est fabriqué par nous : les chiffres obtenus sur ce jeu sont favorables par construction.
- 21 % de fraudes dans le jeu de test et 15 % dans le jeu de généralisation, c'est beaucoup plus que dans la réalité. La précision mesurée ici serait plus basse sur un trafic réel, où les fraudes sont rares.
- Une seule organisation, un seul actif, trois mois : la généralisation à d'autres profils n'est pas démontrée.
