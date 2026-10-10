# Suivi du projet « Breaker » — qui fait quoi, quand, comment

> **Tableau de bord de l'équipe.** Mis à jour à chaque avancée par Claude, côté Romain et côté Timéo.
> Légende : ✅ fait · 🔄 en cours · ⬜ à faire · ✂️ coupé (manque de temps)
> Détail du projet : [`PLAN.md`](PLAN.md) · Historique : [`JOURNAL.md`](JOURNAL.md) · Brief : [`CONTEXTE.md`](CONTEXTE.md)

**Dernière mise à jour :** 2026-10-10 17:10, par Claude (Romain) — R1 validé sur les données de Timéo
**Rendu (gel définitif) :** dim. 11/10 **12:00** · **Checkpoint :** sam. **18:30** · **Pitch :** dim. 13:00

---

## 0. Le projet en 3 lignes

Un **garde antifraude pour la trésorerie crypto des entreprises** (portefeuille multisig sur Avalanche).
1. Chaque paiement est noté **avant** son exécution, à partir du comportement on-chain et d'un **oracle IA qui lit les signalements de fraude sur le Web** (pont Web2 → Web3).
2. S'il est suspect, le portefeuille du client exige des signatures en plus ou une mise en attente, et alerte les signataires.
3. Notre outil ne détient jamais les fonds : **les humains gardent le dernier mot**.

---

## 1. Qui fait quoi (vue d'ensemble)

| | **Romain** — `ia-1/` | **Timéo** — `ia-2/` |
|---|---|---|
| **Rôle** | Détection, IA, oracle Web2, dashboard, présentation | Blockchain : contrats, relais, données de trafic et de fraude |
| **Langage** | Python 3.12 | Solidity (contrats), JavaScript/Node (scripts) |
| **Outils** | pandas, scikit-learn, boto3 (Bedrock), BeautifulSoup, Streamlit | Hardhat, OpenZeppelin, ethers, Avalanche Fuji |
| **Modèle Bedrock** | `us.anthropic.claude-sonnet-5-5` | `us.anthropic.claude-opus-5-5` |
| **Machine** | Mac | Windows 11 (sans Docker) |
| **Assistant** | Claude Code | Claude Code (+ Codex en second avis) |

**L'interface entre nous deux : des fichiers JSON Lines dans `shared/`** (format dans `shared/format-evenements.md`).
- `events.jsonl` : la chaîne → Romain. Écrit par le relais de Timéo.
- `alerts.jsonl` : Romain → la chaîne. Lu par le relais de Timéo.
- `flags.jsonl` : l'oracle de Romain → le registre on-chain. Lu par le relais de Timéo.

→ **Romain ne touche jamais à la blockchain, Timéo ne touche jamais à l'IA.** Chacun avance seul à partir de fichiers d'exemple.

---

## 2. Phase 0 — Mise en place (sam. matin → 16:40) ✅

| # | Tâche | Qui | Statut |
|---|---|---|---|
| 0.1 | Repo GitHub privé, structure, synchro automatique toutes les 5 min | Romain | ✅ |
| 0.2 | Brief du hackathon (`CONTEXTE.md`) à partir du guide Notion | Romain | ✅ |
| 0.3 | Timéo raccordé au bon repo, hook de synchro | Timéo | ✅ |
| 0.4 | Accès AWS Bedrock validé (Romain : Sonnet 5.5, Timéo : Opus 5.5) | Les deux | ✅ |
| 0.5 | Rencontre avec le mentor Team1 + analyse du retour ; [source Granola](https://notes.granola.ai/t/7bf42777-eba3-48f0-a9ab-3780744381e7) référencée dans `shared/retour-mentor-team1.md` | Les deux | ✅ |
| 0.6 | Choix du sujet : **axe 2, trésorerie crypto + oracle Web2 → Web3** | Les deux | ✅ |
| 0.7 | Plan d'action validé (`PLAN.md`) | Les deux | ✅ |
| 0.8 | Base Hardhat, jetons de test, mesure du gas (une pause ≈ 0,002 $) | Timéo | ✅ |
| — | *Coffre de prêt `BreakerVault` (axe 4) : abandonné au pivot, réutilisé en partie* | Timéo | ✂️ |

---

## 3. Phase 1 — Fondations (sam. 16:40 → 18:30)

| # | Tâche | Qui | Comment / outil | Fini quand | Statut |
|---|---|---|---|---|---|
| T1 | **Format des échanges** : `events.jsonl`, `alerts.jsonl`, **`flags.jsonl`** + fichiers d'exemple dans `shared/echantillons/` | Timéo | Markdown + JSON écrit à la main | Romain peut lancer son code sur les exemples | ✅ 16:41 (v2 : `events`, `alerts`, `flags`, `labels` + exemples) |
| T2 | **Contrat `TreasuryGuard`** : multisig M sur N, proposition, approbation, exécution, signalement de risque (signatures en plus / mise en attente), plafond par période, gel, expiration des clés | Timéo | Solidity + Hardhat + OpenZeppelin, tests en local | Les tests passent, dont le scénario de fraude avec et sans garde | ✅ 16:55 (20 tests passent, `cd ia-2 && npm test`) |
| R1 | **Moteur de score** : lit `events.jsonl`, tient l'historique (destinataires connus, montants habituels, rythme), applique les règles, écrit `alerts.jsonl` avec un score et des raisons | Romain | Python + pandas | Tourne sur l'exemple de T1 | ✅ 17:10 validé sur le **test indépendant de Timéo** : 100 % des fraudes freinées ou arrêtées, 89 % des montants en attente, 0,9 % de faux `hold` (`shared/validation-R1.md`) |
| R8a | **Oracle, cœur** : lit une page Web locale → repère les adresses `0x…` → Bedrock dit « accusation / mention / démenti » + **citation exacte** → le code vérifie la citation → écrit `flags.jsonl` | Romain | Python + BeautifulSoup + boto3 (Bedrock), **partage de connexion** | Une page synthétique donne un signalement vérifié | ✅ 17:07 (6 pages pièges, 6/6 justes et stables ; injection résistée ; 17 tests) |
| R7a | **Formulaire du checkpoint** (problème, solution, stack) : texte prêt en section 8 de `PLAN.md` | Romain | — | Formulaire envoyé à 18:30 | ⬜ |
| ★ | ✅ **CHECKPOINT 18:30** : confirmer le track 1, axe 2 | Les deux | — | — | ⬜ |

---

## 4. Phase 2 — Première démo de bout en bout (sam. 18:30 → 23:00)

| # | Tâche | Qui | Comment / outil | Fini quand | Statut |
|---|---|---|---|---|---|
| T2 | `TreasuryGuard` terminé | Timéo | Hardhat | Tous les tests passent | ✅ 16:55 |
| T8 | **Registre des adresses signalées** (dans le Guard ou un contrat `RiskRegistry`) : adresse → niveau, hash de la preuve, expiration | Timéo | Solidity | Un paiement vers une adresse signalée déclenche la friction | ✅ 16:55 (`RiskRegistry.sol`, branché au portefeuille, testé) |
| T3 | **Relais** chaîne ↔ fichiers : écrit `events.jsonl`, lit `alerts.jsonl` et `flags.jsonl` et les envoie sur la chaîne | Timéo | Node + ethers | Une alerte de Romain change réellement le sort d'un paiement | ⬜ |
| T4 | **Générateur de trafic normal** : salaires, fournisseurs habituels, nouveau fournisseur légitime, renouvellement de clé | Timéo | Node, graines aléatoires fixées | Fichier d'entraînement de plusieurs centaines de paiements | ✅ 17:25 (`shared/donnees/train.events.jsonl` : 362 paiements normaux sur 60 jours, + `carnet.json`) |
| R2 | **Modèle d'anomalie** appris sur le trafic normal, combiné aux règles ; seuils des 3 niveaux réglés sur l'entraînement | Romain | scikit-learn (Isolation Forest) | Score et raisons sur chaque paiement | ⬜ |
| R8b | **Corpus Web synthétique** (~30–50 pages) avec pièges : vraies accusations, mentions neutres, démentis, adresses de dons, **tentatives d'empoisonnement** | Romain | Pages HTML générées (Bedrock peut aider à les écrire) | Corpus séparé en « mise au point » et « test » | ⬜ |
| R5a | **Dashboard v1** : paiements en cours, score, raisons, état | Romain | Streamlit | Affiche les alertes en direct | ⬜ |
| T5 | **Scénarios de fraude** (au moins 5) : signataires trompés, clé volée, rafale, goutte-à-goutte sous le plafond, baisse du seuil avant l'attaque, **paiement vers une adresse signalée sur le Web** | Timéo | Node, **autres graines que l'entraînement** | Fichier de test étiqueté | ✅ 17:25 (`shared/donnees/test.*` : 54 paiements frauduleux, 15 épisodes, 6 variantes) |
| ★ | 🎯 **23:00 — DÉMO DE BOUT EN BOUT EN LOCAL** : page Web → signalement → registre → paiement ralenti → alerte dans le dashboard | Les deux | Intégration | Ça tourne, même moche | ⬜ |

---

## 5. Phase 3 — Démo réelle et finition (sam. 23:00 → dim. 03:00)

| # | Tâche | Qui | Comment / outil | Fini quand | Statut |
|---|---|---|---|---|---|
| T6 | **Déploiement sur Avalanche Fuji** + rejeu de la démo, avec les liens de l'explorateur | Timéo | Hardhat + faucet Fuji, wallets **de test** | La démo tourne sur Fuji | ⬜ |
| R3 | **Explication de l'alerte** par Bedrock : quelques phrases pour un signataire, chaque fait relié à une transaction ; repli sur un texte à trous si Bedrock est injoignable | Romain | boto3, `BEDROCK_MODEL_ID` | Alerte lisible par un non-spécialiste | ⬜ |
| R4 | **Rapport d'incident** par Bedrock : chronologie, montants, décisions, preuves | Romain | boto3 | Rapport généré sur la fraude de démo | ⬜ |
| R8c | **Oracle complet** : croisement de plusieurs sources + réputation des sources, expiration des signalements | Romain | Python | **Une tentative d'empoisonnement est rejetée** | ⬜ |
| R5b | **Dashboard v2** : preuves Web (lien, citation), boutons « valider » / « annuler », chiffres clés | Romain | Streamlit | Suffit à filmer la démo | ⬜ |
| T5+ | Variantes de fraude supplémentaires | Timéo | Node | — | ⬜ |
| T9 | **Traçage des fonds — données** (bonus, `PLAN.md` §4 ter) : événements `token_transfer` sortants des adresses signalées, scénario « arnaqueur → 3 mules + dusting d'un innocent », `shared/services-connus.json` | Timéo | Node + ethers | La mule est reliée à l'adresse signalée dans `events.jsonl` | ⬜ |
| R9 | **Traçage des fonds — règle** (bonus) : ≥ 10 % des fonds d'une adresse signalée → `step_up` (`TAINTED_FUNDS`), 1 intermédiaire max, services exclus, dusting ignoré | Romain | Python | La mule est ralentie, l'innocent « dusté » ne l'est pas | ⬜ |
| ⚠️ | **Renouveler la clé Bedrock de Timéo avant 03:28** | Timéo | Workshop Studio | Appel de test réussi | ⬜ |

---

## 6. Phase 4 — Mesures (dim. 02:00 → 09:00, sommeil à tour de rôle)

| # | Tâche | Qui | Comment / outil | Fini quand | Statut |
|---|---|---|---|---|---|
| T7 | **Mesure du gas** des transactions du Guard et du registre (pour le modèle économique) | Timéo | `npm run gas` | Tableau dans `shared/` | ✅ 16:55 (`shared/frais-gas.md` : une alerte ≈ 0,002 $) |
| R6 | **Évaluation** sur le fichier de test : taux de détection, précision, faux positifs, délai de signalement, fonds protégés + **précision de l'oracle** et **délai Web2 → chaîne** | Romain | Python | Tableau de chiffres dans `shared/mesures.md` | ⬜ |
| — | Rejouer les mesures, corriger | Timéo | — | Chiffres définitifs | ⬜ |

---

## 7. Phase 5 — Livrables et pitch (dim. 09:00 → 12:00)

| # | Livrable obligatoire | Qui | Outil | Statut |
|---|---|---|---|---|
| L1 | **Vidéo démo** (2–3 min) | Timéo | Enregistrement d'écran | ⬜ |
| L2 | **README final** : problème, architecture, installation, limites connues | Romain | Markdown | ⬜ |
| L3 | **Pitch deck** (8 slides max) : problème, cible, solution, démo, business model, équipe | Romain | Slides | ⬜ |
| L4 | **Fiche défense** (1 page) : scénario, NIST CSF, OWASP/ATLAS, métriques, limites | Romain | Markdown/PDF | ⬜ |
| L5 | **Playbook de réponse** : automatique vs humain, qui est alerté, documentation | Romain | Markdown | ⬜ |
| L6 | **Slide conformité** : LCB-FT (filtrage des contreparties), Travel Rule, MiCA, AI Act (supervision humaine) ; à faire valider par le mentor KPMG | Romain | Slides | ⬜ |
| L7 | **PoC de bout en bout** fonctionnel | Les deux | — | ⬜ |
| L8 | **Vérification « zéro secret »** dans le repo + **accès du jury** au repo | Timéo | `git log`, GitHub | ⬜ |
| — | Atelier coaching pitch (10:00) | Les deux | — | ⬜ |
| — | Répétition du pitch (Round 1 : 5 min + 2 min de questions) | Les deux | — | ⬜ |
| ★ | 🧊 **RENDU 12:00** | Les deux | — | ⬜ |

---

## 8. Comment on travaille ensemble

| Sujet | Règle |
|---|---|
| **Dossiers** | Romain écrit dans `ia-1/`, Timéo dans `ia-2/`. Dans `shared/`, on prévient dans `JOURNAL.md` avant de modifier un fichier de l'autre |
| **Synchro Git** | Automatique : à la fin de chaque réponse de Claude + toutes les 5 min (pull, commit, push). Commits préfixés `[ia-1]`, `[ia-2]` ou `[shared]` pour les étapes importantes |
| **Communication** | Chaque avancée = une entrée en haut de `JOURNAL.md` + la tâche cochée ici. Les questions pour l'autre vont dans le journal, en gras |
| **Formats** | `shared/format-evenements.md` ne change plus sans prévenir l'autre |
| **Bedrock** | Chacun ses identifiants dans `.env` (ignoré par Git). Modèle lu dans `BEDROCK_MODEL_ID`. **Le Wi-Fi de l'école bloque Bedrock : partage de connexion obligatoire** |
| **Secrets** | Jamais de clé dans le repo ni dans un message. Wallets **de test** uniquement |
| **Données** | 100 % synthétiques : pages Web, transactions, entreprise fictive « NovaTreasury » |
| **En cas de retard** | On coupe dans le périmètre, jamais dans la démo. Ordre de coupe : expiration des clés → gel → plafond (contrat) ; réputation des sources → croisement (oracle) |

---

## 9. Points de contrôle à ne pas rater

| Heure | Quoi | Statut |
|---|---|---|
| Sam. 18:30 | Checkpoint officiel (formulaire problème / solution / stack) | ⬜ |
| Sam. 23:00 | Démo de bout en bout en local | ⬜ |
| Dim. 03:00 | Démo sur Fuji + clé Bedrock de Timéo renouvelée | ⬜ |
| Dim. 09:00 | Chiffres définitifs | ⬜ |
| Dim. 10:00 | Atelier coaching pitch | ⬜ |
| Dim. 12:00 | 🧊 Rendu | ⬜ |
| Dim. 13:00 | Round 1 | ⬜ |
