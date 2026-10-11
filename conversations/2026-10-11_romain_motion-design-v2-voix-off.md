# 2026-10-11 — Romain (avec Claude) — Motion design v2 avec voix off

## Demande

Romain a donné trois reels Instagram de motion design (typographie cinétique « générée par Claude ») comme référence de **rythme et de forme**, en demandant de garder l'identité du site vitrine (couleurs, typographies, logo) et d'ajouter une **voix off** qui explique le problème, la solution, les chiffres et les slogans.

## Ce qui a été fait

1. **Installation du plugin `watch`** (`bradautomates/claude-video`) dans Claude Code, avec ses dépendances (yt-dlp, ffmpeg statique, via `uv` : pas de Homebrew sur le Mac). Les trois reels ont été téléchargés et découpés en images pour en extraire le langage : un ou deux mots géants par coupe avec flou de mouvement, chiffres incarnés par des bulles, HUD monospace, cercles concentriques, bandeau de texte répété, grain.
2. **Voix off** : edge-tts (Microsoft) refusé (403), Polly impossible (jeton AWS expiré), Higgsfield à zéro crédit → **Piper**, voix française libre `fr_FR-siwis-medium`, hors ligne. Les 22 phrases sont synthétisées une par une ; leurs durées fixent la chronologie des 10 plans.
3. **`shared/video/motion-v2/`** : `construire_motion_v2.py` (voix → `timeline.json` → `motion-v2.html` → rendu Playwright/Chrome → `motion-v2.mp4`), README avec le texte complet et le mode d'emploi. La page HTML est une fonction pure du temps (`window.seek(t)`), donc le rendu est identique dans le navigateur et dans le mp4.
4. **Contenu** : les 7 plans de Timéo, plus trois ajouts demandés par le brief « problème, solution, chiffres, slogans » : un plan « trois réponses » (sans friction / signature en plus / mise en attente, jamais de fonds détenus), la ligne de prix (30 jours d'essai, dès 149 €/mois) dans le plan des chiffres, et les deux slogans du site (« Une signature ne suffit pas à faire confiance », « Gardez la main sur votre trésorerie »). Vocabulaire et interdits du plan de Timéo respectés.

## Décisions

- La vidéo finale est **`shared/video/motion-v2/motion-v2.mp4`** (2 min 55, 1080p30, voix AAC). La v1 reste dans le dépôt pour l'historique.
- Les fichiers intermédiaires (segments wav, images du rendu) sont ignorés par git ; la synchro automatique en avait déjà poussé une partie, retirés du suivi.
- Durée 2 min 55 au lieu de 2 min 30 : accepté pour garder les trois ajouts ; le README dit quel plan couper pour revenir à 2 min 30.

## Prochaines étapes

- Timéo / Romain : regarder le mp4 en entier avec le son et relire la voix (prononciation des nombres, débit). Une phrase se corrige dans `SCENES` et se régénère seule.
- Si une voix humaine est voulue : enregistrer les 22 phrases et remplacer `voix/NN-NN.wav`, puis `--rendu`.
- Vérifier que la diapo 5 du deck lance bien le mp4 (et non la page HTML) sur la machine du pitch.
