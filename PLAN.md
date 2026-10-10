# Plan d'action — « Breaker », SOC antifraude pour trésoreries sur la blockchain

> **Statut : proposition rédigée par Claude à la demande de Timéo, samedi 16h35. À valider par Romain.**
> Elle remplace le plan de l'axe 4, archivé dans `shared/archive/PLAN-axe4.md`.
> Track 1 (Fintech Security), **axe 2** : SOC antifraude à l'ère de l'IA générative.

## 1. Le projet en une phrase

**Un garde antifraude pour les entreprises qui gèrent leur trésorerie avec un portefeuille à plusieurs signataires.** Chaque paiement proposé est noté avant son exécution ; s'il est suspect, le portefeuille exige des signatures supplémentaires ou le met en attente, et les signataires reçoivent une alerte expliquée en clair.

## 2. Pourquoi ce cadrage

- **Le retour du mentor Team1** (`shared/retour-mentor-team1.md`) : ne pas bloquer un protocole nous-mêmes, ne jamais gérer les fonds des clients, alerter les signataires, plafonner les sorties par période, forcer le renouvellement des clés.
- **Le cas Drift (avril 2026, 280 à 285 M$)** : des signataires trompés ont validé à l'avance des transactions malveillantes, puis les fonds sont sortis en 31 retraits et 12 minutes. C'est une fraude au président, en version crypto.
- **L'axe 2 du guide** demande exactement notre réponse : authentification renforcée, mise en attente, gel, alerte client.
- **Ce qui nous distingue** : peu d'équipes sauront faire appliquer la réponse par un contrat sur la chaîne, et notre outil ne peut qu'ajouter de la friction. Il ne valide, ne bloque ni ne déplace jamais de fonds.

## 3. Le scénario de démo (un seul, de bout en bout)

1. **Avant.** Une entreprise fictive tient sa trésorerie dans un portefeuille à 5 signataires, dont 2 suffisent pour payer. Trafic normal : salaires, fournisseurs habituels, parfois un nouveau fournisseur.
2. **Fraude.** Deux signataires sont trompés (faux message urgent du dirigeant) et valident une série de virements vers des adresses jamais vues. Variante : une clé volée.
3. **Détection, avant que l'argent parte.** Le moniteur note chaque paiement dès qu'il est proposé : destinataire inconnu, montant hors habitudes, rafale, signatures anciennes, changement récent des signataires ou du seuil.
4. **Réponse graduée, appliquée par le portefeuille du client.**
   - risque moyen : signatures supplémentaires exigées ;
   - risque élevé : mise en attente pendant un délai, annulable par les signataires ;
   - à tout moment : gel du portefeuille par un signataire ;
   - dans tous les cas : alerte avec explication en clair et preuves.
5. **Après.** Rapport d'incident généré (Bedrock), chaque affirmation reliée à une transaction. Le journal des décisions est vérifiable sur la chaîne.
6. **Chiffres à l'écran.** Taux de détection, faux positifs sur le trafic normal, délai entre la proposition et le signalement, part des fonds protégés.

## 4. Architecture

```
 ia-2 (Timéo)                                         ia-1 (Romain)
┌────────────────────────────┐   events.jsonl   ┌──────────────────────────────┐
│ Contrat TreasuryGuard      │ ───────────────> │ Moteur de score              │
│  propose / approuve /      │                  │  règles + détection          │
│  exécute, plafond, délai,  │                  │  d'anomalies, raisons        │
│  gel, expiration des clés  │   alerts.jsonl   │                              │
│                            │ <─────────────── │ Explication et rapport       │
│ Relais chaîne <-> fichiers │                  │  (Bedrock)                   │
│ Générateur de trafic       │                  │                              │
│ Scénarios de fraude        │                  │ Tableau de bord (Streamlit)  │
└────────────────────────────┘                  └──────────────────────────────┘
```

**L'interface entre nous deux, ce sont deux fichiers JSON Lines.** Romain n'a jamais besoin de toucher à la blockchain : il lit `events.jsonl` et écrit `alerts.jsonl`. Le relais de Timéo fait le lien avec la chaîne dans les deux sens. Chacun peut donc avancer seul à partir de fichiers d'exemple.

**Où est l'IA ?**
- **Score :** des règles explicables, plus un modèle d'anomalie appris sur le trafic normal. Chaque alerte cite ses raisons.
- **Bedrock :** rédige l'explication destinée aux signataires et le rapport d'incident. Il ne décide jamais du niveau de risque.
- **Bonus :** Bedrock analyse le texte de justification du paiement pour repérer les marqueurs d'une fraude au président (urgence, secret, changement de coordonnées).

**Ce que le moniteur a le droit de faire sur la chaîne :** signaler un paiement comme risqué, rien d'autre. Le signalement ajoute des exigences ; les signataires gardent le dernier mot.

**Stack**

| Brique | Choix | Qui |
|---|---|---|
| Contrat | Solidity, Hardhat, OpenZeppelin | Timéo |
| Chaîne | Chaîne locale Hardhat pour les mesures, Avalanche Fuji pour la démo | Timéo |
| Relais, trafic, fraudes | Scripts Node (ethers) | Timéo |
| Score | Python 3.12, pandas, scikit-learn | Romain |
| Modèle de langage | AWS Bedrock, modèle lu dans `BEDROCK_MODEL_ID` | Romain |
| Tableau de bord | Streamlit | Romain |

## 5. Qui fait quoi

### Timéo — `ia-2/` : la blockchain et les données

| # | Tâche | Fini quand |
|---|---|---|
| T1 | **Format des événements et des alertes** dans `shared/format-evenements.md`, avec un fichier d'exemple écrit à la main dans `shared/echantillons/` | Romain peut lancer son moteur dessus |
| T2 | **Contrat `TreasuryGuard`** : proposition, approbation et exécution à M signataires sur N ; plafond par période au-delà duquel il faut plus de signatures ; signalement de risque par le moniteur (signatures en plus, ou mise en attente) ; gel par un signataire ; expiration des clés | Les tests passent en local, dont le scénario de fraude avec et sans garde |
| T3 | **Relais** : écrit les événements de la chaîne dans `events.jsonl`, lit `alerts.jsonl` et envoie le signalement sur la chaîne | Une alerte de Romain change réellement le sort d'un paiement |
| T4 | **Générateur de trafic normal** : salaires, fournisseurs récurrents, nouveau fournisseur légitime, renouvellement de clé légitime | Un fichier d'entraînement de plusieurs centaines de paiements |
| T5 | **Scénarios de fraude**, au moins 5 variantes : signataires trompés, clé volée, rafale, goutte-à-goutte sous le plafond, baisse du seuil avant l'attaque | Un fichier de test étiqueté, produit avec d'autres graines que l'entraînement |
| T6 | **Déploiement sur Fuji** et rejeu de la démo, avec les liens de l'explorateur | La démo tourne sur Fuji |
| T7 | **Mesure du gas** des transactions du garde, pour le modèle économique | Tableau dans `shared/` |

### Romain — `ia-1/` : la détection, l'explication et la présentation

| # | Tâche | Fini quand |
|---|---|---|
| R1 | **Moteur de score** : lit `events.jsonl`, tient l'historique (destinataires connus, montants habituels, rythme), applique les règles, sort un score et des raisons | Tourne sur l'exemple de T1 et écrit `alerts.jsonl` |
| R2 | **Modèle d'anomalie** appris sur le trafic normal de T4, combiné aux règles | Les seuils des trois niveaux sont réglés sur l'entraînement, jamais sur le test |
| R3 | **Explication de l'alerte** par Bedrock : quelques phrases pour un signataire, chaque fait relié à une transaction, avec repli sur un texte à trous si Bedrock est injoignable | Une alerte lisible par quelqu'un qui ne connaît pas la blockchain |
| R4 | **Rapport d'incident** par Bedrock : chronologie, montants, décisions prises, preuves | Un rapport généré sur la fraude de démo |
| R5 | **Tableau de bord** : paiements en cours, score, raisons, état (normal, signatures en plus, en attente, gelé), chiffres clés | Suffit à filmer la démo |
| R6 | **Évaluation** : taux de détection, précision, faux positifs, délai de signalement, fonds protégés, sur le fichier de test de T5 | Tableau de chiffres dans `shared/` |
| R7 | **Livrables écrits** : formulaire du checkpoint, deck, fiche de défense, playbook de réponse, slide conformité | Relus par Timéo |

### Ensemble

- Intégration de bout en bout, vidéo de démo, README final, répétition du pitch, vérification qu'aucun secret n'est dans le dépôt, accès du jury au dépôt.

## 6. Calendrier

| Créneau | Timéo | Romain | Contrôle |
|---|---|---|---|
| **Sam. 16h30–17h15** | T1 : format et exemple | Lit le plan, prépare l'environnement Python | Plan validé à deux, noté dans `JOURNAL.md` |
| **Sam. 17h15–18h30** | T2 : contrat et tests | R1 sur l'exemple ; R7 : formulaire du checkpoint | Formulaire prêt |
| **Sam. 18h30** | ✅ **Checkpoint** | ✅ **Checkpoint** | Track confirmé |
| **Sam. 18h30–21h00** | T2 fini, T3 : relais, T4 : trafic normal | R1 fini, R2, R5 en première version | Romain reçoit le fichier d'entraînement |
| **Sam. 21h00–23h00** | T5 : fraudes ; intégration | Intégration ; R3 | **Première démo de bout en bout en local, même moche** |
| **Sam. 23h00–02h00** | T6 : Fuji ; variantes de fraude | R3, R4, R5 | Rapport généré sur la fraude de démo |
| **Dim. avant 03h00** | **Renouveler la clé Bedrock** (elle expire vers 03h28) | — | Appel de test réussi |
| **Dim. 02h00–07h00** | Sommeil à tour de rôle ; T7 | Sommeil à tour de rôle ; R6 | — |
| **Dim. 07h00–09h00** | Rejoue les mesures, corrige | R6 : chiffres définitifs | Tableau de chiffres dans `shared/` |
| **Dim. 09h00–10h00** | Vidéo de démo (2 à 3 minutes) | README final | Vidéo enregistrée |
| **Dim. 10h00** | Atelier de coaching pitch | Atelier de coaching pitch | — |
| **Dim. 10h00–11h30** | Vérification des secrets, accès du jury | R7 : deck, fiche de défense, playbook, slide conformité | Tout est dans le dépôt |
| **Dim. 12h00** | 🧊 **Rendu** | 🧊 **Rendu** | — |

**Règle d'or :** une démo de bout en bout qui marche samedi à 23h00 vaut mieux que des briques parfaites séparées.

## 7. Travailler chacun de son côté sans se gêner

- Timéo n'écrit que dans `ia-2/`, Romain que dans `ia-1/`. Dans `shared/`, on prévient dans `JOURNAL.md` avant de changer un fichier de l'autre.
- Avant de commencer : `git pull --rebase`, puis lecture du haut de `JOURNAL.md`. Après chaque avancée : une entrée dans `JOURNAL.md`, puis commit et push.
- Le format de `shared/format-evenements.md` ne change plus sans prévenir l'autre.
- **Bedrock** : chacun ses identifiants, dans `.env` à la racine (ignoré par Git). Le code lit le modèle dans `BEDROCK_MODEL_ID`, car nous n'avons pas accès aux mêmes modèles. Le Wi-Fi de l'école bloque Bedrock : passer en partage de connexion pour ces appels. Détail dans `shared/aws-bedrock.md`.

## 8. Texte pour le checkpoint de 18h30 (à ajuster par Romain)

- **Problème.** Les entreprises qui gèrent leur trésorerie sur la blockchain dépendent de quelques signataires. Il suffit d'en tromper deux, par un faux message du dirigeant que l'IA générative rend crédible, pour vider les fonds en quelques minutes, comme chez Drift en avril 2026.
- **Solution.** Un garde antifraude qui note chaque paiement avant son exécution et déclenche une réponse graduée appliquée par le portefeuille du client : signatures supplémentaires, mise en attente, gel, alerte expliquée. L'outil ne détient jamais les fonds.
- **Stack.** Solidity et Hardhat sur Avalanche Fuji, Python et scikit-learn pour le score, AWS Bedrock pour les explications et le rapport, Streamlit pour le tableau de bord.

## 9. Limites et risques

| Risque | Parade |
|---|---|
| **Toutes les données sont synthétiques**, donc les chiffres sont favorables par construction | Graines différentes entre entraînement et test, variantes de fraude que le moteur n'a jamais vues, et on le dit au jury |
| **Faux positifs** : un paiement légitime retardé | Le pire cas est une signature de plus ou un délai. Les signataires peuvent toujours passer outre à l'unanimité |
| **Tous les signataires trompés à la fois** | Hors de portée : on le dit. Le délai de mise en attente laisse quand même une chance de réagir |
| **Le renouvellement des clés ne détecte rien** et n'empêche pas un signataire trompé de signer avec une clé neuve | Présenté comme une mesure de protection, pas comme la détection |
| **Le moniteur est lui-même compromis** | Il ne peut qu'ajouter de la friction : au pire, des paiements légitimes sont ralentis |
| **Retard sur le contrat** | Couper dans l'ordre : expiration des clés, puis gel, puis plafond. Le signalement de risque et la mise en attente sont le cœur |
| **Bedrock injoignable** (réseau, clé expirée) | Texte à trous sans modèle de langage, prévu dans R3 |
| **Démo en direct qui plante** | Vidéo enregistrée et scénario rejouable en local |

**À confirmer avec le mentor KPMG :** le cadre de conformité à mettre sur la slide. Si le client est une entité financière régulée, DORA s'applique à ses incidents (notes dans `shared/dora-notes.md`) ; sinon, l'angle est l'AI Act et la traçabilité des décisions.

**Réponse à « si votre modèle se trompe, qui est responsable ? »** Le modèle ne peut que ralentir un paiement. La décision de payer, d'annuler ou de geler reste aux signataires, et chaque signalement est inscrit sur la chaîne avec ses raisons.

## 10. Ce qu'on garde du travail déjà fait

- L'installation Hardhat, les jetons de test, la mesure du gas (une transaction du garde coûte environ 0,002 $).
- Les recherches sur Drift et sur DORA, le retour du mentor.
- L'accès Bedrock validé chez les deux.
- Le coffre de prêt `BreakerVault` ne sert plus : il sera retiré de `ia-2/` quand `TreasuryGuard` sera en place, et reste dans l'historique Git.
