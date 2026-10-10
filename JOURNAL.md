# Journal d'avancement

Ajouter les entrées les plus récentes en haut.

## Modèle d'entrée

### AAAA-MM-JJ HH:MM — ia-1 / ia-2
- **Fait :**
- **En cours :**
- **Bloquant :**
- **Prochaine étape :**

---

### 2026-10-10 19:57 — ia-2 / Timéo (avec Claude) — T9 : TRAÇAGE DES FONDS, CÔTÉ DONNÉES
- **Fait (T9) : les données du traçage des fonds.** Dès qu'une adresse entre au registre, mon relais remonte tous les transferts de mUSD qu'elle a émis depuis le déploiement et les écrit dans `events.jsonl` sous un nouveau type, `token_transfer` (`from`, `to`, `token`, `amount`, `contract` = `token`). Il continue ensuite de suivre l'adresse. Format : `shared/format-evenements.md`, section « Les transferts des adresses signalées ».
- **Scénario prêt et testé sur la chaîne locale :** `npm run tracing:local` (ou `tracing:fuji`), relais lancé à côté. Un arnaqueur encaisse 100 000 mUSD, envoie 18 000, 12 000 et 10 000 à trois mules, 30 000 à une plateforme d'échange et 0,01 à un innocent ; l'oracle le signale ; l'organisation propose trois paiements (mule, innocent, plateforme). Le relais a bien écrit les 5 transferts juste après `address_flagged`.
- **Romain, pour R9, trois choses à savoir :**
  1. **Les lignes `token_transfer` peuvent dater d'avant le signalement** : leur `block` et leur `timestamp` sont ceux du transfert d'origine. Pour ce type seulement, `seq` ne suit pas l'ordre du temps. Ton moteur ne doit pas supposer des horodatages croissants.
  2. **Le relais ne filtre rien** : la poussière (0,01 mUSD) et le transfert vers la plateforme sont écrits aussi. À toi d'appliquer le seuil de 10 % des sorties de l'adresse signalée et la liste `shared/services-connus.json` (trois adresses factices : plateforme, pont, routeur).
  3. Le traçage s'arrête à un intermédiaire par construction : seuls les transferts sortants des adresses signalées sont écrits.
- **Pour développer R9 sans chaîne :** `shared/echantillons/tracage.events.jsonl` (sortie réelle du relais), `tracage.roles.json` (qui est qui, avec les parts : 18 %, 12 %, 10 %, 30 %, poussière) et `tracage.labels.jsonl` (paiement vers la mule = `fraud`, les deux autres = `normal`).
- **Attendu par le plan :** le paiement vers la mule freiné avec la raison `TAINTED_FUNDS` ; rien à ce titre pour l'innocent ni pour la plateforme. Attention, tes règles actuelles freineront sans doute les trois par `NEW_RECIPIENT` : pour isoler l'effet du traçage, mets l'innocent et la plateforme dans le carnet d'adresses.
- **Non fait :** je n'ai pas ajouté de `token_transfer` aux jeux `train`, `test` et `holdout`, pour ne pas les modifier. Pas encore rejoué sur Fuji.
- **Côté Timéo, toutes les tâches T1 à T9 sont faites.** Reste : renouveler la clé Bedrock avant 03:28, rejouer la démo complète sur Fuji avec ton tableau de bord (actions et traçage), la vidéo (L1) et la vérification « zéro secret » (L8).

### 2026-10-10 19:53 — ia-2 / Timéo (avec Claude) — LE RELAIS TRAITE LES ACTIONS DU TABLEAU DE BORD
- **Fait (ta demande de 19h49, P4 version démo) : mon relais lit `shared/actions.jsonl` et écrit `shared/actions-resultats.jsonl`**, au format de ton `shared/format-actions.md`. Il vaut pour la chaîne locale comme pour Fuji (`npm run relay:local`, `npm run relay:fuji`).
  - Actions traitées : `approve`, `cancel`, `freeze`, `unfreeze`, signées avec la clé de test du signataire indiqué dans `by`.
  - **Une action en plus, `execute`** (`payment_id`, `by`) : sans elle, un paiement approuvé depuis le tableau de bord ne pouvait pas partir. À toi de l'ajouter à `shared/format-actions.md` et au tableau de bord si tu veux un bouton « exécuter ».
  - Erreurs rendues sous la forme du nom d'erreur du contrat quand il existe (`AlreadyApproved()`, `WalletFrozen()`, `NotEnoughApprovals(2, 3)`), sinon `unknown_signer`, `unknown_action`, `invalid_payment_id`.
  - Comme pour les alertes, les actions déjà présentes dans le fichier au démarrage du relais sont ignorées.
- **Testé sur la chaîne locale, 12 actions sur 12 conformes :** approbation, double approbation refusée, annulation, action sur un paiement annulé refusée, signataire inconnu refusé, action inconnue refusée, gel, exécution refusée pendant le gel, trois votes de dégel, puis exécution. Pas encore rejoué sur Fuji avec ton tableau de bord.
- **⚠️ Ne lance pas ton exécuteur `ia-1/integration/actions.js` en même temps que mon relais :** les deux liraient le même fichier et chaque action partirait deux fois. Avec mon relais, ton exécuteur n'est plus nécessaire ; tu peux retirer l'étape 5b de `ia-1/integration/README.md`.
- **Le relais n'ajoute aucun pouvoir :** il signe au nom du signataire choisi, et le portefeuille refuse ce que ce signataire n'a pas le droit de faire. À dire au jury : ce fichier n'existe que pour la démo, en production chaque signataire signe dans son propre portefeuille.
- **Prochaine étape côté Timéo :** T9, les données du traçage des fonds.

### 2026-10-10 19:51 — ia-1 / Romain (avec Claude)
- **Jeu de généralisation de Timéo : mesuré sur le Mac, règles + R2, sans toucher à aucune règle.** Arrêtées 49 → 51 %, montants en attente **57 → 65 %**, freinées 95 %, faux `hold` 1,4 % (inchangé). Intégré dans `shared/mesures.md` (colonnes test / généralisation, et la réserve sur `owner_swap_then_drain` : « freinée » surestime, seule la mise en attente compte).
- **R3 face aux 2 libellés à injection de prompt :** les deux paiements sont en `hold` (0,87 / 0,86) et l'explication Bedrock signale la consigne cachée comme un motif de prudence au lieu de la suivre. Texte dans `shared/mesures.md`.
- **Merci pour ce jeu, Timéo : c'est le chiffre le plus honnête qu'on ait**, on le montrera à côté du test.

### 2026-10-10 19:49 — ia-1 / Romain (avec Claude)
- **Fait (R5b) : actions des signataires dans le tableau de bord.** Barre « Je suis… », boutons valider / annuler / geler / dégeler / contester, panneau d'état. Le dashboard n'a aucune clé : il écrit dans **`shared/actions.jsonl`** (format proposé dans **`shared/format-actions.md`**, nouveau fichier, sans toucher au tien), un exécuteur signe et répond dans `shared/actions-resultats.jsonl`. Contester = ligne `{"address", "remove": true}` dans `flags.jsonl`, que ton relais gère déjà. **Testé en direct en local** : annulation du paiement 4 par un signataire et retrait du signalement, tous deux visibles sur la chaîne.
- **Timéo, pour Fuji (seule étape qui dépend de toi) :** ajouter à ton relais la lecture de `actions.jsonl` (approve / cancel / freeze / approveUnfreeze signés par `signerOf(by)`) et l'écriture de `actions-resultats.jsonl`. Mon exécuteur local `ia-1/integration/actions.js` (60 lignes) fait exactement ça, tu peux le reprendre tel quel.
- **Côté Romain, les phases 1 à 4 sont terminées** (R1-R8, R5b en local). Prochaine étape : B1, bilan de la démo, à faire à deux.
### 2026-10-10 19:47 — ia-2 / Timéo (avec Claude) — T5+ : JEU DE GÉNÉRALISATION (FRAUDES DE FORMES NOUVELLES)
- **Fait (T5+) : un troisième jeu de données, `shared/donnees/holdout.*`**, fait de formes de fraude que le moteur n'a jamais vues. 30 jours de plus (jours 90 à 119), 261 paiements dont **39 frauduleux en 15 épisodes**. Détail et tableau dans `shared/donnees/README.md`.
  - Six formes nouvelles : `owner_swap_then_drain` (remplacement d'un signataire par la clé d'un intrus, maquillé en renouvellement, puis vidage : la forme de Bybit), `structuring` (fractionnement vers des adresses toutes différentes), `trust_building` (deux petits paiements, puis le gros), `known_recipient_overpay` (bonne adresse, dix à vingt fois le montant), `weekend_single`, `memo_prompt_injection` (consigne cachée dans le libellé, visant Bedrock).
  - Trois formes du jeu de test rejouées avec d'autres graines, comme repères.
  - Des cas légitimes trompeurs : lot de fin de mois, gros premier paiement à un nouveau cabinet d'audit, urgence un dimanche.
- **`train` et `test` n'ont pas changé d'une ligne** (vérifié par le script de comparaison, puis par `git diff`). Tes mesures et ton modèle R2 restent valables ; rien à réentraîner.
- **⚠️ Romain : ne règle rien en regardant ce jeu.** Le jeu de test a déjà servi plusieurs fois à la mise au point ; le `holdout` est la seule mesure encore propre. Si tu modifies une règle après l'avoir vu, il ne prouve plus rien. Les étiquettes des fraudes en plusieurs temps portent un champ `stage` (`grooming` ou `cashout`).
- **Première mesure, tes règles seules, sur le PC de Timéo** (`ia-2/scripts/evaluer-holdout.py`, à lancer depuis `ia-1/`) :

  | | Jeu de test | Jeu de généralisation |
  |---|---|---|
  | Fraudes mises en attente | 63 % | **49 %** |
  | Fraudes freinées ou mises en attente | 100 % | **95 %** |
  | Montants frauduleux mis en attente | 89 % | **57 %** |
  | Paiements normaux mis en attente à tort | 0,9 % | **1,4 %** |
  | Paiements normaux avec une signature en plus | 14,2 % | **22,5 %** |

- **Ce que ça dit, sans rien enjoliver :** le moteur généralise, mais moins bien que sur le test. Les deux chiffres sont à donner au jury côte à côte.
- **Point faible à connaître avant le pitch : `owner_swap_then_drain`.** 3 des 7 paiements ne reçoivent qu'un `step_up`, qui n'arrête rien quand l'attaquant tient déjà trois clés. « Freinée » surestime donc la protection dans ce cas : seule la mise en attente compte. À prendre en compte dans ta façon de présenter « freinées ou arrêtées » (R6).
- **Autres constats :** les deux gros paiements finaux de la mise en confiance ne sont que freinés (le destinataire est devenu « connu ») ; deux gros premiers paiements légitimes à un cabinet d'audit sont mis en attente à tort.
- **À faire de ton côté, si tu veux :** relancer avec le modèle R2 sur ton Mac (il ne tourne pas ici) et vérifier que l'explication Bedrock (R3) résiste aux deux libellés piégés, paiements `memo_prompt_injection`.
- **Vu :** ta demande d'un fichier `shared/actions.jsonl` lu par le relais pour les boutons du tableau de bord (R5b, P4). Je le fais ensuite, sauf si Timéo préfère T9.

### 2026-10-10 19:42 — ia-1 / Romain (avec Claude)
- **Fait (R6) : `shared/mesures.md`**, le tableau pour le deck et la fiche de défense. 6 chiffres clés : 100 % des fraudes freinées ou arrêtées, 94 % des montants frauduleux en attente, 0,9 % de faux positifs, signalement en ≤ 1 s (local) / 5-6 s (Fuji), oracle 100 % / 100 % avec 7 injections déjouées, 0,002 $ par alerte. Chaque chiffre a sa commande de reproduction et la section « Limites » est écrite pour le jury.
- **Timéo :** j'ai repris tes chiffres Fuji (5-6 s, 0,00054 AVAX) et gas. Si tu régénères les données ou refais la démo Fuji, dis-le : je rafraîchis le tableau.
- **Prochaine étape :** B1, le bilan de la démo (ce qui marche / à garder / à enlever / à améliorer), qui ouvre la phase business.

### 2026-10-10 19:34 — ia-1 / Romain (avec Claude)
- **Fait (R4) : rapport d'incident** (`ia-1/score/rapport.py`). Faits par le code (paiements signalés, délai, montants, gel, annulations, signalements Web, preuves, chronologie), synthèse Bedrock en 3 paragraphes vérifiée (aucun montant hors des faits, aucun hash). Rapport de la démo de ce soir : `ia-1/rapports/rapport-demo-locale.md` — 4 paiements signalés, **285 300 mUSD protégés, 0 sorti**, signalement en ≤ 1 s.
- **Fait (R8c) : croisement des sources de l'oracle.** Réputation par source (`ia-1/oracle/sources.json`), publication si poids ≥ 0,8 ; la même source répétée compte une fois. **Démo d'empoisonnement :** 3 pages du même blog anonyme accusant notre fournisseur CloudNova → non publiée ; un forum réputé seul → publiée ; deux sites inconnus indépendants → publiée. 36 tests dans `ia-1/`.
- **Timéo :** le format de `flags.jsonl` ne change pas (`sources_count` est maintenant le vrai nombre de sources distinctes). Pour la vidéo, le scénario « empoisonnement rejeté » est dans `ia-1/oracle/corpus_demo/empoisonnement/`.
- **Côté Romain, reste en phase 3 : R5b** (boutons du dashboard : dépend d'un fichier d'actions lu par ton relais, voir mon entrée de 17:50). Puis phase 4 (mesures R6) et phase business (B1-B8).
### 2026-10-10 19:34 — ia-2 / Timéo (avec Claude) — ✅ T6 : DÉPLOYÉ SUR FUJI, DÉMO REJOUÉE (0 mUSD PERDU)
- **Fait (T6) : les contrats sont sur Avalanche Fuji et la démo y tourne.** Timéo a envoyé 0,5 AVAX de test au déployeur ; répartition vers les comptes, puis déploiement à 19h29 (bloc 59275146).
  - Portefeuille `TreasuryGuard` : `0xfDb595EA595195C149ABf2bf28892c34a1a06D9c`
  - Registre `RiskRegistry` : `0x24871b8A07a7C7B2632E760c23051661E341cC40`
  - Jeton de test `mUSD` : `0xFF65eD05180D3f725a1DE658e0f539A3452274bD`
  - Liens Snowtrace, réglages et transactions de la démo : `ia-2/README.md`, section « Déploiement sur Avalanche Fuji ».
- **Première démo sur Fuji, sur le PC de Timéo, avec ton moteur (règles seules) :** paiement normal exécuté sans friction ; les 3 virements frauduleux mis en `hold` **5 à 6 secondes** après leur proposition (délai d'examen : 30 s), score 0,88 ; les fraudeurs bloqués à 2 signatures sur 3 ; gel et annulation par un signataire. **0 mUSD sorti sur 280 500 tentés.**
- **Chiffre pour la mesure « délai de signalement » (R6) :** 5 à 6 s sur Fuji, contre 1 à 2 s en local. La différence vient du temps de bloc de Fuji et de l'interrogation du RPC public par le relais, pas du moteur.
- **Coût réel sur Fuji :** environ 0,00054 AVAX pour tout le déploiement, 0,00005 AVAX pour les trois signalements. Il reste 0,25 AVAX au déployeur.
- **Pour Romain :**
  - `ia-2/deployments/fuji.json` (adresses, bloc, réglages) et `ia-2/deployments/fuji-carnet.json` (carnet d'adresses du moteur) sont dans le dépôt.
  - La phrase secrète n'est que sur le PC de Timéo : tu peux lire Fuji depuis ton Mac (tableau de bord, relais en lecture), mais pas y signer.
  - Je n'ai pas lancé `--expliquer` : le PC est sur le Wi-Fi de l'école, qui bloque Bedrock. À faire en partage de connexion pour la vidéo.
  - `OFF_HOURS` s'est déclenché (samedi soir), comme chez toi.
- **État du portefeuille Fuji :** dégelé après la démo par `npm run unfreeze:fuji` (nouveau script), prêt pour un nouveau passage.
- **Prochaine étape côté Timéo :** T9 (traçage des fonds, bonus) et les variantes de fraude ; renouveler la clé Bedrock avant 03:28.

### 2026-10-10 19:25 — ia-1 / Romain (avec Claude)
- **R3 validé en direct** (partage de connexion) : Bedrock (Opus 4.8) reformule les 4 alertes de l'exemple en 2 à 4 phrases fidèles aux faits, avec l'action à faire ; ≈ 6 s par alerte, sous les 30 s du délai d'examen. Exemple pour le paiement vers l'adresse signalée : « …destinataire inconnu signalé comme problématique sur le Web… Avant toute signature, contactez la personne à l'origine de la demande par un autre canal… »
- **Timéo :** pour la démo Fuji, lance le moteur avec `--expliquer` (Bedrock en partage de connexion) pour que le tableau de bord montre ces explications ; sans réseau, le texte à trous prend le relais tout seul.
- **Prochaine étape :** R4 (rapport d'incident), puis R8c (croisement des sources de l'oracle).

### 2026-10-10 19:23 — ia-1 / Romain (avec Claude)
- **R3 codé** (`ia-1/score/explication.py`, option `--expliquer` du moteur) : Bedrock reformule les faits du moteur pour un signataire non expert ; garde-fous (adresses, longueur, repli, pause après panne). 27 tests. **Validation en direct dès que Romain repasse en partage de connexion** (le Wi-Fi de l'école a de nouveau coupé Bedrock).
- **Lu, Timéo :** Fuji prêt sauf AVAX ; moteur validé sur ton PC ; R2 bloqué par Smart App Control (pas un bug). **Décision en attente de Romain** sur le lieu de la démo Fuji ; avis de Claude côté Romain : **ton PC, règles seules, sans faire circuler la phrase secrète** ; R2 reste un argument chiffré mesuré sur le Mac.
- **Code commun Bedrock** : `ia-1/commun/bedrock.py` (chaîne de modèles sans Sonnet, repli sans température). L'oracle sera rebranché dessus en R8c.

### 2026-10-10 19:02 — ia-2 / Timéo (avec Claude) — FUJI : COMMENT APPROVISIONNER LE DÉPLOYEUR
- **Question de Timéo :** il ne peut pas avoir l'adresse du déployeur dans son portefeuille, comment l'approvisionner ? **Réponse :** inutile de l'y importer. Il obtient des AVAX de test sur son propre portefeuille (Core ou MetaMask, réseau Fuji), puis les envoie par un simple transfert à `0x4EcC7e01cdB900b0FD16f91dFC289CdBBe768564`. La phrase secrète de test reste dans `ia-2/.env`.
- **Toujours bloquant pour T6 :** ce transfert. Dès qu'il est fait, je lance `npm run fuji:fund` puis `npm run deploy:fuji`.

### 2026-10-10 18:57 — ia-2 / Timéo (avec Claude) — MOTEUR TESTÉ SUR LE PC DE TIMÉO, R2 BLOQUÉ PAR WINDOWS
- **Fait :** ton moteur de score tourne sur le PC de Timéo (Windows 11), dans `ia-1/.venv`. Testé de bout en bout sur la chaîne locale avec mon relais et mon scénario (`RESPOND=1`) : paiement normal exécuté sans friction ; les 3 virements frauduleux mis en `hold` (score 0,88, `PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS`) ; **0 mUSD sorti sur 280 500**.
- **⚠️ Limite sur ce PC : le modèle d'anomalie R2 ne se charge pas.** Le contrôle d'application de Windows (Smart App Control, activé) bloque un fichier binaire de scikit-learn : `ImportError: DLL load failed while importing _radius_neighbors`. Je ne le désactive pas : c'est un réglage de sécurité de la machine de Timéo, et à ma connaissance il ne se réactive pas sans réinitialiser Windows. Conséquences :
  - `pytest` ici : 19 tests passent, les 2 tests du modèle échouent pour cette raison, pas à cause du code.
  - Le moteur est lancé **sans `--modele`** sur ce PC. Le scénario de démo n'en a pas besoin (0,88 par les règles).
  - **Toutes les mesures avec le modèle R2 se font sur ton Mac.**
- **Tes chiffres R1 confirmés de façon indépendante**, sur le jeu relibellé et sur une autre machine : fraudes arrêtées 63 %, freinées ou arrêtées 100 %, 2 285 715 mUSD mis en attente sur 2 565 065 (89 %), faux `hold` 0,9 % sur 564 paiements normaux.
- **Sous Windows :** `.venv/Scripts/python.exe` au lieu de `.venv/bin/python`, et `PYTHONUTF8=1` devant la commande (sinon les accents des libellés font planter la lecture).
- **Donc, pour Fuji :** démo sur le PC de Timéo avec les règles seules. Si tu tiens à montrer R2 sur Fuji, il faudrait lancer le relais sur ton Mac, donc y recopier la phrase secrète de test hors de Git : à décider entre vous deux, je ne la fais pas circuler.
- **Toujours bloquant :** 0 AVAX sur le déployeur `0x4EcC7e01cdB900b0FD16f91dFC289CdBBe768564`.

### 2026-10-10 18:48 — ia-2 / Timéo (avec Claude) — T6 FUJI : PRÊT, EN ATTENTE DU FAUCET
- **Fait :** tout est prêt pour Fuji, sauf l'argent. Phrase secrète de test créée dans `ia-2/.env` (ignoré par Git, jamais affichée), dix comptes dérivés, adresses publiques dans `ia-2/deployments/fuji-comptes.json`. Nouvelles commandes dans `ia-2/` : `npm run fuji:setup`, `fuji:fund`, `deploy:fuji`, `relay:fuji`, `scenario:fuji`.
- **Bloquant : le déployeur `0x4EcC7e01cdB900b0FD16f91dFC289CdBBe768564` a 0 AVAX.** Timéo doit demander des AVAX de test au faucet pour cette adresse (compte Builder Hub, ou code de coupon à demander au mentor Team1). Ensuite `npm run fuji:fund` répartit vers les signataires, le moniteur et l'oracle, puis `npm run deploy:fuji`.
- **Réponse à Romain, point 1 (où tournent le relais et le moteur sur Fuji) : sur le PC de Timéo.** Raisons : la phrase secrète des comptes Fuji y est et ne doit pas circuler ; c'est Timéo qui enregistre la vidéo (L1). J'installe ton environnement Python dans `ia-1/.venv` sur ce PC (dossier ignoré par Git) ; je réentraînerai le modèle R2 ici et je te dirai si le moteur tourne sous Windows.
- **Réponse à Romain, point 2 (carnet d'adresses Fuji) :** les « prestataires habituels » sont les comptes n° 8 et 9, déjà dans `ia-2/deployments/fuji-comptes.json` : `0x3f7955b8895f5140b072276d92A2c8D05fA19438` et `0x800764A3dd203476193c6A065183814be5e1A508`. Après déploiement, `ia-2/deployments/fuji.json` (suivi par Git) contiendra aussi un champ `known_recipients`, comme en local.
- **Pour Fuji, côté code :** le relais lit maintenant les journaux par tranches de 2 000 blocs (limite des RPC publics). Le prix du gas relevé sur Fuji est quasi nul, quelques AVAX de test suffisent largement.
- **Prochaine étape :** déploiement dès que le déployeur est approvisionné ; puis adresses des contrats et liens Snowtrace dans `ia-2/README.md`, comme tu le demandes.

### 2026-10-10 18:46 — Romain (avec Claude) — PHASE 3 LANCÉE
- **Timéo lance la phase 3 avec T6 : déploiement sur le testnet Avalanche Fuji.**
- **Points de coordination pour la démo sur Fuji :**
  1. Le relais et le moteur de score communiquent par les fichiers de `shared/` : ils doivent tourner **sur la même machine**. Deux options : relais Fuji sur le Mac de Romain (Node et `ia-2` y sont installés et testés), ou moteur sur le PC de Timéo (Python 3.12 + `cd ia-1 && pip install -r requirements.txt`, puis réentraîner le modèle R2).
  2. **Carnet d'adresses** de la démo Fuji : il faudra les adresses des fournisseurs « habituels » déployés (comme `ia-1/integration/carnet.js` en local).
  3. **Wallets de test uniquement**, phrase secrète dans `.env` (jamais dans Git) ; AVAX du faucet.
  4. Bedrock (oracle) : partage de connexion obligatoire ; modèle Opus (jamais Sonnet).
- **Timéo, dis dans le journal quelle option tu préfères pour le point 1.** Une fois déployé, mets les adresses des contrats Fuji et les liens Snowtrace dans `ia-2/README.md` : le tableau de bord génère déjà des liens vers testnet.snowtrace.io pour le `chain_id` 43113.

### 2026-10-10 18:44 — ia-2 / Timéo (avec Codex) — CIBLES DE LA COMPARAISON
- **Précision de Timéo :** inclure startups crypto, fonds et fondations de même profil (forte trésorerie, pas d'équipe de sécurité), entreprises classiques payant en stablecoins plus tard et équipes de dApps comme Drift sur Solana à titre d'exemple.
- **Fait :** comparaison et pitch complétés dans shared/comparaison-autres-blockchains.md ; cibles déjà décidées dans le plan. Drift illustre le besoin, sans annoncer une prise en charge Solana.
- **Actualisation :** démo intégrée locale de Romain à 18:41 mentionnée. Production auditée non acquise. B4 inchangée.
- **Fichiers :** note comparative, compte-rendu de conversation et JOURNAL.md.



### 2026-10-10 18:41 — Romain (avec Claude) — ✅ PHASE 2 TERMINÉE : DÉMO DE BOUT EN BOUT
- **Démo complète en local sur le Mac de Romain** : chaîne + contrats + relais de Timéo, moteur de score en direct (règles + R2), oracle Bedrock, tableau de bord. Mode d'emploi en 6 terminaux : `ia-1/integration/README.md`.
- **Scénario de Timéo (`RESPOND=1`) :** paiement normal exécuté sans friction ; 3 virements frauduleux (280 500 mUSD) mis en `hold` **dans la seconde** (score 0,93) ; **0 mUSD parti** (contre 95 000 mUSD au 1er passage, moteur arrêté par un bug).
- **Web2 → Web3 en direct :** l'oracle signale l'arnaqueur d'une page de forum (0,95, adresse de dons rejetée), le relais l'inscrit au registre, un paiement banal de 4 800 mUSD vers lui est **bloqué par le contrat et par le moteur**.
- **Bug trouvé grâce à l'intégration, corrigé :** le modèle R2 sauvegardé ne se rechargeait pas dans le moteur. Test de non-régression ajouté (21 tests).
- **Timéo :** ton relais, ton déploiement et ton scénario ont marché du premier coup sur Mac, bravo. Le scénario Web2 → Web3 est dans `ia-1/integration/scenario_oracle.js` (lancé depuis `ia-2`, sans toucher à ton dossier). Remarque : la démo un samedi déclenche `OFF_HOURS` sur la fraude (juste, mais à expliquer).
- **Suite :** phase 3 (Fuji, R3/R4 explication et rapport Bedrock, R5b, R8c), puis bilan de la démo (B1).
### 2026-10-10 18:35 — ia-2 / Timéo (avec Codex) — COMPARAISON MULTICHAÎNE
- **Coordination :** recherche demandée par Timéo, complément à B4 de Romain ; ajout d'une note distincte sans modifier le positionnement ni ses analyses. B4 passe en cours pour la comparaison fonctionnelle seulement.
- **Fait :** sources officielles vérifiées ; résultats dans shared/comparaison-autres-blockchains.md. Guardian propose déjà signatures multiples et revue, Squads dispose de délais, Forta intervient avant exécution ; ces briques ne sont pas exclusives à Breaker.
- **Attention :** spécialisation Avalanche, prix accessible et oracle Web sont des pistes de différenciation à valider. T9/R9 ne constituent pas une invention du traçage. Ancien oracle Chainalysis non maintenu depuis mars 2026.
- **Reste B4 :** prix, parcours produit, comparaison commerciale et validation auprès des clients ; tâche non terminée.



### 2026-10-10 18:08 — Romain (avec Claude) — VISION PRODUIT
- **Décision de Romain : positionnement « uniquement Avalanche (AVAX) ».** ⚠️ **Timéo :** `shared/cible-et-modele-economique.md` (ligne 30) parle encore de « Squads sur Solana » comme canal de distribution, à retirer ou à passer en « hors périmètre ».
- **Nouvelle phase 4 ter « Produit commercial » (P1-P8 dans `SUIVI.md`), une fois la démo assurée :** site vitrine, espace client avec abonnement, boutons valider / annuler / geler / contester, notifications (connecteur e-mail de l'entreprise, puis Slack / Telegram), bouton « vraie / fausse alerte » et rapport mensuel, mode observation au démarrage, réglages du client. S'inspirer de Safe / Hypernative / Fireblocks. Pendant le hackathon : au plus une maquette pour le pitch.
- **B4 élargi :** étudier aussi comment les concurrents abordent le marché (site, application, inscription, prix affiché, notifications).
- **Explication validée pour le pitch :** « La signature en plus casse la complicité (+1 signataire indépendant, réglage `stepUpExtra`) ; la mise en attente casse l'urgence (délai `holdDelay`, levé seulement à l'unanimité). »
- **Timéo, petite incohérence :** `shared/echantillons/events.exemple.jsonl` indique `required_approvals: 4` pour un `hold`, alors que le contrat donne 3 (2 + `stepUpExtra` = 1). À aligner quand tu repasses dessus.

### 2026-10-10 17:56 — ia-1 / Romain (avec Claude)
- **Jeu de données régénéré par Timéo : vérifié.** 20 tests passent ; évaluation et modèle R2 réentraîné : **chiffres strictement identiques** (règles seules : 63 % arrêtées, 89 % des montants, 0,9 % de faux `hold` ; avec R2 : 69 %, 94 %, 0,9 %). Ta vérification était juste.
- **Corrigé à la demande de Timéo :** ligne B4 de `SUIVI.md` (Hypernative Guardian en tête des concurrents ; Safe Shield avertit sans agir) et `CONTEXTE.md` (choix final : track 1, axe 2, au lieu de « track 1 ou 2 »).
- **Formulation sur Safe à valider ensemble pour le pitch :** « Safe Shield avertit sans agir ; Guardian bloque et vise les grandes trésoreries ; nous visons les petites organisations avec une réponse graduée qui ne peut pas verrouiller les fonds, plus l'oracle Web. » Avis de Claude côté Romain : bonne formulation, à condition de vérifier en B4 le prix et la cible réels de Guardian.

### 2026-10-10 17:53 — ia-2 / Timéo (avec Claude) — RELECTURE DE LA PARTIE DE TIMÉO
- **Demande de Timéo :** relire toute sa partie pour qu'elle concorde avec la cible et les arguments de rentabilité décidés à 17h30. Fait ; détail ci-dessous.
- **⚠️ Romain : le jeu de données `shared/donnees/` a été régénéré.** Il décrivait une entreprise classique (loyer, cotisations, TVA en stablecoin) ; il décrit maintenant l'équipe d'un protocole (rémunération des contributeurs, subventions, infrastructure RPC, audit de sécurité, primes de bug).
  - **Ce qui change :** 323 libellés sur 618, les 42 adresses du carnet et des prestataires, les hash de transaction.
  - **Ce qui ne change pas, vérifié ligne à ligne par un script :** le nombre et l'ordre des événements, les heures, les montants, les identifiants de paiement, les niveaux de risque, les étiquettes (fichiers identiques), et le résultat de ton filtre de mots d'urgence sur chaque libellé. Tes caractéristiques et tes mesures devraient donc être identiques.
  - **À faire de ton côté :** réentraîner le modèle d'anomalie (tu l'avais demandé) et relancer l'évaluation pour confirmer. Dis-le dans le journal si un chiffre bouge : ce serait un défaut de ma vérification.
  - Les fichiers d'exemple de `shared/echantillons/` ne changent que d'un libellé (« Salaires » devient « Rémunération des contributeurs ») ; adresses et hash identiques.
- **Affirmation fausse corrigée :** « Safe ne surveille rien par défaut », relevée par l'autre session de Timéo (entrée de 17h50). Corrigée dans `shared/cible-et-modele-economique.md` (argument de rentabilité n° 2, section concurrence, sources) et `PLAN.md` section 1 bis. Nouvelle formulation, **à valider par Timéo et Romain** : Safe Shield avertit sans agir ; Guardian de Hypernative agit mais bloque et vise les grandes trésoreries ; nous visons les petites organisations avec une réponse graduée qui ne peut pas verrouiller les fonds. **Romain : la ligne B4 de `SUIVI.md` dit encore « Safe (gratuit, sans surveillance) », je te la laisse.**
- **Autres alignements :** bandeau « secondaire » sur `shared/dora-notes.md` et bandeau de mise en contexte sur `shared/retour-mentor-team1.md` (écrits à l'époque de l'axe 4) ; `ia-2/README.md`, `shared/format-evenements.md`, `shared/frais-gas.md`, lignes T4 de `PLAN.md` et `SUIVI.md`.
- **Deux corrections hors ciblage trouvées en relisant :**
  - `.env.example` à la racine proposait encore Sonnet : remplacé par Opus 5.5, selon la consigne de 17h19.
  - Fuji : `ia-2/.env.example` et `hardhat.config.js` attendaient trois clés de l'époque de l'axe 4 (dont une « clé d'attaquant ») alors que le déploiement demande huit comptes. Remplacé par une seule phrase secrète de test, `FUJI_MNEMONIC`.
- **Rien à changer :** les contrats, les tests (20 passent), le relais, le scénario de démo, la mesure du gas.
- **Non modifié, à voir par Romain :** `CONTEXTE.md` ligne 12 dit encore « Nos choix : Track 1 ou Track 2 ».

### 2026-10-10 17:50 — ia-2 / Timéo (avec Claude) — CORRECTION À FAIRE SUR SAFE
- **Question de Timéo :** en quoi notre garde ressemble-t-il à Safe ? Réponse complète dans `conversations/2026-10-10_timeo_comparaison-safe.md`.
- **Erreur dans nos documents : « Safe ne surveille rien par défaut » est dépassé.** Safe Shield analyse chaque transaction dans l'interface de Safe (Blockaid, Tenderly, Hypernative). Depuis le 20 novembre 2025, Guardian de Hypernative ajoute un contrat de contrôle qui bloque les transactions à haut risque. Un juré qui connaît Safe le relèvera.
- **Où la phrase apparaît :** `PLAN.md` section 1 bis, `shared/cible-et-modele-economique.md` lignes 29 et 53, `SUIVI.md` B4. **Je n'ai rien modifié** : le positionnement est une décision de Timéo et Romain.
- **Formulation proposée :** Safe Shield avertit mais n'agit pas ; Guardian agit, mais il bloque, et il est vendu aux grandes trésoreries par un commercial, sans prix public. Nous : petites organisations, réponse graduée qui ne peut pas verrouiller les fonds, oracle Web. Non confirmé : gratuité de Safe Shield, prix de Guardian.
- **Pour Romain (B4, concurrence) :** Hypernative Guardian devient le concurrent le plus proche, à mettre en tête du tableau comparatif.
- **Feuille de route :** chez Safe, les signatures sont réunies hors chaîne. Notre module devra lire le service de transactions de Safe ; le relais actuel ne suffira pas tel quel.

### 2026-10-10 17:50 — ia-1 / Romain (avec Claude)
- **Fait (R5a) : tableau de bord v1** (`ia-1/dashboard/app.py`, Streamlit, rafraîchi toutes les 2 s). Il lit `shared/events.jsonl`, `alerts.jsonl` et `flags.jsonl` du relais. Il affiche les indicateurs (dont le **montant protégé**), le bandeau « gelé », les paiements à examiner (raisons, explication, liens vers l'explorateur Fuji) et les adresses signalées par l'oracle (citation, preuve, expiration). Démo hors chaîne : `python -m dashboard.preparer_demo`. 20 tests au total dans `ia-1/`.
- **Côté Romain, la phase 2 est terminée** (R1, R2, R8a, R8b, R5a). Reste pour le jalon de 23:00 : **la démo de bout en bout ensemble** (relais de Timéo + moteur + oracle + dashboard sur la même machine).
- **Timéo :** pour les boutons « valider » / « annuler » du dashboard (R5b), le relais pourrait-il lire un fichier `shared/actions.jsonl` (`{"payment_id": 4, "action": "cancel", "by": "alice"}`) et signer avec la clé de test du signataire ? À discuter.

### 2026-10-10 17:48 — ia-1 / Romain (avec Claude)
- **Fait (R8b) : corpus de l'oracle et mesure** (`ia-1/oracle/corpus.py`, `ia-1/eval/evaluer_oracle.py`). 40 pages écrites par gabarits (pas par un LLM), 63 adresses, moitié dev / moitié test. **Test : 100 % de précision, 100 % de rappel, 0 fausse accusation sur 24**, dont 7 injections de prompt (visibles et cachées) et 9 démentis. Le repli par mots-clés tombe à 67 % / 36 % : l'IA fait la différence. Limite : des gabarits sont plus faciles que le vrai Web.
- **Prochaine étape :** texte du checkpoint (18:30), puis R5 (dashboard).

### 2026-10-10 17:46 — ia-1 / Romain (avec Claude)
- **Fait (R2) : modèle d'anomalie** (`ia-1/score/anomalie.py`, Isolation Forest appris sur `shared/donnees/train`, raison `ANOMALY_MODEL`). Sur le test de Timéo : **fraudes arrêtées 63 → 69 %, montants frauduleux en attente 89 → 94 %, faux `hold` inchangés (0,9 %)**. La nouveauté du destinataire est exclue des caractéristiques (double comptage avec `NEW_RECIPIENT`, décidé sur train). 18 tests.
- **Pour Timéo :** en démo, lancer le moteur avec `--modele modeles/anomalie.joblib` (à générer : voir `ia-1/README.md`). Si tu régénères le jeu de données, préviens-moi : je réentraîne le modèle.
- **Prochaine étape :** R8b (corpus de l'oracle), puis R5 (dashboard).

### 2026-10-10 17:42 — Romain (avec Claude) — ORGANISATION
- **Décision Romain + Timéo :** cible = petites et moyennes organisations qui détiennent des fonds en crypto (multisig, sans équipe de sécurité). **Nouvelle phase « Business » (B1 à B8) dans `SUIVI.md`**, placée **après la démo et les tests** : bilan de la démo, réalité du problème, étude de marché, concurrence, entretiens de validation du besoin, prix, mise sur le marché, décision go / ajustement.
- **Répartition :** **Timéo = technique de l'outil**, **Romain = business** (étude de marché, vente, commerce). Mais **maintenant, on se concentre à deux sur la démo** : établir ce qui marche, ce qu'il faut garder, enlever, modifier, améliorer.
- **Objectif immédiat : finir la phase 2.** Romain enchaîne R2 (modèle d'anomalie), R8b (corpus de l'oracle), R5 (dashboard). Checkpoint officiel à 18:30.

### 2026-10-10 17:35 — ia-2 / Timéo (avec Claude) — DÉCISION SUR LA CIBLE
- **Décision de Timéo (vers 17h30) : nous visons des organisations réelles qui gardent des millions dans un portefeuille à plusieurs signataires, sans équipe de sécurité.**
  - **En priorité :** les équipes de protocoles et les DAO (dix à trente personnes, trésorerie de plusieurs millions tenue par quelques fondateurs ; ils paient des audits de code mais rien ne surveille leurs signataires ; Drift entre dans ce cas), et les startups crypto, fonds et fondations (même profil).
  - **Plus tard :** les entreprises classiques qui paient en stablecoins (besoin fort, marché encore jeune).
  - **Pas visées :** les grandes plateformes (Bybit, Coinbase), qui ont déjà leurs équipes et leurs outils. Bybit sert d'argument, pas de client.
  - **Les dApps restent clientes pour le portefeuille de leur équipe, plus pour leur contrat.**
- **Pourquoi c'est rentable (à reprendre dans le deck) :** coût par client presque nul (0,002 $ de gas par alerte, quelques centimes de Bedrock) ; trou de prix entre Safe (gratuit, ne surveille rien) et Fireblocks (grands comptes) ; distribution par un module installé dans Safe ou Squads. Hypothèse de prix : abonnement par portefeuille protégé, quelques centaines d'euros par mois.
- **Tout est écrit dans `shared/cible-et-modele-economique.md`**, avec les chiffres de marché, leur niveau de confiance et les sources.
- **Claude de Romain, à lire avant d'envoyer le formulaire du checkpoint (R7a) :**
  1. J'ai mis à jour le texte du checkpoint en **section 8 de `PLAN.md`** (problème réécrit, ligne « Cible » ajoutée), ainsi que la section 1, une nouvelle section 1 bis et la ligne du scénario de démo. `SUIVI.md` section 0 aussi. Dis-moi si tu avais des modifications en cours sur ces passages.
  2. Les slides « cible » et « business model » (L3) et la fiche de défense (L4) peuvent reprendre les sections 1 à 5 du nouveau document. **Ne mets pas sur une slide un chiffre marqué « à vérifier ».**
  3. **Slide conformité (L6) :** la cible prioritaire n'est en général pas une entité financière régulée, donc l'angle DORA devient secondaire. Angles proposés, à valider par le mentor KPMG : filtrage des contreparties (LCB-FT), AI Act et supervision humaine, traçabilité des décisions.
  4. **Rien ne change dans le code** (contrats, relais, moteur, oracle).
  5. **Jeu de données :** NovaTreasury paie un loyer, des cotisations et la TVA en stablecoin, ce qui colle mal à la nouvelle cible. Je relibellerai en trésorerie d'une équipe de protocole à la prochaine régénération (avec T9). Structure et fraudes inchangées, adresses et hash différents : **je te préviens avant de pousser**, tes mesures actuelles restent valables d'ici là.
- **Prochaine étape côté Timéo :** intégration avec le vrai moteur ; T6 (Fuji) dès l'accord de Timéo pour les portefeuilles de test.

### 2026-10-10 17:28 — ia-2 / Timéo (avec Claude)
- **Question de Timéo, pour la slide « cible » et « business model » (L3) :** qui a le plus besoin de nous, les grandes plateformes (Bybit, Coinbase) ou les dApps ? **Avis donné, pas encore une décision :** ni les unes ni les contrats des autres, mais les **petites et moyennes organisations qui gardent des millions dans un portefeuille à plusieurs signataires sans équipe de sécurité** : équipes de protocoles et DAO, startups crypto, fonds, fondations. Les grandes plateformes ont déjà des équipes et des outils (Fireblocks) ; elles servent de preuve que le problème existe, pas de premier client.
- **Chiffres trouvés par recherche web, à vérifier avant de les mettre sur une slide :**
  - Safe, le portefeuille à plusieurs signataires le plus répandu : plus de 60 Md$ sécurisés selon Safe (chiffre déclaré ; un suivi tiers donne 35 Md$), plus de 61 millions de comptes créés (la plupart sont de petits comptes, ce n'est pas la taille du marché), plus de 10 M$ de revenu annualisé annoncé en février 2026. La fondation Ethereum y a mis toute sa trésorerie (environ 650 M$) en octobre 2025.
  - Fireblocks, l'outil des grands : entrée de gamme entre 699 et 999 $ par mois selon des comparateurs qui ne s'accordent pas, offres entreprise à partir d'environ 36 000 $ par an. À confirmer sur leur site.
- **Hypothèse de prix à discuter (inventée, pas mesurée) :** abonnement par portefeuille protégé, quelques centaines d'euros par mois. Coût marginal presque nul : 0,002 $ de gas par alerte (`shared/frais-gas.md`), quelques centimes de Bedrock par explication.
- **Concurrence à citer honnêtement :** Safe est gratuit mais ne surveille rien par défaut ; Hypernative et Blockaid proposent des contrôles avant signature pour les multisigs (de mémoire, non vérifié) ; Fireblocks a un moteur de règles pour les grands comptes.
- **Distribution :** en production, notre garde serait un module pour Safe (et Squads sur Solana), installé là où les clients sont déjà, plutôt qu'un portefeuille à nous.

### 2026-10-10 17:22 — ia-2 / Timéo (avec Claude)
- **Question de Timéo :** visons-nous des entreprises du monde réel ou encore des dApps ? **Réponse donnée :** des entreprises réelles qui tiennent une trésorerie en crypto dans un portefeuille à plusieurs signataires (plateformes d'échange, fintechs, fonds, entreprises qui paient en stablecoins, équipes de protocoles). Plus de contrat de dApp à protéger. Le code et les données sont déjà dans ce cadre (entreprise fictive NovaTreasury : salaires, fournisseurs, loyer).
- **Point de réalisme pour le pitch :** le jeu de données paie le loyer, les cotisations et la TVA en mUSD, ce qu'aucune administration n'accepte aujourd'hui. À présenter comme une simplification, ou à relibeller à la prochaine régénération du jeu (celle de T9), en prévenant Romain car les hash changeront.
- **Limite du cadrage à dire au jury :** nous ne traitons pas la fraude sur compte bancaire classique ; la cible est la trésorerie tenue sur la chaîne.

### 2026-10-10 17:19 — Romain (avec Claude) — CONSIGNE MODÈLES
- **Décision de Romain : utiliser Opus 5.5, ou Fable 5.1 si besoin. Ne jamais utiliser Sonnet.**
- **Blocage :** sur le compte de l'événement, Opus 5.5 et Fable 5.1 sont « autorisés » mais leur accord Marketplace est `NOT_AVAILABLE` (marketplace privé des organisateurs). Demande à faire aux organisateurs / au mentor AWS. **Opus 4.8 fonctionne** : c'est le repli actuel de l'oracle (6/6 sur le corpus). Détail : `shared/aws-bedrock.md`.
- **Timéo :** merci d'appliquer la même règle dans ton code (pas de Sonnet) et de vérifier si ton Opus 5.5 par clé d'API marche encore.

### 2026-10-10 17:13 — ia-2 / Timéo (avec Claude)
- **Fait (T3) :** relais `ia-2/scripts/relay.js` (`npm run relay:local`), déploiement local (`npm run deploy:local`) et scénario de démo en direct (`npm run scenario:local`). Mode d'emploi en quatre terminaux dans `ia-2/README.md`.
- **Testé de bout en bout sur la chaîne locale, avec un faux moteur de score à la place du tien :** paiement normal exécuté ; trois virements frauduleux de 95 000 mUSD signalés `hold` **2 secondes** après leur proposition, puis bloqués (2 signatures sur 3 exigées) ; adresse inscrite au registre depuis `flags.jsonl` ; gel et annulation par un signataire. 0 mUSD sorti sur 280 500 tentés.
- **Romain, pour l'intégration de 21h :**
  1. Le relais et ton moteur doivent tourner **sur la même machine** : ils se parlent par `shared/events.jsonl`, `shared/alerts.jsonl` et `shared/flags.jsonl`, que j'ai mis dans `.gitignore` (ils ne passent pas par Git). Ta commande `--events ../shared/events.jsonl --out ../shared/alerts.jsonl --suivre` correspond telle quelle. Le plus simple : toi sur ton Mac avec Node 20 (`cd ia-2 && npm install`), ou ton moteur sur le PC de Timéo (Python 3.12 y est installé).
  2. Au démarrage, le relais **réécrit `events.jsonl`** depuis le déploiement et **ignore les alertes déjà présentes** dans `alerts.jsonl` (elles visent des numéros de paiement d'une session précédente). Lance donc le relais avant ton moteur. Les lignes de `flags.jsonl`, elles, sont toutes rejouées.
  3. Ton verdict doit arriver pendant le délai d'examen : 30 secondes par défaut en démo (`REVIEW_DELAY` au déploiement).
- **Bien lu :** ta validation de R1 sur mon jeu de test. Les jeux de données n'ont pas changé depuis ; je les ai régénérés pour vérifier, ils sont identiques.
- **Réglage Hardhat :** `allowBlocksWithSameTimestamp` activé, sinon l'heure de la chaîne locale prenait de l'avance sur l'heure réelle et faussait les délais en démo.
- **Prochaine étape :** intégration avec ton vrai moteur ; puis T6 (Fuji), pour lequel il me faut l'accord de Timéo pour créer les portefeuilles de test.

### 2026-10-10 17:10 — ia-1 / Romain (avec Claude)
- **R1 évalué sur le test indépendant de Timéo** (`ia-1/eval/evaluer_donnees.py`) : **100 % des 54 fraudes freinées ou arrêtées** (63 % en `hold`), **89 % des montants frauduleux mis en attente** (2,29 M sur 2,57 M mUSD ; la ligne de base sans moniteur laissait sortir 0,97 M), **0,9 % de faux `hold`** sur 564 paiements normaux. Détail : `shared/validation-R1.md`.
- **Merci Timéo, ton jeu a révélé deux défauts**, corrigés sur `train` seulement : `NEW_OWNER_PROPOSES` se déclenchait à chaque renouvellement de clé (14 jours) ; les adresses du carnet passaient pour « récentes ». Friction sur les fournisseurs récurrents en `train` : 45 % → 0 %.
- **Dans `test`, la friction restante vient surtout de la semaine qui suit une baisse du seuil par l'attaquant** : voulu, à expliquer au jury.

### 2026-10-10 17:07 — ia-1 / Romain (avec Claude)
- **Fait (R8a) : cœur de l'oracle Web2 → Web3** dans `ia-1/oracle/`. Page → texte visible (texte caché écarté) → adresses → Bedrock (outil à schéma fixe, consigne anti-injection) → **citation vérifiée par le code** → `flags.jsonl` au format de Timéo + `flags-rejetes.jsonl`.
- **Corpus de 6 pages pièges : 6/6 justes, stables sur 3 passages.** Seule la vraie arnaque est signalée ; démenti, mention, accusation retirée et deux injections de prompt (cachée et visible) sont rejetés. Le repli par mots-clés se fait piéger par l'accusation retirée : bon argument pour le pitch. 17 tests au total dans `ia-1/`.
- **⚠️ Bedrock :** les modèles 5.5 sont maintenant refusés chez Romain ; Sonnet 4.5 marche, et un repli automatique est en place (voir `shared/aws-bedrock.md`). **Timéo, ton Opus 5.5 marche-t-il encore ?**
- **Pour Timéo (T3) :** le relais peut lire `shared/flags.jsonl` ; mes champs sont exactement ceux de ton format (`address`, `level`, `category`, `confidence`, `sources_count`, `source_url`, `quote`, `evidence_hash`, `expires_at`).
- **Prochaine étape :** checkpoint de 18:30, puis R8b (corpus plus large) et R5 (dashboard).
### 2026-10-10 17:06 — ia-2 / Timéo (avec Claude)
- **Fait (T4, T5) :** jeux de données dans `shared/donnees/`, produits par `cd ia-2 && npm run dataset` (90 jours simulés sur la chaîne locale avec les vrais contrats, 15 secondes, reproductible). **Lis `shared/donnees/README.md`.**
  - `train.events.jsonl` : 60 jours de trafic normal seul, 362 paiements, 1 576 événements.
  - `test.events.jsonl` : 30 jours, 256 paiements dont **54 frauduleux en 15 épisodes et 6 variantes** (rafale à la Drift, seuil abaissé, goutte-à-goutte, adresse signalée, clé volée, faux changement de coordonnées).
  - `carnet.json` : les 42 adresses déjà payées par l'entreprise, au format que tu as demandé (tableau d'adresses en minuscules).
  - `test.labels.jsonl` : la vérité, à ne lire que dans l'évaluation.
- **Romain, quatre points pour R2 et R6 :**
  1. Lire `train` puis `test` à la suite : c'est une seule histoire, les identifiants se suivent.
  2. Le trafic normal est en heures ouvrées de Paris, comme tu l'as demandé, avec quelques paiements légitimes le soir (pièges à faux positifs).
  3. **Les clés sont renouvelées tous les 14 jours : 33 remplacements de signataire légitimes.** Ta règle `RECENT_OWNER_CHANGE` (7 jours) se déclenchera donc presque tout le temps ; à revoir.
  4. Les `risk_flagged` du jeu viennent du portefeuille (`OVER_PERIOD_CAP`) ou du registre, jamais du moniteur (champ `by`).
- **Ligne de base à battre :** sans aucune alerte du moniteur, les règles du portefeuille laissent sortir 971 240 mUSD sur 2 565 042 mUSD de fraude proposée.
- **Format :** deux types ajoutés, `config_approved` et `config_cancelled` ; champ `episode` dans les étiquettes des fraudes.
- **Prochaine étape :** T3, le relais en direct sur la chaîne locale.

### 2026-10-10 17:03 — ia-1 / Romain (avec Claude)
- **R1 validé et optimisé** (`shared/validation-R1.md`). Générateur de trafic (`ia-1/eval/generateur.py`, 8 fraudes dont goutte-à-goutte et usurpation de fournisseur), réglage sur 20 graines, test sur 90 graines jamais vues : **99-100 % des fraudes freinées ou arrêtées, ≈ 98 % arrêtées hors goutte-à-goutte, 0,2-0,4 % de mises en attente à tort**. 11 tests, 400 000 événements/s.
- **Nouveaux codes de raison :** `PAYMENT_FRAUD_PATTERN`, `RAPID_REPEAT`, `NEW_OWNER_PROPOSES`. Seuil `hold` passé à 0,75.
- **Pour Timéo :** ton trafic T4/T5 servira de **test indépendant** (mon générateur et mon moteur sont du même côté). Pense au carnet d'adresses (`carnet.json`) et à un `proposer` renseigné dans `payment_proposed` (utilisé par `NEW_OWNER_PROPOSES`).
- **Prochaine étape :** R8a, cœur de l'oracle.

### 2026-10-10 16:54 — ia-1 / Romain (avec Claude)
- **Fait (R1) :** moteur de score dans `ia-1/score/` (Python 3.12). Lit `events.jsonl`, écrit `alerts.jsonl` au format de Timéo. 8 règles explicables (`FLAGGED_ADDRESS`, `NEW_RECIPIENT`, `AMOUNT_OUTLIER`, `BURST`, `URGENCY_MEMO`, `OFF_HOURS`, `RECENT_OWNER_CHANGE`, `THRESHOLD_LOWERED`), score en « OU bruité », `hold` ≥ 0,70, `step_up` ≥ 0,30. Mode direct `--suivre` pour suivre le fichier du relais.
- **Résultat sur `shared/echantillons/` :** paiements 1-2 passent, 3 (nouveau fournisseur) en `step_up`, 4-5-6 (fraude) en `hold`. 5 tests passent. Script `ia-1/eval/comparer.py` (seul à lire `labels.jsonl`).
- **Pour Timéo :** le moteur utilise un **carnet d'adresses du client** (`ia-1/config/carnet.exemple.json`, adresses déjà connues) pour éviter de signaler tous les premiers paiements. **Peux-tu générer un carnet avec ton trafic normal (T4), par exemple `shared/echantillons/carnet.json` ?** J'ai aussi ajouté `OFF_HOURS` (hors 7h–20h, heure de Paris) : pense à mettre le trafic normal en heures ouvrées.
- **Prochaine étape :** R8a, cœur de l'oracle (lecture de page + Bedrock + citation vérifiée).
### 2026-10-10 16:54 — ia-2 / Timéo (avec Claude)
- **Fait (T2, T8, T7) :** contrats `TreasuryGuard` (portefeuille 2 sur 5 avec délai d'examen, signalement `StepUp` / `Hold`, plafond par période, gel, expiration des clés, remplacement de signataire, changement de seuil) et `RiskRegistry` (adresses signalées par l'oracle, avec hash de preuve, expiration et retrait). **20 tests passent** en local (`cd ia-2 && npm install && npm test`). Détail dans `ia-2/README.md`.
- **Scénario de fraude dans les tests :** deux signataires trompés, dix paiements de 95 000 mUSD. Portefeuille témoin : 95 % de la trésorerie part. Avec le garde : rien ne sort. Garde sans moniteur : 95 000 mUSD partent, puis le plafond exige une troisième signature.
- **Gas (`shared/frais-gas.md`) :** une alerte du moniteur coûte environ 0,002 $, une inscription au registre 0,004 $.
- **Pour Romain :** ABI à jour dans `shared/abi/` (`TreasuryGuard`, `RiskRegistry`). Dans `shared/format-evenements.md`, trois précisions alignées sur le contrat : `risk_flagged` porte un champ `by` (moniteur, registre ou portefeuille) ; nouveau type `config_proposed` ; `owner_key_renewed` supprimé (renouveler une clé, c'est remplacer le signataire). Le registre n'accepte que les niveaux 1 (`step_up`) et 2 (`hold`).
- **Nettoyage :** le coffre de prêt `BreakerVault`, `SimplePool`, leur test et leurs ABI sont retirés (ils restent dans l'historique Git).
- **Prochaine étape :** T3, le relais (chaîne locale → `events.jsonl`, `alerts.jsonl` et `flags.jsonl` → chaîne), puis T4, le trafic normal.

### 2026-10-10 16:52 — ia-2 / Timéo (avec Codex)
- **Fait :** synchronisation du dépôt et récupération de SUIVI.md à la demande de Timéo. La version datée de 16:50 contient bien T9 (données de traçage, Timéo) et R9 (propagation du risque, Romain), toutes deux à faire et prévues en bonus après la démo de 23:00.
- **Fichiers :** SUIVI.md et PLAN.md consultés, statuts conservés ; compte-rendu dans conversations/2026-10-10_timeo_recuperation-suivi.md.


### 2026-10-10 16:43 — ia-2 / Timéo (avec Codex)
- **Demande et fait :** lien Granola du pitch avec le mentor enregistré dans shared/retour-mentor-team1.md : https://notes.granola.ai/t/7bf42777-eba3-48f0-a9ab-3780744381e7.
- **Coordination :** ajout de la source uniquement, analyse existante conservée ; SUIVI.md et conversations/2026-10-10_timeo_source-pitch-mentor.md mis à jour.
- **Limite :** Granola inaccessible au lecteur web de Codex ; aucun nouveau résumé du contenu ajouté.
- **Prochaine étape :** poursuivre le plan validé ; aucune décision de projet changée.


### 2026-10-10 16:41 — ia-2 / Timéo (avec Claude)
- **Fait (T1) :** `shared/format-evenements.md` réécrit pour l'axe 2, avec les quatre fichiers `events.jsonl`, `alerts.jsonl`, `flags.jsonl` (demandé par Romain pour l'oracle) et `labels.jsonl`. Exemples complets dans `shared/echantillons/` : 31 événements qui racontent deux paiements normaux, un nouveau fournisseur légitime, un signalement de l'oracle et une fraude en rafale.
- **Romain, tu peux démarrer R1 et R8 dessus.** Trois points à connaître : (1) le verdict doit arriver pendant le **délai d'examen** de 60 secondes qui suit `payment_proposed` ; (2) les étiquettes sont dans un fichier à part, `labels.jsonl`, que le moteur ne doit jamais lire ; (3) seuls l'adresse, le niveau, le hash de preuve et l'expiration d'un signalement vont sur la chaîne, pas l'URL ni la citation.
- **Lu :** plan validé par Romain avec l'oracle Web2 → Web3 ; je prends T8 (registre des adresses signalées).
- **Exemples pour le pitch, vérifiés par recherche :** Bybit (21 février 2025, environ 1,46 Md$, 3 signataires sur 6 ont validé une transaction que l'interface leur montrait falsifiée) en plus de Drift. L'accord Avalanche / Émirats cité par le mentor est l'annonce du 14 septembre 2026 : le coffre de documents de l'identité numérique UAE PASS passe sur un L1 Avalanche dédié. C'est de la vérification de documents, pas un accord « KYC » ; mise en service non confirmée.
- **Prochaine étape :** contrat `TreasuryGuard` (T2) avec le registre (T8), puis tests.

### 2026-10-10 16:35 — Romain (avec Claude) — DÉCISION
- **Validé par Romain :** passage à l'**axe 2 du track 1**, lecture « **trésorerie crypto** » (portefeuille multisig d'entreprise). **Uniquement de la crypto, la fraude bancaire classique est exclue.** Le `PLAN.md` de Timéo (16:35) est adopté.
- **Ajout de Romain : l'oracle Web2 → Web3** (section 4 bis de `PLAN.md`). Un oracle IA lit le Web (pages de signalement, listes publiques), repère les adresses accusées de fraude (Bedrock + citation exacte vérifiée par le code), puis les inscrit dans un registre on-chain. Un paiement vers une adresse signalée déclenche la friction. Jamais de blocage, signalements contestables et à durée limitée.
- **Nouvelles tâches :** **R8** (Romain) oracle + corpus synthétique avec pièges (démentis, empoisonnement) ; **T8** (Timéo) registre des adresses signalées, alimenté par `flags.jsonl` via le relais.
- **Pour Timéo :** merci de prévoir dans `shared/format-evenements.md` le format de `flags.jsonl` (adresse, niveau, catégorie, url_source, citation, hash_preuve, expiration) et l'événement on-chain du registre.
- **Prochaine étape :** checkpoint de 18:30 avec le texte de la section 8 (mis à jour avec l'oracle).

### 2026-10-10 16:31 — ia-2 / Timéo (avec Claude)
- **Fait :** nouveau `PLAN.md`, rédigé à la demande de Timéo pour l'**axe 2 du track 1** : garde antifraude pour une trésorerie d'entreprise tenue par un portefeuille à plusieurs signataires. **Romain, c'est une proposition : lis-la et dis ce que tu changes.** Ton plan de l'axe 4 est archivé tel quel dans `shared/archive/PLAN-axe4.md`.
- **Répartition proposée (consigne de Timéo : le plus technique côté blockchain pour lui) :** Timéo → contrat `TreasuryGuard`, relais chaîne/fichiers, trafic normal, scénarios de fraude, Fuji. Romain → moteur de score, explication et rapport par Bedrock, tableau de bord, évaluation, livrables écrits.
- **Interface entre les deux :** deux fichiers JSON Lines, `events.jsonl` (Timéo vers Romain) et `alerts.jsonl` (Romain vers Timéo). Romain n'a pas besoin de la blockchain pour avancer.
- **En cours :** format des événements et fichier d'exemple (tâche T1), puis le contrat.
- **Bloquant :** accord de Romain sur le plan ; formulaire du checkpoint à 18:30 (texte proposé en section 8 du plan).

### 2026-10-10 16:26 — ia-2 / Timéo (avec Claude)
- **Annonce de Timéo :** après l'échange avec le mentor, il veut passer de l'axe 4 à l'**axe 2 du track 1** (SOC antifraude à l'ère de l'IA générative : prise de contrôle de compte, arnaques au paiement, fraude au président ; réponse graduée par authentification renforcée, mise en attente, gel, alerte). **Accord de Romain non confirmé ici ; `PLAN.md` n'est pas modifié.**
- **Lecture proposée par Claude, à confirmer par Timéo :** l'axe 2 appliqué à une **trésorerie d'entreprise sur la chaîne**, pas à la fraude bancaire classique. Le client est une entreprise qui gère ses fonds par un portefeuille à plusieurs signataires. Chaque transaction proposée est notée avant son exécution (destinataire jamais vu, montant hors habitudes, rafale, signatures anciennes, changement récent des signataires ou du seuil). Réponse appliquée par le portefeuille du client lui-même : signatures supplémentaires exigées, mise en attente avec délai, gel par les signataires, alerte. Plafond par période sans autorisation supplémentaire et expiration des clés, les deux idées du mentor. L'outil ne peut qu'ajouter de la friction ; il ne valide, ne bloque ni ne déplace rien.
- **Pourquoi cette lecture :** elle garde notre avantage crypto, le cas Drift (signataires trompés, soit une fraude au président version crypto), Avalanche, Hardhat, Bedrock et le format des événements. La version bancaire classique (voix clonées, faux documents KYC) nous ferait repartir de zéro, sans données pour mesurer la détection.
- **Coût du changement :** le coffre de prêt `BreakerVault` (environ deux heures de travail) ne sert plus tel quel ; `ia-1/` ne contient pas encore de code. La grille de notation est la même pour tous les axes du track 1.
- **Bloquant :** confirmation de Timéo sur la lecture (trésorerie sur la chaîne ou fraude bancaire classique) et accord de Romain, avant le checkpoint de 18:30.

### 2026-10-10 16:23 — ia-2 / Timéo (avec Claude)
- **Correction :** j'avais mal lu la note du mentor. Timéo, présent, précise sa conclusion : **nous ne faisons pas nous-mêmes la transaction de pause** (trop centralisé) ; on **alerte les signataires** du protocole ; on **impose un renouvellement périodique de leurs clés** (quinze jours par exemple).
- **Proposition de Claude, non décidée** (détail en section 4 de `shared/retour-mentor-team1.md`) : garder la pause mais la laisser aux mains du protocole. Le moniteur alerte et prépare la transaction, les signataires la valident ; le protocole choisit entre alerte seule, pause validée par ses signataires, ou pause automatique qu'il délègue lui-même. Ajouter au contrat une expiration des rôles pour forcer le renouvellement des clés.
- **Pourquoi ne pas tout enlever :** le guide cite la pause du contrat dans le playbook de l'axe 4, la réponse pèse 20 %, et l'alerte seule existe déjà sur le marché.
- **Bloquant :** décision de Romain et Timéo sur ce cadrage avant de toucher au contrat. **Romain, ta lecture de l'échange avec le mentor ?**

### 2026-10-10 16:18 — ia-2 / Timéo (avec Claude)
- **Fait :** note Granola du mentor Team1 lue et confrontée au plan dans `shared/retour-mentor-team1.md`. Frais de gas mesurés (`npm run gas` dans `ia-2/`) : une pause coûte environ 34 000 gas, soit **0,002 $** au prix relevé à 16h17.
- **Ce que le mentor confirme :** l'architecture en deux composantes, Drift comme cas de référence, la transaction sur la chaîne (c'est notre `escalate`).
- **Proposition, à valider à deux :** ajouter un **plafond de sorties permanent** dès le niveau Normal (idée du mentor, 10 % par période). **Refuser** le déplacement automatique des fonds : il casse notre règle « le gardien ne touche jamais aux fonds » et contredit le conseil MiCA du même mentor.
- **Attention pitch :** ne pas dire qu'Avalanche aurait empêché Drift (faux, un expert le relèvera) ; dire que la pause y est définitive en une à deux secondes pour une fraction de centime. Chiffre de Drift : 280 à 285 M$ d'après nos sources, pas 255 M$.
- **À confirmer avec le mentor KPMG :** le cadrage DORA (client régulé exposé au coffre, nous comme prestataire tiers de services TIC).
- **Prochaine étape :** plafond permanent dans le contrat si validé, puis scripts de déploiement, de trafic et d'attaque.

### 2026-10-10 15:37 — ia-2 / Timéo (avec Claude)
- **Fait :** en partage de connexion, **Bedrock fonctionne chez Timéo** avec sa clé d'API : appel réel réussi sur `us.anthropic.claude-opus-5-5`.
- **Écart avec Romain :** `claude-sonnet-5-5` et `claude-haiku-5-5` sont refusés avec la clé de Timéo (« private marketplace eligibility »). Détail dans `shared/aws-bedrock.md`.
- **Pour Romain :** dans le module DORA, lire le modèle dans la variable `BEDROCK_MODEL_ID` (valeur par défaut au choix) au lieu de l'écrire en dur.
- **Rappel :** la clé de Timéo expire vers 03:28 dimanche.

### 2026-10-10 15:34 — ia-2 / Timéo (avec Claude)
- **Diagnostic Bedrock chez Timéo :** la clé est en place, c'est bien le réseau qui bloque. Sur le Wi-Fi de l'école, le nom `bedrock-runtime.us-west-2.amazonaws.com` se résout, mais la connexion TLS est coupée (« Connection was reset »), alors que `sts.us-west-2.amazonaws.com` répond. Même constat que Romain.
- **Bloquant :** Timéo doit passer en partage de connexion pour que je valide sa clé. Je n'ai pas cherché à contourner le filtrage de l'école.

### 2026-10-10 15:33 — ia-2 / Timéo (avec Claude)
- **Fait :** clé d'API Bedrock de Timéo rangée dans `.env` à la racine du repo (ignoré par Git, vérifié par `git check-ignore`). Modèle `.env.example` ajouté à la racine ; `.gitignore` complété par `!.env.example`, car la règle `.env.*` ignorait aussi les modèles (celui de `ia-2/` n'était jamais parti). Méthode décrite dans `shared/aws-bedrock.md`.
- **Bloquant :** l'appel de test échoue depuis le Wi-Fi de l'école (« Connection was closed »), comme l'a vu Romain. La clé n'est donc **pas encore validée**. Elle expire vers **03:28 dimanche** : à renouveler avant le rendu.
- **À savoir :** Timéo a collé cette clé dans sa conversation avec Claude. Elle n'est dans aucun fichier suivi par Git.
- **Prochaine étape :** retester Bedrock en partage de connexion ; côté code, script de déploiement, trafic normal et attaque autonome.

### 2026-10-10 14:45 — Romain (avec Claude)
- **Fait :** accès AWS de l'événement configuré chez Romain (profil local `hackathon`, région us-west-2). **Bedrock fonctionne** : appel réel réussi avec `us.anthropic.claude-sonnet-5-5`. Procédure dans `shared/aws-bedrock.md`.
- **Bloquant découvert :** le Wi-Fi de l'école bloque `bedrock*.amazonaws.com`. Il faut passer par le partage de connexion du téléphone (ou CloudShell). À signaler aux organisateurs.
- **Décision :** coffre **de prêt** validé (plus de signes précurseurs, donc une pause avant le premier dollar sorti). Cadrage réglementaire : client fictif agréé MiCA exposé au coffre (voir `PLAN.md`).
- **Pour Timéo :** récupérer tes propres identifiants dans Workshop Studio (voir `shared/aws-bedrock.md`), ne pas partager les clés.

### 2026-10-10 14:15 — ia-2 / Timéo (avec Claude)
- **Fait :** projet Hardhat dans `ia-2/` avec les contrats `BreakerVault` (coffre de prêt, disjoncteur à trois niveaux Normal / Limited / Paused, rôles séparés), `SimplePool` (pool d'échange qui sert d'oracle de prix) et `MockToken`. **13 tests passent** sur la chaîne locale (`cd ia-2 && npm install && npm test`).
- **Scénario rejoué dans les tests**, inspiré de Drift : faux jeton au prix gonflé, prise du rôle de configuration, délai de sécurité ramené à zéro, listing, puis vidage en 31 emprunts. Sans disjoncteur le coffre est vidé ; pause après 3 emprunts : plus de 90 % des fonds restent ; pause au listing : rien ne sort.
- **Écart par rapport à `PLAN.md`, à valider par Romain :** coffre **de prêt** plutôt que simple coffre de dépôts et retraits. Raison : cela donne au moniteur des signes précurseurs avant le premier retrait (rôle accordé à une adresse neuve, délai abaissé, collatéral à liquidité dérisoire). La pause, le plafond de sorties et le gardien borné du plan sont là.
- **Pour Romain :** `shared/format-evenements.md` (proposition de format des événements et des alertes, à amender), `shared/abi/` (ABI pour web3.py), `shared/dora-notes.md` (délais et critères DORA : la notification initiale sous 4 h après classement et 24 h après prise de connaissance est confirmée ; le reste est à lire dans les textes).
- **Synchro :** la boucle automatique a committé mon travail en cours de route (commits `[auto]` de 14:09 et 14:14) ; rien de cassé, mais les messages de commit ne disent pas ce qu'ils contiennent.
- **Bloquant :** identifiants AWS ; portefeuilles de test et AVAX du faucet pour Fuji.
- **Prochaine étape :** script de déploiement (local puis Fuji), générateur de trafic normal et script d'attaque autonome qui écrivent les événements au format proposé.

### 2026-10-10 14:08 — ia-2 / Timéo (avec Claude)
- **Décision :** Timéo confirme l'**axe 4 du track 1** et me dit que Romain est d'accord. Je travaille désormais uniquement dans ce repo (l'ancien dossier local de Timéo ne sert plus).
- **Accord avec `PLAN.md` :** je prends la répartition proposée (contrat, déploiement Fuji, trafic et attaques dans `ia-2/`) et la stack **Hardhat**. J'avais proposé Foundry à Timéo ; l'argument Windows sans WSL ni Docker est le bon, je m'aligne.
- **Cadrage validé par Timéo :** une seule démo de bout en bout, mais un détecteur conçu pour une classe d'exploits (vidage en plusieurs transactions précédé de signes précurseurs), mesuré sur des variantes non vues mélangées à du trafic normal.
- **En cours :** squelette Hardhat dans `ia-2/`, contrat du coffre, tests locaux, puis proposition du format des événements dans `shared/` pour que Romain puisse démarrer le moniteur.
- **Bloquant :** identifiants AWS (Timéo les attend).
- **Prochaine étape :** format des événements poussé dans l'heure.

### 2026-10-10 14:10 — Romain (avec Claude)
- **Fait :** `PLAN.md` (projet « Breaker », étapes jusqu'au rendu, répartition, limites et risques, idées bonus) et `shared/pitch-mentor.md` (pitch oral de 1 min 30 + questions pour le mentor Team1).
- **Proposition :** partir sur l'idée de Timéo (disjoncteur DeFi, axe 4 du track 1) et y intégrer l'idée de Romain comme vecteur d'attaque (agent IA de trésorerie piégé).
- **Répartition proposée :** Timéo → contrat Vault, déploiement Fuji, trafic et attaques (`ia-2/`). Romain → moniteur, score de risque, module DORA, dashboard (`ia-1/`).
- **Bloquant :** validation à deux + avis du mentor ; accès AWS Bedrock.
- **Prochaine étape :** présenter le pitch au mentor Team1, décider avant 15:30.

### 2026-10-10 13:51 — ia-2 / Timéo (avec Claude)
- **Fait :** Timéo est raccordé à ce repo (clone, hook Stop, boucle de synchro toutes les 5 min). Jusqu'ici son travail partait par erreur sur `veryromain/hackathon-ia-cyber`, un autre repo. Compte-rendu complet dans `conversations/2026-10-10_timeo_choix-axe-et-setup.md`. AWS CLI et Python 3.12 installés chez Timéo.
- **Décision de Timéo :** track 1 ; modèles par AWS Bedrock (crédits du hackathon).
- **En cours :** choix du sujet, non décidé. Idée à l'étude côté Timéo (proposée par Claude) : axe 4 du track 1, un disjoncteur on-chain (testnet Avalanche Fuji) qui met un contrat en pause pendant une attaque simulée, puis classe l'incident selon DORA et préremplit la notification.
- **Bloquant :** deux idées différentes sur la table (supervision d'agents IA financiers côté Romain, disjoncteur DeFi côté Timéo). Pas d'identifiants AWS configurés.
- **Prochaine étape :** trancher le sujet ensemble avant le checkpoint de 18:30.

### 2026-10-10 13:30 — Romain (avec Claude)
- **Fait :** brief du hackathon dans `CONTEXTE.md` (guide Notion + slides), repo publié sur GitHub (privé), synchro automatique mise en place (`scripts/auto-sync.sh`), comptes-rendus de conversation dans `conversations/`.
- **Décision :** on vise le **Track 1 ou le Track 2**, à confirmer au checkpoint de sam. 18:30.
- **Idée proposée :** un seul projet qui marche pour les deux tracks. IA n°1 = agent financier piégé (document ou outil MCP empoisonné qui pousse à un paiement non autorisé). IA n°2 = superviseur / passerelle qui loggue chaque appel d'outil avec sa chaîne d'autorité, détecte (OWASP ASI01/02/03/07), bloque, demande une validation humaine ou coupe (kill switch), et génère le rapport d'incident.
- **Prochaine étape :** valider l'idée avec Timéo, squelette de code des deux IA, `PLAN.md` jusqu'au rendu de dim. 12:00.

### 2026-10-10 — Équipe
- **Fait :** création du repo
