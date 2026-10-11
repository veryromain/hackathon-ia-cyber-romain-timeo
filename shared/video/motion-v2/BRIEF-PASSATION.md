# Brief de passation — finaliser le motion design v2 de Breaker

> Pour l'assistant qui reprend la vidéo (Claude Cowork ou autre). Tout est dans le dépôt `hackathon-ia-cyber`, dossier `shared/video/motion-v2/`. Lire dans cet ordre.

## 1. Ce qu'il faut lire (10 minutes)

| Ordre | Fichier | Pourquoi |
|---|---|---|
| 1 | `shared/video/motion-v2/README.md` | Ce que montre et dit chaque plan, le style, les limites, comment regénérer |
| 2 | `shared/plan-video-motion.md` | Le plan de Timéo : les 7 plans d'origine, **ce que la vidéo ne doit pas dire**, les mentions obligatoires à l'image |
| 3 | `shared/video/motion-v2/construire_motion_v2.py` | Le seul fichier à modifier : `SCENES` en tête (texte de la voix, plan par plan), puis le HTML/CSS/JS de la page (gabarit `HTML`, fonctions `DRAW` pour l'animation de chaque plan) |
| 4 | `ia-2/site-vitrine/dist/style.css` et `index.html` | La charte à respecter (couleurs, polices, logo, slogans) |
| 5 | `shared/mesures.md`, `JOURNAL.md` (entrées du 11/10 09:52 et 10:40) | D'où viennent les chiffres ; ne pas en inventer d'autres |
| 6 | `shared/video/README.md` | La matière de Timéo : fiches PNG et sorties de terminal réelles |

Référence de rythme : trois reels Instagram de motion design « typographie cinétique » (un ou deux mots géants par coupe, flou de mouvement, chiffres incarnés par des formes, HUD monospace, cercles concentriques, bandeau répété). Seul le tempo est repris.

## 2. Règles non négociables

- **Charte du site** : fond `#07111F`, vert citron `#C7FA70`, bleu clair `#A8BFFF` (signature en plus), ambre `#FFC481` (mise en attente), verre dépoli, Manrope / DM Sans / IBM Plex Mono, logo « B » à pans coupés.
- **Vocabulaire** : signature en plus · mise en attente · Cosignataire. Jamais « bloqué », « l'IA bloque », « nous avons rejoué Drift » (dire « la cadence de Drift »), jamais la clé de contrainte, jamais un montant réel « sauvé » (tout est en mUSD de test).
- **Mentions à l'image** : « Avalanche Fuji · réseau de test · accéléré » (plans 4-5), « accéléré : 2 min 10 en réel » (6), « chaîne de test locale » (7), « avec le seuil de clés volées (2 sur 5) » (8), « données synthétiques » (9), réserves « prototype non audité » (10).
- **Chiffres autorisés** : 1,46 Md$ Bybit, 280 M$ Drift, 31 retraits / 12 min, 3 150 mUSD en 39 s, 95 000 + 93 500 + 92 000 = 280 500 mUSD, 10 / 7 / 9 s, 25 000 mUSD sanctions, 3 200 / 600 000 / 4 800 (Cosignataire), 285 000 mUSD, 91 %, 5,1 %, 5 à 6 s, ≈ 1 ¢, 30 jours d'essai, 149 / 449 / 990 €.

## 3. Comment modifier

- **Une phrase de la voix** : éditer `SCENES` dans le script. Les visuels se calent automatiquement sur le début de chaque phrase (`S.seg[i]` dans `DRAW`), donc changer une phrase ne casse pas le montage.
- **Un visuel** : modifier le bloc `<section class="scene" id="s-…">` concerné et sa fonction dans `DRAW`. Chaque image est une fonction pure du temps (`window.seek(t)`) : pas de transition CSS, pas de hasard.
- **Vérifier sans rendre** : `python3 construire_motion_v2.py --html` puis ouvrir `motion-v2.html` dans Chrome (Espace lecture, ← → plans, F plein écran).

## 4. Ce que l'assistant distant ne peut pas faire

Le rendu du mp4 a besoin de la machine de Romain : Piper (voix, `~/.local/share/piper-voices/`), Playwright + Google Chrome, ffmpeg. **Un assistant en environnement distant (Cowork, Claude Code sur le Web) peut lire et modifier le script, pas produire la voix ni le mp4.** Après ses modifications, Romain relance sur le Mac :

```bash
python3 shared/video/motion-v2/construire_motion_v2.py --tout
```

Environ 6 minutes. Seules les phrases modifiées sont resynthétisées, et dès que la page change, les images du rendu précédent sont effacées automatiquement : rien à nettoyer à la main.
