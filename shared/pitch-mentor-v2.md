# Pitch mentor, version 2 (axe 2, trésoreries à plusieurs signataires)

> Rédigé par Claude pour Timéo le 10 octobre vers 23h00. Remplace `pitch-mentor.md`, qui date de l'axe 4.
> À dire à l'oral, sans slides, en deux minutes. Le but est d'obtenir un avis franc, pas de convaincre.
> Tous les chiffres viennent de `shared/mesures.md` et de `ia-2/README.md`.

## Le pitch (environ 2 minutes)

**Le problème.**
En février 2025, Bybit a perdu environ 1,46 milliard de dollars. Aucune clé n'avait été volée : trois de ses six signataires ont validé une transaction que leur écran affichait falsifiée. En avril 2026, Drift a perdu environ 280 millions en 12 minutes, après la manipulation de ses signataires.

Un portefeuille à plusieurs signataires protège contre une clé volée. Il ne protège pas contre des signataires trompés, pressés ou menacés. Et les équipes les plus exposées sont les plus petites : un protocole, une DAO, une startup crypto, vingt personnes, des millions en trésorerie, personne pour surveiller.

**Notre solution : Breaker, un garde antifraude pour ces trésoreries.**
Chaque paiement est noté avant son exécution, à partir des habitudes de l'équipe et de ce qui se dit sur le Web à propos du destinataire. S'il est suspect, le portefeuille exige une signature de plus, ou le met en attente, et chaque signataire reçoit une alerte expliquée en clair.

Nous ne bloquons rien et nous ne détenons jamais les fonds. Notre outil ne peut qu'ajouter une vérification, que les signataires peuvent lever ensemble. S'il se trompe ou tombe en panne, le client perd une signature et un peu de temps, jamais l'accès à son argent.

**Ce qui tourne aujourd'hui.**
Tout est déployé sur le testnet Avalanche Fuji. Deux signataires trompés tentent de sortir 280 500 dollars en trois virements : les trois sont mis en attente en quelques secondes, un collègue gèle et annule, zéro dollar sort. Chaque décision est inscrite sur la chaîne avec ses raisons.

Sur des fraudes dont le garde n'avait jamais vu la forme, mesurées une seule fois, 91 % des montants sont mis en attente.

## Les chiffres clés

| Chiffre | Ce qu'il mesure | À dire avec |
|---|---|---|
| **91 %** | Montants frauduleux mis en attente, sur 40 fraudes de formes jamais vues | Mesuré une seule fois, sur un jeu préparé à l'aveugle |
| **95 %** | Fraudes freinées ou mises en attente, dont 78 % mises en attente | Les 5 % manqués sont les petits paiements d'une mise en confiance |
| **5,1 %** | Paiements légitimes mis en attente à tort | Tous de gros premiers paiements à un nouveau bénéficiaire ; 0 % sur les prestataires récurrents |
| **0 mUSD** | Sorti sur 280 500 tentés, démo sur Fuji | Vérifiable sur l'explorateur |
| **5 à 6 s** | Délai de signalement sur Fuji, pour 30 s de délai d'examen | 10 à 20 s quand l'explication est rédigée par le modèle de langage |
| **0,002 $** | Coût en gas d'une alerte | Le gas est négligeable dans un abonnement |
| **50** | Tests automatiques du contrat | Prototype non audité |

**La réserve à dire d'emblée :** toutes les données sont synthétiques, fabriquées par nous. Ces chiffres ne garantissent rien sur un trafic réel.

## Ce qui nous démarque

1. **Freiner au lieu de bloquer.** Les outils existants avertissent dans l'interface, ou bloquent la transaction. Nous ajoutons une signature, puis un délai. Un garde en panne ou compromis ne peut pas verrouiller les fonds.
2. **Une mesure honnête.** Le moteur a été réglé sur un jeu, puis évalué une seule fois sur un jeu final préparé à l'aveugle par l'autre membre de l'équipe. Nous montrons les deux résultats côte à côte, y compris le moins bon.
3. **Tout est vérifiable.** Chaque signalement est sur la chaîne, avec ses raisons. Le jury peut ouvrir l'explorateur pendant le pitch.
4. **Le pont Web vers blockchain.** Un oracle lit les signalements de fraude publiés sur le Web, ne retient une accusation que s'il retrouve la citation exacte dans la page, et inscrit l'adresse dans un registre que le portefeuille consulte. Les fausses accusations répétées par une même source sont rejetées.
5. **On protège aussi la personne.** Une clé neuve ne compte pas pendant deux jours sur un paiement signalé, ce qui répond à la forme de Bybit. Et chaque signataire dispose d'une seconde clé, gardée à part, qui lui permet de révoquer la sienne en une transaction ou de signer sous la menace sans que le paiement parte.
6. **Une cible que personne ne sert.** Les grandes plateformes ont leurs équipes et leurs outils. Les équipes de vingt personnes n'ont rien à un prix affiché.

## Ce qui est fragile, à ne pas cacher

- Données synthétiques, une seule organisation fictive, trois mois de trafic.
- Contrat non audité, sur un réseau de test.
- Nous avons écrit notre propre portefeuille. Un vrai client utilise Safe ou Squads : le module qui s'y greffe reste à écrire, et chez Safe les signatures sont réunies hors de la chaîne.
- Une signature de plus ne sert à rien si l'attaquant tient déjà assez de clés. Seule la mise en attente protège dans ce cas.
- Sur une chaîne publique, rien n'est secret : la parade contre la contrainte est lisible par qui sait lire le contrat.
- Aucun client interrogé, aucun prix validé.

## Les questions à poser au mentor

**Sur le produit**
1. Freiner plutôt que bloquer : est-ce un vrai avantage pour une équipe de protocole, ou préfèrent-elles un blocage net ?
2. Qui décide des réglages (seuils, délais) chez le client, et comment éviter qu'un signataire compromis les assouplisse ?
3. Notre délai d'examen est de 30 secondes en démo. Quel délai une équipe accepterait-elle sur tous ses paiements : une minute, une heure, un jour ?
4. La seconde clé par signataire : est-ce utilisable en pratique, ou un frein à l'adoption ?

**Sur la technique**
5. Faut-il abandonner notre portefeuille maison et tout reconstruire comme module de Safe ? Qu'est-ce qui se perd si les signatures ne sont plus sur la chaîne ?
6. Qu'est-ce qu'Avalanche permet ici que les autres chaînes ne permettent pas (finalité, chaînes dédiées) ?
7. Notre oracle est une source centralisée. Comment le rendre crédible : plusieurs opérateurs, preuves publiées, contestation ?

**Sur la mesure**
8. Nos données sont synthétiques. Quelle preuve convaincrait un jury ou un premier client : rejouer un incident réel, un pilote, un audit ?
9. 5 % de paiements légitimes mis en attente : acceptable, ou rédhibitoire ?

**Sur le marché**
10. Qui paie : le protocole, sa fondation, ses investisseurs, son assureur ?
11. Par quel canal atteindre ces équipes : les cabinets d'audit, les écosystèmes comme Avalanche, les places de marché d'applications des portefeuilles ?
12. Face à Hypernative Guardian, déjà intégré à Safe, quel est notre angle le plus défendable ?

**Sur la conformité**
13. Notre cible n'est en général pas une entité régulée. Quel angle mettre sur la slide : filtrage des contreparties, AI Act et supervision humaine, traçabilité ?
14. Un registre public d'adresses « accusées » nous expose-t-il juridiquement ? Que faut-il prévoir pour la contestation ?

**La question à poser en dernier :** « Si vous étiez dans le jury demain, qu'est-ce qui vous ferait douter ? »
