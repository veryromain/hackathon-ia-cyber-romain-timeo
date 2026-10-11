# Voix off de la vidéo de démonstration (v1, 2 min 30)

> Romain (avec Claude), 11/10 vers 09:50, d'après le plan en 7 plans de Timéo (`shared/plan-video-motion.md`). Même texte que les sous-titres de `shared/video/motion-v1.html`. Vocabulaire fixé : signature en plus · mise en attente · Cosignataire (jamais « bloqué », « arrêté »). Lire posément : ≈ 130 mots par minute.

| Temps | Plan | Texte |
|---|---|---|
| 0:00 | 1 Problème | Bybit, un milliard quatre cent soixante millions. Drift, deux cent quatre-vingts millions. Dans les deux cas, personne n'a volé de clé au moment du paiement. Des signataires ont validé. Breaker est la garde antifraude qui se greffe sur le coffre que vous avez déjà. |
| 0:15 | 2 Paiement normal | Un paiement habituel, vers un prestataire connu : deux signatures, trente secondes d'examen. Il passe sans friction, trente-neuf secondes après la proposition. Tout est vérifiable sur l'explorateur. |
| 0:35 | 3 L'attaque | Deux signataires trompés proposent trois paiements vers une adresse jamais vue : deux cent quatre-vingt mille. En sept à dix secondes, le garde met chaque paiement en attente, l'inscrit sur la chaîne, et explique pourquoi, en français. Nouveau destinataire, montants hors norme, trois paiements en deux minutes, un libellé qui insiste sur l'urgence et le secret. Il demande une signature de plus. Il en manque une : rien ne part. Un signataire alerté gèle le coffre et annule. Zéro sorti sur deux cent quatre-vingt mille. |
| 1:15 | 4 L'oracle | Le garde lit aussi le Web. Un paiement de vingt-cinq mille vers une adresse nouvelle : d'abord une signature en plus. Puis il cherche, lit trois pages, retient une citation exacte : cette adresse est sur la liste des sanctions. L'adresse est inscrite au registre. Même avec trois signatures, l'attente reste : le paiement est annulé. |
| 1:40 | 5 Cosignataire | En mode Cosignataire, un agent tient une signature. Il simule chaque paiement, puis signe ou s'abstient, et dit pourquoi. Une facture habituelle : il cosigne. Soixante pour cent de la trésorerie d'un coup : il refuse. Un inconnu : il attend un humain de plus. Vos signataires gardent le dernier mot. |
| 2:00 | 6 Cadence de Drift | Nous avons rejoué la cadence de Drift : trente et un retraits en douze minutes, approuvés par deux clés volées. Chacun mis en attente. Zéro exécuté, zéro sorti sur deux cent quatre-vingt-cinq mille. |
| 2:15 | 7 Chiffres | Mesuré sur des fraudes dont le garde n'avait jamais vu la forme : quatre-vingt-onze pour cent des montants mis en attente, cinq pour cent de paiements légitimes retardés. Prototype de hackathon, non audité, sur réseau de test. Breaker. Une signature ne suffit pas à faire confiance. |

## Ce qu'on ne dit pas (plan de Timéo)
« Nous avons rejoué Drift » (c'est la cadence) · « l'IA bloque » · le fonctionnement de la clé de contrainte · un montant réel sauvé.

## Comment produire le mp4 à partir de la v1
1. Ouvrir `shared/video/motion-v1.html` dans Chrome, touche **F** (plein écran), **R** pour relancer.
2. Mac : ⌘⇧5 → « Enregistrer l'écran entier » → démarrer, appuyer sur **R**, laisser 2 min 30, arrêter. Le fichier .mov arrive sur le Bureau ; iMovie l'exporte en mp4 et permet d'ajouter la voix (micro) par-dessus, ou de remplacer un plan par les captures de Timéo (`plan2-agent-cosignataire.mp4`, `plan3-agent-web.mp4`, `plan4-tableau-de-bord.mp4`).
3. Windows (Timéo) : Win+Alt+R sur la fenêtre Chrome.
