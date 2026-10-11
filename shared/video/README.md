# Matière de la vidéo (plan : `shared/plan-video-motion.md`)

Rassemblé par Timéo (avec Claude) le 11 octobre à 9 h. Tout vient de démonstrations réellement jouées ; rien n'est retouché. Ce sont des images fixes et des textes de terminal, à animer : il n'y a pas de capture vidéo de l'écran dans ce dossier.

| Fichier | Plan | Ce que c'est | D'où ça vient |
|---|---|---|---|
| `plan3-fiche-paiement-10.png` | 3 | Fiche du tableau de bord : 95 000 mUSD vers une adresse jamais vue, mise en attente, score 0,88, explication rédigée | Démo Fuji de 08:25, paiement 10 |
| `plan3-fiche-paiement-12.png` | 3 | Même attaque, troisième paiement : 92 000 mUSD, « Opération confidentielle validée par la direction » | Démo Fuji de 08:25, paiement 12 |
| `plan4-fiche-paiement-13-sanctions.png` | 4 | Fiche du paiement de 25 000 mUSD vers l'adresse sanctionnée, score 0,97, « signalé par l'oracle (sanctions) » | Démo Fuji de 08:25, paiement 13 |
| `plan4-terminal-agent-web.txt` | 4 | L'agent lit le Web : avis « freiner » en 6 s, puis « refuser » après lecture de 3 pages, avec la citation retenue | Essai de 08:13, réseau Avalanche pour l'historique |
| `plan5-terminal-agent-cosignataire.txt` | 5 | L'agent cosignataire : cosigne 3 200 mUSD, refuse 600 000, ne signe pas l'inconnu | Essai de 08:17, chaîne de test locale |
| `plan6-terminal-drift-fuji.txt` | 6 | Les 31 retraits à la cadence de Drift, un par un, tous bloqués | Rejeu Fuji de 01:26 |

## La vidéo elle-même

`video.html` est la vidéo, construite comme une page animée (sept plans, environ 2 min 30). L'ouvrir dans Chrome ou Edge, plein écran (F11), lancer l'enregistrement de l'écran, puis appuyer sur Espace. Elle lit les quatre plans filmés dans un dossier `plans/` placé à côté d'elle ; ces fichiers (71 Mo) ne sont pas dans le dépôt, ils sont sur le PC de Timéo dans `C:\Users\bvtim\breaker-video\plans\`.

## À savoir avant de monter

- **Les images sont des fiches seules**, sans les compteurs du haut du tableau de bord. C'est voulu : le compteur « Montant protégé » affiche 802 800 mUSD parce qu'il additionne la répétition de 07:31 et la démo de 08:25. Le chiffre du deck est 280 500 mUSD pour l'attaque des paiements 10 à 12.
- **Les fiches portent le badge « annulé »** : elles ont été capturées après la fin du scénario.
- **`OFF_HOURS` apparaît dans les raisons** parce que la démo a été jouée un dimanche matin. À ne pas présenter comme un signal de fraude.
- **Le paiement normal du plan 2 (3 150 mUSD) n'a pas de fiche** : le tableau de bord ne liste que les paiements signalés. Pour ce plan, utiliser le lien de l'exécution sur Snowtrace (entrée du journal de 08:45) ou une animation.
- **Le paiement 14 (clé de contrainte) n'est pas dans ce dossier**, par décision de Timéo.
- **La première ligne de l'explication du plan 4 dit « la simulation est absente »** : dans cet essai l'agent n'avait pas de portefeuille à simuler (paiement fictif sur le réseau principal, lu seulement pour l'historique). La simulation tourne dans l'essai du plan 5.
- Le fichier du plan 6 s'arrête avant la coupure réseau de la fin ; le bilan est celui lu ensuite sur la chaîne.

## Pour une vraie capture vidéo de l'écran

Aucun enregistreur n'est installé sur le PC de Timéo. Windows en fournit un : `Windows + Alt + R` démarre et arrête l'enregistrement de la fenêtre active (barre de jeu Xbox), le fichier arrive dans `Vidéos\Captures`. Le tableau de bord est sur `http://127.0.0.1:8599` tant qu'il tourne.
