# Vitrine Breaker : traitement des trois points

11 octobre 2026 — Codex, demande de Tim : traiter les points de l'audit zéro-secret.

## 1. Paquet minimal

La vitrine actuelle du dossier équipe a été copiée dans le checkout du site existant. Le répertoire servi `dist/` contient exactement `index.html`, `app.js` et `style.css`. Un contrôle à liste fermée refuse tout fichier supplémentaire, lien symbolique ou motif de secret identifié. Les fichiers de configuration, journaux et scripts de contrôle restent hors du répertoire servi.

Correction de la recommandation initiale : le packager natif Sites impose `.openai/hosting.json` dans l'archive comme métadonnée de déploiement. Il faut le conserver, sans aucun secret. Le contrôle vérifie ses deux seuls champs autorisés (`project_id`, `static`) et l'absence de sa représentation dans les réponses HTTP. Il n'est pas présent dans le `dist/` des sources.

## 2. Paquet et production contrôlés

La version actuelle est publiée sur https://breaker-treasury.espace-de-tr-0859.chatgpt.site, avec son audience propriétaire conservée. Les sources et l'archive ont été vérifiées contre 318 variantes des secrets locaux, y compris 20 clés privées Fuji dérivées : aucune détection.

Le contrôle utilise le jeton de service Sites uniquement en mémoire, via un en-tête envoyé à cette seule origine, sans suivre de redirection. Les réponses ne sont pas enregistrées ; seuls statuts, empreintes et conclusions sont conservés.

- `/app.js` et `/style.css` : HTTP 200 et identité octet pour octet avec les fichiers contrôlés.
- `/` : HTML conforme aux sources après retrait du seul script de détection Cloudflare identifié. Cet ajout d'infrastructure varie selon la requête ; il est distingué des octets du site. Tout autre écart échoue.
- `/.openai/hosting.json`, `/.env`, `/.git/config`, `/scripts/verify-static.py`, `/README.md` : HTTP 200 avec la page d'accueil de repli, identique après normalisation Cloudflare. Les fichiers demandés ne sont pas exposés par ces réponses.

Le statut 200 d'un chemin sensible ne constitue donc pas ici une fuite ; exiger uniquement 404 aurait produit un faux échec. Le contrôle valide le contenu réellement retourné et recherche les secrets dans toutes les réponses.

Preuves : `site-publication-validation.json` et `site-production-validation.json`. Contrôle reproductible : `sites/breaker/scripts/verify-static.py` dans le checkout Sites, copie dans `ia-2/site-vitrine/scripts/` côté équipe.

## 3. Secrets exclusivement hors navigateur

Aucune clé d'API ou de signature n'a été ajoutée à la vitrine. Aucun besoin de transférer les identifiants des moteurs vers l'hébergeur : le site reste statique. Le contrôle refuse l'ajout d'appels réseau, de stockage navigateur ou de variables d'environnement au JS sans révision explicite. Le `.gitignore` du checkout exclut les fichiers d'environnement et de clés.

Le README fixe la frontière pour les développements futurs : appels AWS/Bedrock/Apify via un serveur authentifié et autorisé, clés de cosignature dans le service de signature, jamais dans le HTML/JS ou des variables de build publiques. Cette consigne et le contrôle de publication protègent la vitrine actuelle ; ils ne constituent pas une implémentation anticipée d'un serveur ou du cosignataire futur.

Les polices Google et le script Cloudflare sont des communications d'infrastructure externes ; aucune fuite des clés applicatives n'a été identifiée. Le scan reste limité aux secrets connus et aux motifs/encodages recherchés.
