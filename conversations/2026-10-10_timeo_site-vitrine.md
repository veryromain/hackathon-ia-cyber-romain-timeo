# Site vitrine Breaker

Timéo demande de commencer le site. Première maquette créée : page française, toutes les cibles, trois scénarios interactifs et mesures synthétiques. Sources dans ia-2/site-vitrine. Vérification Chrome ordinateur et mobile, syntaxe JavaScript et interactions. Publication Sites privée en préparation. Aucun abonnement ni connexion du portefeuille implémenté.

## Publication — 2026-10-10 20:27

Déploiement privé confirmé : https://breaker-treasury.espace-de-tr-0859.chatgpt.site . Connexion ChatGPT requise. P2 terminé au niveau maquette. Sources copiées et poussées dans le dépôt. Les fonctions réelles de compte et de signature restent hors de cette version.

## Charte, logo et haut de page animé — 2026-10-10 21:45 (Timéo avec Claude)

Timéo montre une capture du site de Safe (des cartes de portefeuilles posées sur un nuage gris, sur une trame de carrés) et demande : une charte de couleurs différente de celle de Safe, adaptée à la cybersécurité et qui mette le client en confiance ; le logo d'avant, redessiné dans le même style ; un fond interactif, avec autre chose que des carrés ; des bulles qui apparaissent et repartent. Les appels à l'action lui conviennent. Le reste du site sera revu plus tard.

Décisions prises en faisant :

- **Couleurs :** bleu nuit, cobalt et fond givre. Le bleu est la couleur que les clients associent à la sécurité et à la banque ; le vert et l'ambre restent réservés aux réponses du garde, pour qu'une couleur veuille toujours dire la même chose.
- **Logo :** le B dans son bloc à pans coupés de la première maquette, redessiné en SVG, en cobalt.
- **Fond :** des tuiles qui ont la silhouette du logo plutôt que des carrés arrondis. Elles s'allument sous le curseur, un clic envoie une onde.
- **Bulles :** des paiements plutôt que des portefeuilles. Chacun arrive, attend le verdict, puis repart ; le nombre de signatures exigées passe de 2/2 à 2/3 quand le garde freine. C'est le produit montré en quelques secondes.
- **Adresses affichées :** comptes de test du déploiement Fuji ou adresses inventées. L'adresse réellement sanctionnée utilisée dans la démo de Romain n'est pas reprise sur le site.

Fichiers : `ia-2/site-vitrine/dist/` (les trois fichiers) et `ia-2/site-vitrine/README.md` (tableau des couleurs). Vérifié dans un navigateur à 1440 px et 390 px.

Prochaines étapes : republier le site (Codex) ; revoir le reste de la page avec Timéo.
