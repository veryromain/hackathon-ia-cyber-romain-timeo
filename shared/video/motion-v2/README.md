# Motion design v2 — vidéo de démonstration avec voix off (livrable L1)

> Romain (avec Claude), 11 octobre 2026, 10 h – 10 h 40. Remplace la v1 (`shared/video/motion-v1.html`, sans voix) : mêmes faits, même identité que le site vitrine, mais un montage « typographie cinétique » et une **voix off synthétisée** calée image par image.

| Fichier | Quoi |
|---|---|
| **`motion-v2.mp4`** | La vidéo finale, 1920 × 1080, 30 i/s, 2 min 55, H.264 + voix AAC. **C'est ce fichier qui se lance à la diapo 5 du deck.** |
| `motion-v2.html` | La même vidéo en page autonome (voix incluse) : ouvrir dans Chrome, **Espace** lecture / pause, **←/→** plan précédent / suivant, **R** début, **F** plein écran, **S** sous-titres. |
| `construire_motion_v2.py` | Le script qui fabrique tout : voix, chronologie, page, rendu. |
| `timeline.json` | Chronologie des 10 plans et des 22 phrases (début, durée), produite par la voix. |
| `voix-off.mp3` | La piste voix seule (normalisée −16 LUFS). |
| `motion-v2-vignette.jpg` | Une image du plan « marque », pour les documents. |

## Ce que dit la voix (22 phrases, 10 plans)

Vocabulaire fixé : signature en plus · mise en attente · Cosignataire. Jamais « bloqué », « l'IA bloque », « nous avons rejoué Drift », ni la clé de contrainte, ni un montant réel sauvé. Les chiffres sont ceux des démonstrations jouées (`JOURNAL.md`, `shared/mesures.md`), le texte est dans `SCENES` en tête du script.

| Plan | Durée | À l'écran | Voix |
|---|---|---|---|
| 1 Problème | 0:00 | « 1,46 Md$ » et « 280 M$ » qui claquent, bulles proportionnelles, 31 barres ; puis « Aucune clé volée. » / « Des signataires ont validé. » | Bybit, Drift, 31 retraits en 12 minutes ; personne n'a volé de clé, des signataires ont validé |
| 2 Marque | 0:15 | Trois clés cochées, carte « 95 000 mUSD validé de bonne foi », « Pas contre un mauvais paiement. » ; logo, « breaker. », slogan du site | Un multisig protège contre une clé volée, pas contre un mauvais paiement ; Breaker se greffe sur le coffre que vous avez déjà ; « Une signature ne suffit pas à faire confiance » |
| 3 Trois réponses | 0:30 | Jauge d'analyse, trois pastilles vert / bleu / ambre | Noté avant exécution ; sans friction, signature en plus, mise en attente ; jamais de fonds détenus, les signataires gardent le dernier mot |
| 4 Paiement normal | 0:47 | Carte 3 150 mUSD, 1/2 → 2/2, compteur 0 → 39 s, « exécuté », hash Snowtrace | Deux signatures, aucune friction, exécuté 39 s après la proposition |
| 5 Attaque | 0:57 | Trois cartes 95 000 / 93 500 / 92 000, compteur 280 500, badges « mise en attente » avec ondes, fiche réelle du paiement 10 (explication surlignée), quatre raisons en mots géants, « 2 / 3 », gel, annulé ×3, « 0 mUSD » | Deux signataires trompés ; moins de dix secondes, inscrit sur la chaîne, expliqué en français ; les quatre raisons ; il manque une signature, rien ne part ; gel et annulation ; zéro sorti sur 280 500 |
| 6 Oracle | 1:31 | Terminal réel (freiner 6,2 s → trois pages lues → citation OFAC → refuser 4,7 s), « SANCTIONS », registre, fiche du paiement 13, 3/3 signatures mais attente maintenue, annulé | Le garde lit aussi le Web ; liste de sanctions ; inscrite au registre pour tous les clients ; même avec trois signatures, l'attente reste |
| 7 Cosignataire | 1:53 | Trois décisions réelles : a cosigné 3 200 ; n'a pas signé 600 000 (60 % de la trésorerie) ; attend un humain pour 4 800 | L'agent tient une signature, simule, signe ou s'abstient et dit pourquoi ; vos signataires gardent le dernier mot |
| 8 Cadence de Drift | 2:13 | 31 barres qui montent avec le compteur, puis cerclées « attente », « 0 exécuté. » | 31 retraits en 12 minutes par deux clés volées, chacun mis en attente, zéro sorti sur 285 000 |
| 9 Chiffres | 2:26 | 91 % (compteur), 5,1 %, 5 à 6 s, ≈ 1 ¢, « 30 jours d'essai gratuit », « dès 149 € / mois » | Mesuré sur des formes jamais vues ; 91 % ; 5,1 % ; un centime par alerte ; essai 30 jours puis 149 € |
| 10 Fin | 2:45 | Réserves en capitales, logo, « Gardez la main sur votre trésorerie. », « Construit pour Avalanche. Pensé pour les signataires. » | Prototype non audité, réseau de test ; Breaker, gardez la main |

Mentions à l'image (coin haut droit) : « Avalanche Fuji · réseau de test · accéléré » (plans 4-5), « accéléré : 2 min 10 en réel » (6), « chaîne de test locale · mode Cosignataire, en option dès Standard » (7), « avec le seuil de clés volées (2 sur 5) » (8), « jeu de test final · formes de fraude jamais vues · données synthétiques » (9).

## D'où vient le style

Trois reels de motion design « générés par Claude » ont servi de référence de rythme (un ou deux mots géants par coupe, flou de mouvement à l'entrée, chiffres incarnés par des formes, HUD monospace dans les coins, cercles concentriques sur les événements, bandeau de texte répété, grain). **La charte est celle du site vitrine** (`ia-2/site-vitrine/dist/style.css`) : bleu nuit `#07111F`, vert citron `#C7FA70`, bleu clair `#A8BFFF` (signature en plus), ambre `#FFC481` (mise en attente), verre dépoli, lumières de fond qui dérivent, trame de points, Manrope / DM Sans / IBM Plex Mono, logo « B » à pans coupés. Aucun élément visuel des reels n'est repris, seulement leur tempo.

## Comment c'est fabriqué (et comment refaire)

1. **Voix** : chaque phrase est synthétisée séparément avec [Piper](https://github.com/rhasspy/piper) (voix française `fr_FR-siwis-medium`, hors ligne, gratuite). La durée réelle de chaque phrase fixe la chronologie : les visuels se calent sur le début de chaque phrase, jamais l'inverse. Les phrases sont collées sur une piste silencieuse avec 0,45 s entre elles.
2. **Page** : `motion-v2.html` est une page 1920 × 1080 dont chaque image est une **fonction pure du temps** (`window.seek(t)`), sans transition CSS ni hasard : le navigateur et le moteur de rendu produisent exactement la même image.
3. **Rendu** : Playwright pilote le Chrome installé sur le Mac, capture 5 260 images à 30 i/s (environ 5 minutes), puis ffmpeg encode le mp4 et y mixe la voix.

```bash
# Outils (une fois) : uv tool install piper-tts playwright ; ffmpeg dans le PATH ; Google Chrome installé.
python3 shared/video/motion-v2/construire_motion_v2.py --tout     # voix → html → mp4
python3 shared/video/motion-v2/construire_motion_v2.py --html      # seulement la page (après un changement visuel)
python3 shared/video/motion-v2/construire_motion_v2.py --rendu     # seulement le rendu (reprend les images déjà faites)
```

Pour changer une phrase : modifier `SCENES` puis relancer `--tout` (seules les phrases modifiées sont resynthétisées). Pour changer la voix : `PIPER_MODEL=/chemin/voix.onnx` ; pour le débit : `PIPER_LENGTH=0.9` (plus rapide) ou `1.0`.

## Limites, à dire si on nous le demande

- **Voix synthétique** (Piper, modèle libre) : intelligible mais pas une voix d'acteur. Les autres services testés étaient inaccessibles ce matin (edge-tts refusé par Microsoft, Polly : jeton AWS expiré, Higgsfield : zéro crédit). Pour une voix humaine, enregistrer `voix-off` phrase par phrase et remplacer les fichiers `voix/NN-NN.wav` avant `--rendu` ; la chronologie se recale toute seule.
- **Pas de capture vidéo réelle de l'écran** : les fiches du tableau de bord sont des images fixes (celles de Timéo), les terminaux sont rejoués à partir de leurs sorties réelles ; le plan 4 est une reconstitution (le tableau de bord ne liste pas un paiement non signalé).
- Pas de musique : à ajouter au montage si le jury l'entend dans une salle bruyante, la piste voix seule est fournie.
- Durée 2 min 55 au lieu des 2 min 30 visées : trois phrases de plus que la v1 (les trois réponses, le prix, le slogan de fin). Pour tenir 2 min 30, retirer le plan 3 ou le plan 9 et relancer `--tout`.
