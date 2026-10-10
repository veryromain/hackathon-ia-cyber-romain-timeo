# Site vitrine Breaker

Maquette statique française avec présentation du garde, cibles, résultats synthétiques contextualisés et aperçu interactif de trois paiements. Aucune connexion réelle de portefeuille, transaction, abonnement ni collecte de contact.

Les mesures viennent de `shared/mesures.md` (10 octobre 2026). Le lien GitHub du protocole nécessite un accès au dépôt privé.

Pour l'ouvrir : servir `dist/` avec un serveur HTTP statique, ou ouvrir `dist/index.html` dans un navigateur. Aucun build nécessaire. Polices Google facultatives, avec repli système.

Source de travail Sites distincte du dépôt d'équipe, pour éviter les conflits Git. Copie complète des fichiers de la page dans ce dossier. Site publié en accès privé : https://breaker-treasury.espace-de-tr-0859.chatgpt.site (connexion ChatGPT du propriétaire requise).

## Révision du 10 octobre, 21h (Claude, à la demande de Timéo)

La maquette affichait des chiffres dépassés et ne disait rien du problème. Ce qui a changé dans `dist/` :

- **Nouvelle section « Le problème »** : Bybit (février 2025, environ 1,46 Md$, trois signataires sur six trompés) et Drift (avril 2026, environ 280 M$, 31 retraits en 12 minutes), avec un lien vers l'analyse de chaque incident.
- **Nouvelle section « Avertir, bloquer, ou freiner »** : notre positionnement, sans nommer de concurrent.
- **Section « Les preuves » refaite avec la mesure finale** de `shared/mesures.md` (jeu `final`, passé une fois à 20h40) : 91 % des montants frauduleux mis en attente, 0 mUSD sorti pendant la démo Fuji, 5 à 6 s pour signaler, 5,1 % de paiements légitimes mis en attente. Les anciens chiffres (65 % et 1,4 %) venaient du jeu de généralisation, mesuré avant les corrections du moteur.
- **Preuves vérifiables** : quatre liens Snowtrace vers le portefeuille de la démo et ses transactions sur Avalanche Fuji.
- **Réserves réécrites** sous les chiffres : ce que « freinée » ne garantit pas, données synthétiques, prototype non audité.
- **Prix** : une phrase sur le modèle (abonnement par portefeuille protégé). Aucun montant, la grille n'est pas décidée (tâche B6).

`app.js` n'a pas changé. Les styles ajoutés sont à la fin de `style.css`. Vérifié dans un navigateur à 1366 px et à 390 px : aucune barre de défilement horizontale, les trois scénarios et le bouton d'explication fonctionnent.

### Trois points d'attention

- **Le site publié n'est pas à jour.** L'adresse privée ci-dessus est alimentée par une copie de travail séparée, gérée par Codex. Ces modifications ne sont que dans le dépôt : il faut republier depuis cette copie, ou y reporter `dist/`, pour qu'elles apparaissent en ligne.
- **Les liens Snowtrace pointent vers le déploiement Fuji du 10 octobre à 19h29.** Si les contrats sont redéployés (par exemple pour la probation des clés neuves), il faudra mettre à jour les quatre liens de la section « Les preuves ».
- **Toujours absents**, par choix : formulaire de contact, « réserver une démo », connexion d'un portefeuille. La page ne collecte rien.

## Refonte visuelle du 10 octobre, 21h20 (Claude, à la demande de Timéo)

Timéo a demandé un design inspiré de celui de Safe{Labs} (safe.global). La page a été réécrite dans ce langage visuel, relevé sur leur site le soir même :

| Élément | Chez Safe{Labs} | Repris ici |
|---|---|---|
| Fond et texte | Gris très clair (#F5F5F5), texte presque noir | Identique |
| Titres | Très grands, très fins (police Citerne, graisse 300), interlignage serré | Police libre Outfit en graisse 300, mêmes proportions |
| Texte courant | DM Sans | DM Sans |
| Couleur d'accent | Vert menthe (#7FFAB7) sur les boutons | Identique |
| Cartes | Blanches, coins de 16 à 24 px, ombre douce | Identique |
| Chiffres clés | Rangée de cartes, grand chiffre fin, libellé en capitales espacées | Identique, avec une ligne de contexte sous chaque chiffre |
| Haut de page | Titre à gauche sur une trame de carrés arrondis, aperçu du produit à droite | Identique, avec notre carte de paiement en attente |
| Rythme | Sections claires, une longue section sombre, questions fréquentes, appel final | La démo interactive est la section sombre ; six questions ajoutées |

**Ce qui n'est pas repris :** leur logo, leur nom, leurs textes, leurs images, leur police propriétaire. Le site reste celui de Breaker ; il ne se fait pas passer pour celui de Safe.

Le contenu est celui de la révision de 21h (problème, positionnement, mesure finale, preuves Fuji), plus une section « Questions fréquentes » : détention des fonds, erreur du garde, panne, blockchains, audit, prix.

`app.js` : une seule ligne changée (couleur de la jauge). `style.css` et `index.html` : réécrits, lisibles, non minifiés. L'ancienne version sombre reste dans l'historique Git (commit `3ce2b94`).

Vérifié dans un navigateur à 1440 px et à 390 px : aucune barre de défilement horizontale, polices chargées, les trois scénarios et le bouton d'explication fonctionnent.

## Charte, logo et haut de page animé, 10 octobre, 21h45 (Claude, à la demande de Timéo)

Timéo a demandé quatre choses : une charte de couleurs qui ne soit plus celle de Safe et qui inspire confiance, le retour du logo d'avant, un fond interactif, et des bulles qui apparaissent puis repartent. La mise en page, les textes et les boutons d'appel à l'action n'ont pas changé.

### Charte de couleurs

| Rôle | Couleur | Valeur |
|---|---|---|
| Fond | Givre | `#F2F5FA` |
| Texte, section sombre, pied de page | Bleu nuit | `#0A1B33` |
| Boutons, liens, logo | Cobalt | `#2454E6` |
| Accent sur fond sombre | Cobalt clair | `#8FB1FF` |
| Réponse « sans friction » | Vert | `#0B7F5F` |
| Réponse « signature supplémentaire » | Cobalt | `#2454E6` |
| Réponse « en attente » | Ambre | `#9A5600` sur `#FDF0D8` |

Le vert menthe et le gris neutre de Safe ont disparu. Toutes les valeurs sont des variables en tête de `style.css`.

### Logo

Celui de la première maquette : un B dans un bloc à deux pans coupés, suivi de « breaker. » en minuscules grasses avec le point en couleur. Il est redessiné en SVG (le B n'est plus une lettre de police) et passe du vert citron au cobalt. Il est défini une fois en tête de `index.html` (`<symbol id="mark">`) et repris par `<use>`.

### Fond interactif

Une trame de tuiles qui ont la silhouette du logo, dessinée par `app.js` dans un `<canvas class="field">`, en haut de page et dans l'appel final. Les tuiles proches du curseur s'allument en cobalt puis s'éteignent ; un clic envoie une onde. Sans JavaScript, un motif fixe équivalent reste affiché.

### Flux de paiements

À droite du titre, trois emplacements posés sur un « nuage » de tuiles pleines. Chaque paiement arrive avec la mention « Analyse en cours », reçoit son verdict au bout d'une seconde (le nombre de signatures exigées passe de 2/2 à 2/3 quand le garde freine), puis laisse la place au suivant. Six paiements tournent : trois sans friction, un avec signature supplémentaire, deux en attente. Les adresses sont celles des comptes de test du déploiement Fuji ou sont inventées ; aucune ne vient d'une liste réelle. Ce flux remplace la carte fixe « Paiement proposé » et sa légende.

Si le visiteur a demandé à réduire les animations, trois paiements fixes s'affichent, la trame réagit sans traînée et sans onde. Quand l'onglet est caché, le flux s'arrête.

Vérifié dans un navigateur à 1440 px et à 390 px : aucune erreur dans la console, aucune barre de défilement horizontale, survol et clic sur la trame, défilement des paiements, démo des trois scénarios. Le site publié (adresse privée gérée par Codex) n'a pas changé : il faut republier depuis `dist/`.

