# Argumentaire « sécurité du contrat » pour le pitch : solide parce qu'il ne promet rien de plus que ce qu'on peut prouver

> Romain (avec Claude), 11/10 vers 01:25. Principe : un argumentaire est incontestable quand chaque phrase est **vérifiable par le jury en une commande** et quand on nomme soi-même ce qu'on n'a pas fait. Toute exagération serait relevée par un juré qui connaît le sujet ; l'honnêteté précise, non.

## 1. Les 30 secondes à dire (dans la section « ce qu'on ne fait pas encore »)

« Notre contrat n'a pas encore été audité par un tiers. Voici ce que nous avons fait à la place, et ce que ça vaut.
Un, **l'architecture borne le risque** : le contrat ne garde jamais de pouvoir sur les fonds. Aucune fonction, pas même la nôtre, ne peut transférer un euro sans les signatures humaines du client. Le pire bug possible est un faux ralentissement, pas une perte.
Deux, **l'analyse statique** : zéro détection de sévérité haute ou moyenne, et chaque remarque informative examinée et documentée.
Trois, **le fuzzing** : 7 000 appels aléatoires par huit types d'acteurs, intrus compris, sans qu'aucune des cinq promesses du contrat ne soit violée.
Quatre, **le code et les tests sont publics**, les commandes sont dans le dépôt : vous pouvez tout rejouer.
Cinq, **l'audit externe est budgété avant le premier client payant**, et notre surface est petite, parce que nous ne gardons rien. »

## 2. Pourquoi c'est inattaquable : chaque mot est vérifiable

| Ce qu'on dit | Comment le jury peut le vérifier | Ce qu'on NE dit PAS |
|---|---|---|
| « Aucune fonction ne peut transférer sans signatures humaines » | Le seul `safeTransfer` du contrat est dans `execute`, qui exige `validApprovals ≥ requiredApprovals` ; le moniteur n'a que `flagRisk` ; l'oracle n'a que le registre. Lecture du code : 5 minutes | « Notre contrat est sûr » |
| « Zéro détection haute ou moyenne » | `slither .` dans `ia-2`, résultat et analyse ligne par ligne dans `shared/audit-contrat.md` | « Slither prouve l'absence de bug » (il ne trouve que des motifs connus) |
| « 7 000 appels aléatoires, 0 invariant violé » | `FUZZ_SEQ=300 npx hardhat test ../ia-1/integration/invariants.test.js` ; graines fixées, reproductible ; les 5 invariants sont écrits en clair en tête du fichier | « Le contrat est exhaustivement testé » |
| « 50 tests unitaires » | `npx hardhat test` | — |
| « Code public » | le dépôt sera public au rendu (livrable L8), licence MIT en tête des fichiers | « Audité par la communauté » |
| « Audit externe avant le premier client payant » | ligne du plan dans `shared/audit-contrat.md`, intro aux auditeurs demandée aux mentors | « Audit en cours » |

## 3. Les objections qu'un juré fera, et la réponse

- **« Slither ne trouve que des motifs connus. »** Exact, c'est pour ça qu'on a ajouté les invariants et qu'on prévoit l'audit externe. L'analyse statique sert à écarter les erreurs classiques (réentrance, accès), pas à prouver la logique.
- **« Votre fuzzing, c'est vous qui l'avez écrit. »** Oui. Les invariants sont les cinq promesses commerciales du produit, écrites en clair, et le générateur est à graine fixe : n'importe qui peut relancer avec dix fois plus de séquences. Nous ne cachons pas que 300 séquences est un début ; 3 000 avant l'audit.
- **« Vous n'êtes pas dépositaires, et alors ? »** Et alors le pire scénario change de nature : un bug chez un dépositaire perd l'argent ; un bug chez nous retarde un paiement, et l'unanimité des signataires lève même ce retard. C'est une différence de catégorie de risque, vérifiable dans `execute`.
- **« Et si un attaquant retire votre garde ? »** Retirer ou affaiblir le garde passe par la procédure d'un paiement : proposition, signatures renforcées, délai. Jamais en une transaction.
- **« Pourquoi pas d'audit avant le hackathon ? »** Parce qu'un audit se fait sur un contrat stable, et que le nôtre a évolué jusqu'à ce soir (clé d'identité). L'auditer maintenant aurait été payer pour rien.
- **« Quel coût, quel délai ? »** Surface d'environ 500 lignes, sans garde de fonds : audit court. Estimation de l'ordre de 10 à 25 k$ **(à confirmer avec un cabinet, ne pas affirmer un chiffre précis au jury si on n'a pas de devis)** ; introduction demandée aux mentors.

## 4. Ce qu'il ne faut jamais dire
- « Audité » sans « par nous-mêmes ».
- « Aucune vulnérabilité » : dire « aucune détectée par ces méthodes ».
- « Impossible de perdre des fonds » : dire « aucune fonction ne peut transférer sans les signatures humaines ; nous n'avons trouvé aucun chemin qui contourne cette règle ».
- Un chiffre d'audit externe comme si on avait un devis.

## 5. Où le mettre dans le deck
Une seule slide, dans la partie « limites et suite », avec les quatre chiffres (0 détection grave · 50 tests · 7 000 appels aléatoires · 0 invariant violé) et la phrase « le pire bug possible est un faux ralentissement ». Pas en ouverture : la sécurité du contrat n'est pas notre promesse principale, c'est une condition.
