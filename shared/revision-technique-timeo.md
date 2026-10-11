# Révision technique pour les questions du jury (Timéo)

> Préparé avec Claude le 11 octobre à 12 h 15, pour le pitch de 13 h. Chaque réponse tient en deux phrases et repose sur un fait vérifié dans le dépôt. Les réponses business sont dans `shared/pitch-final.md` (Romain). Vocabulaire : « signature en plus », « mise en attente », « Cosignataire » ; jamais « bloqué » ni « arrêté » pour une fraude mise en attente.

## Les dix chiffres à savoir par cœur

| Chiffre | Ce qu'il mesure |
|---|---|
| 91 % | des montants frauduleux mis en attente sur le jeu final (1,12 M sur 1,23 M de mUSD) |
| 95 % | des fraudes freinées : 38 sur 40, dont 31 mises en attente et 7 en signature en plus |
| 5,1 % | des paiements légitimes mis en attente : 12 sur 234, tous de gros premiers paiements à un nouveau bénéficiaire |
| 0 mUSD | sorti sur 280 500 tentés, démonstration sur Avalanche Fuji |
| 5 à 6 s | pour inscrire le signalement sur Fuji ; 7 à 10 s avec l'explication rédigée |
| 30 s et 180 s | délai d'examen et mise en attente de la démo (valeurs de démonstration) |
| 0,002 $ | de gas par alerte inscrite ; environ 1 centime avec l'explication |
| 2 jours | de probation pour une clé neuve ; 15 jours de validité d'une clé |
| 51 et 80 | tests du contrat et tests Python, tous passants |
| 2 min | pour que l'agent cherche un destinataire sur le Web et rende son avis final |

## 1. Comment ça marche

**Décrivez l'architecture en une phrase.**
Un contrat sur Avalanche tient la trésorerie et applique les freins ; un moteur hors chaîne note chaque paiement proposé et inscrit son verdict sur la chaîne ; un oracle lit le Web et inscrit les adresses signalées. Les signataires voient le tout dans un tableau de bord et gardent la décision.

**Que se passe-t-il entre la proposition et l'exécution ?**
Tout paiement attend un délai d'examen. Pendant ce délai le moteur le note ; si le score dépasse un seuil, le contrat exige une signature en plus, et au-dessus d'un second seuil il ajoute une mise en attente.

**Quelle différence entre signature en plus et mise en attente ?**
La signature en plus ajoute une personne ; la mise en attente ajoute du temps. Le temps est la seule protection quand l'attaquant tient déjà assez de clés.

**Que peut faire votre garde sur les fonds ?**
Une seule chose : relever le niveau de vérification d'un paiement en attente. Il ne peut ni proposer, ni approuver, ni exécuter, ni annuler, et il ne peut jamais baisser un niveau.

**Et si votre service tombe en panne ?**
Les paiements suivent les règles ordinaires du coffre. Deux protections restent actives parce qu'elles sont dans le contrat : le plafond par période et le registre des adresses signalées.

**Et si vous vous trompez ?**
Un paiement légitime demande une signature de plus ou attend un délai. L'unanimité des signataires ramène un paiement mis en attente au délai court : rien n'est figé pour toujours.

## 2. La détection

**Comment calculez-vous le score ?**
Seize règles lisibles donnent chacune un poids entre 0 et 1, combinés pour qu'aucune ne suffise seule sauf les plus graves. S'y ajoute un modèle d'anomalie entraîné sur le trafic normal du client. Signature en plus à partir de 0,30, mise en attente à partir de 0,75.

**Quelles règles, par exemple ?**
Bénéficiaire jamais payé, montant hors norme pour ce client, rafale de paiements, libellé pressant ou secret, signataire tout juste ajouté qui propose, adresse signalée, adresse qui imite celle d'un fournisseur.

**Où est l'IA ?**
À quatre endroits : le modèle d'anomalie, l'oracle qui lit les pages Web, l'explication rédigée pour le signataire, et l'agent qui instruit un dossier par paiement. Les règles restent lisibles, donc aucune décision n'est une boîte noire.

**Quel modèle de langage ?**
Claude Opus 4.8 par Amazon Bedrock. Il rédige et il juge, mais il ne peut que durcir un avis calculé sans lui, jamais lever une alerte.

**Comment avez-vous mesuré ?**
Le moteur est réglé sur 60 jours de trafic normal, puis évalué une seule fois sur un jeu final de 274 paiements dont 40 frauduleux, aux formes qu'il n'avait jamais vues. Nous n'avons pas retouché les seuils après cette mesure.

**Ce sont des données synthétiques.**
Oui, et c'est écrit sur chaque support. Ces chiffres ne garantissent rien sur un trafic réel ; l'essai gratuit de 30 jours sert à les remplacer par des vrais.

**5,1 % de fausses mises en attente, c'est beaucoup.**
Les douze cas sont tous de gros premiers paiements à un nouveau bénéficiaire ; il n'y en a aucun sur les prestataires habituels. Et l'erreur coûte une signature et un délai, pas le paiement.

**Quelles fraudes passent ?**
Deux sur quarante : les deux premiers petits paiements d'une mise en confiance, que rien ne distingue d'un nouveau fournisseur. Le gros paiement qui suit, lui, est mis en attente.

## 3. L'oracle et le Web

**Comment l'oracle lit-il le Web ?**
Il cherche l'adresse, collecte les pages avec Apify, et un modèle les lit. Une accusation n'est retenue que si la citation est retrouvée mot pour mot dans la page.

**Et si quelqu'un publie une fausse accusation pour nuire à un concurrent ?**
Une source inconnue ne suffit pas : il faut une source de confiance, ou plusieurs sources indépendantes. Les signalements expirent, peuvent être contestés, et leur preuve est inscrite sur la chaîne.

**Et une page piégée qui donne des instructions au modèle ?**
Le texte caché est retiré avant lecture, et le texte du Web est traité comme une donnée. Même trompé, le modèle ne peut que durcir un avis : une page ne peut pas le convaincre de signer.

**L'avez-vous fait tourner sur le vrai Web ?**
Oui : sur une adresse du groupe Lazarus, il a trouvé la fiche officielle de l'OFAC et une seconde source, puis le coffre a refusé le paiement malgré trois signatures. Limite : ce sont des listes de sanctions publiques, pas encore un forum.

**Deux minutes, c'est plus long que votre délai d'examen.**
C'est vrai. L'agent rend d'abord un avis en quelques secondes avec ce qu'il sait, puis le durcit quand le Web a répondu ; en production la recherche tourne en avance sur les destinataires connus.

## 4. L'agent et le mode Cosignataire

**Que fait l'agent ?**
Pour chaque paiement il simule le transfert sur le nœud, lit l'historique du destinataire sur la chaîne, consulte le Web, puis rend un avis : laisser, freiner ou refuser. Chaque décision est conservée avec les faits sur lesquels elle repose.

**Que veut dire « simuler » ?**
Il rejoue le transfert sans l'envoyer, pour savoir s'il réussirait et quelle part de la trésorerie partirait. Un paiement qui sort plus de la moitié de la trésorerie est refusé, même vers un fournisseur connu.

**En mode Cosignataire, l'agent peut-il empêcher un paiement pour toujours ?**
Non. Il occupe un siège de signataire et peut refuser de signer ; son refus met le paiement en attente. Les humains peuvent passer outre par une procédure renforcée après un délai, et un test le prouve.

**Et si l'agent ne peut pas vérifier ?**
Il ne signe pas. Si la simulation ou la lecture du Web échoue, il demande une validation humaine au lieu de cosigner.

**Pourquoi ne pas refuser d'office ?**
Parce qu'un paiement légitime refusé est un dommage dont nous serions la cause, alors qu'un retard ne l'est pas. Et un garde défaillant qui fige un coffre est précisément le risque contre lequel la documentation de Safe met en garde.

## 5. Les clés et les personnes

**Et si une clé est volée ?**
Son propriétaire la révoque seul, en une transaction, avec une seconde clé gardée hors ligne. La nouvelle clé passe deux jours en probation : elle ne compte ni pour les paiements signalés, ni pour dégeler.

**Et si l'attaquant tient déjà assez de clés ?**
Alors la signature en plus ne suffit pas et seule la mise en attente protège, en donnant aux autres signataires le temps de geler. C'est notre limite connue : en rejouant la cadence de Drift avec une clé de plus que le seuil, des fonds sont sortis en essai local.

**Vous avez rejoué Drift ?**
Nous avons rejoué sa cadence, 31 retraits en 12 minutes, sur notre coffre de démonstration avec le seuil de clés volées : rien n'est sorti. Ce n'est pas le rejeu de l'attaque réelle, qui visait les droits d'administration d'un protocole sur Solana.

**Et si un signataire est forcé de signer sous la menace ?**
Nous avons une réponse, démontrée sur Fuji, que nous ne publions pas. À l'oral seulement : une seconde clé signe en apparence normalement, le paiement ne part pas, et les autres signataires sont prévenus hors chaîne.

**Qui peut geler, qui peut dégeler ?**
Un seul signataire suffit pour geler. Pour dégeler il faut le quorum renforcé, trois signataires sur cinq dans la démo, et les clés en probation ne comptent pas.

## 6. La sécurité du code

**Votre contrat est-il audité ?**
Pas par un tiers. Nous avons fait une analyse statique sans détection grave, 51 tests et environ 7 000 appels aléatoires sans invariant violé ; l'audit externe est prévu avant le premier client payant.

**Un bug de votre contrat peut-il faire perdre des fonds ?**
Oui, c'est possible, et nous ne prétendons pas le contraire. C'est pourquoi le prototype ne tient que des jetons de test et qu'aucun client ne paie avant l'audit.

**Avez-vous des secrets dans le dépôt ?**
Non, et c'est vérifié par un script sur les fichiers et sur tout l'historique, sur nos deux postes. Les clés sont dans des fichiers ignorés par Git.

**Des données personnelles ?**
Aucune : les jeux de données sont synthétiques, et les pages Web collectées restent hors du dépôt.

## 7. Les limites, à dire sans attendre la question

- **Le coffre de la démonstration tient lieu du Safe du client.** Le greffon sur Safe n'est pas écrit ; l'estimation de six à huit semaines n'est pas vérifiée.
- **Une seule chaîne :** Avalanche, sur le réseau de test Fuji. Le code est du Solidity standard, donc portable, mais rien d'autre n'est déployé.
- **Les délais de 30 et 180 secondes sont ceux de la démo.** En production on parle de minutes pour l'examen et d'heures pour la mise en attente.
- **Le signal « adresse sans passé sur la chaîne » n'est pas mesuré** : nos adresses de test n'ont pas d'historique.
- **Le poids d'une rafale ne grandit pas avec sa taille.** C'est la cause de la limite sur Drift, et la première correction prévue.

## Pièges

- « Audité » : toujours ajouter « par nous-mêmes, pas par un tiers ».
- « L'IA bloque » : l'agent refuse de signer, le paiement est mis en attente, les humains décident.
- « Nous avons rejoué Drift » : dire « la cadence de Drift ».
- « Impossible de perdre des fonds » : ne jamais le dire.
- Si tu ne sais pas : « Je n'ai pas ce chiffre ; voici ce que nous avons mesuré », puis un des dix chiffres.
