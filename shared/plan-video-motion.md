# Plan de la vidéo de démonstration en motion design (livrable L1)

> Proposé par Timéo (avec Claude), 11 octobre, 8 h 50. La vidéo se lance à la slide 5 du deck (`shared/pitch/breaker-deck.html`, « Sur Avalanche Fuji : 280 500 tentés, zéro sorti »). Durée visée : 2 min 30. Chaque chiffre vient d'une démonstration déjà jouée et notée dans `JOURNAL.md`.

## Les sept plans

| # | Temps | À l'écran | Phrase dite | Source des images |
|---|---|---|---|---|
| 1 | 0:00 – 0:15 | Texte animé : « Bybit, 1,46 Md$. Drift, 280 M$. Les clés étaient valides. » Puis le logo. | « Dans les deux cas, personne n'a volé de clé au moment du paiement. Des signataires ont validé. » | Motion pur, reprise de la section « Le problème » du site |
| 2 | 0:15 – 0:35 | Tableau de bord : paiement de 3 150 mUSD au prestataire connu, 2 signatures sur 2, exécuté. | « Un paiement habituel passe sans friction, en 39 secondes. » | Capture réelle, démo Fuji de 08:45 (paiement 9) |
| 3 | 0:35 – 1:15 | Trois paiements vers une adresse jamais vue, 280 500 mUSD. Le niveau passe à « mise en attente », l'explication s'affiche, « 2 sur 3 », puis gel et annulation. Compteur final : 0 mUSD sorti. | « Deux signataires trompés proposent 280 500. En 7 à 10 secondes, le garde l'inscrit sur la chaîne et explique pourquoi. Il manque une signature : rien ne part. » | Capture réelle (paiements 10 à 12), liens Snowtrace en surimpression |
| 4 | 1:15 – 1:40 | L'oracle : une recherche Web, trois pages, une citation surlignée, l'adresse inscrite au registre, le paiement de 25 000 mUSD refusé malgré 3 signatures. Mention « accéléré, 2 min 10 en réel ». | « Le garde lit aussi le Web. Cette adresse est sur la liste des sanctions : le portefeuille la refuse de lui-même. » | Terminal réel (collecte de 00:45, agent de 08:13) + capture du paiement 13 |
| 5 | 1:40 – 2:00 | L'agent cosignataire : trois lignes de décision qui s'écrivent (cosigne 3 200 ; refuse 600 000, « 60 % de la trésorerie » ; ne signe pas l'inconnu). Mention « chaîne de test locale ». | « En mode Cosignataire, un agent tient une signature. Il simule chaque paiement, puis signe ou s'abstient, et dit pourquoi. Vos signataires gardent le dernier mot. » | Terminal réel (`npm run agent:local`, 08:17) |
| 6 | 2:00 – 2:15 | Motion : la cadence de Drift, 31 retraits en 12 minutes, une barre qui se remplit en accéléré, puis « 0 mUSD sorti sur 285 000 ». Mention « avec le seuil de clés volées ». | « Nous avons rejoué la cadence de Drift sur notre portefeuille : 31 retraits en 12 minutes, zéro sorti. » | Motion pur à partir des chiffres du rejeu de 01:26 (pas de capture) |
| 7 | 2:15 – 2:30 | Trois chiffres : 91 % des montants frauduleux mis en attente, 5,1 % de paiements légitimes retenus, 0 mUSD sorti en démo. Puis « Prototype non audité, données synthétiques, réseau de test ». Logo et slogan. | « Mesuré sur des fraudes dont le garde n'avait jamais vu la forme. Prototype de hackathon, non audité. » | Motion pur, section « Chiffres » du site |

## Faut-il simuler une attaque à la cadence de Drift dans la vidéo ?

**Non, pas en direct. Oui, comme un plan de 15 secondes en motion (plan 6), à partir du rejeu déjà fait.**

- **Douze minutes ne tiennent pas dans une vidéo de 2 min 30.** Il faudrait accélérer 30 fois une capture d'écran de terminal : illisible.
- **Le rejeu est déjà fait et noté** (Fuji, 01:26 à 01:38, 31 retraits, 285 000 mUSD tentés, 0 sorti). Le rejouer ne prouverait rien de plus et occupe le relais Fuji 20 minutes.
- **Le résultat dépend du nombre de clés volées.** Avec le seuil (2 sur 5), rien ne sort. Avec une de plus, 119 600 mUSD sont sortis sur 285 000 en essai local. La vidéo doit donc porter la mention « avec le seuil de clés volées », et la limite va sur la slide A3 ou « ce qu'il reste à faire ».
- **Le scénario principal du deck est celui des 280 500 mUSD.** C'est lui qui porte la slide 5 : la vidéo doit montrer le même, pas un autre chiffre.

## Ce que la vidéo ne doit pas dire

- « Nous avons rejoué Drift » : c'est la cadence qui est rejouée, sur un portefeuille de trésorerie. Drift était la prise des droits d'administration d'un protocole sur Solana.
- « L'IA bloque » : en mode Cosignataire, le refus met en attente, les signataires peuvent passer outre après un délai.
- Le fonctionnement de la clé de contrainte (décision de Timéo du 10 octobre : dit au jury à l'oral, jamais écrit ni filmé).
- Un montant « sauvé » réel : tout est en mUSD de test.

## Mentions à garder à l'image

- « Avalanche Fuji, réseau de test » sur les plans 2 à 4 ; « chaîne de test locale » sur le plan 5.
- « Accéléré » dès qu'une attente est coupée (délai d'examen de 30 s, lecture du Web).
- L'heure d'été de la démo fait apparaître « hors heures ouvrées » dans les raisons : le couper au montage ou le dire, mais ne pas le présenter comme un signal de fraude.

## Ce qu'il faut capturer avant le montage

1. Le tableau de bord sur les données de la démo de 08:45 (`shared/demo-finale-20261011/`, encore ouvert sur ce PC) : paiements 9, 10 à 12, 13.
2. Un terminal avec `npm run agent:local` (commandes dans l'entrée du journal de 08:19), relais local sur un autre dossier que `shared/`.
3. Un terminal avec la lecture du Web par l'agent (`--web`, adresse `0x098B…2f96`) : 2 min 10, à accélérer.
