# 2026-10-11 — Romain — Vérification « zéro secret » sur le Mac (L8)

## Ce qui a été fait
- Lancement de `cd ia-2 && npm run zero-secret` sur le Mac de Romain, comme demandé par Timéo dans le journal du 07:38.
- Premier passage : code de sortie 1, un seul point signalé, `AWS_PROFILE` (valeur `hackathon`, nom de profil AWS local). Le script considère comme secret toute valeur de `.env` de 8 caractères ou plus qui ne ressemble pas à une URL, un e-mail, une région ou un nombre. Le mot « hackathon » apparaît dans 29 fichiers et 33 commits : faux positif évident.
- Correction dans `ia-2/scripts/zero-secret.js` : ajout de `NOT_SECRET_NAME`, liste de noms de variables qui ne sont jamais des secrets (`AWS_PROFILE`, `AWS_DEFAULT_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`, `NODE_ENV`, `LOG_LEVEL`, `HARDHAT_NETWORK`).
- Second passage : code de sortie 0, « ✅ Zéro secret ». 262 fichiers suivis, 163 commits toutes branches. `FUJI_MNEMONIC` cherché en entier, par 10 morceaux et via les clés privées dérivées : 0 occurrence. Motifs génériques : aucun.

## Couverture
- `.env` racine du Mac : `AWS_PROFILE`, `AWS_REGION`, `BEDROCK_MODEL_ID`. Aucune valeur secrète (Bedrock passe par le profil AWS du Mac).
- `ia-2/.env` : `FUJI_RPC_URL`, `FUJI_MNEMONIC`.
- Les deux `.env` sont bien ignorés par Git ; seuls les `.env.example` sont suivis.

## Mises à jour
- `SUIVI.md` : L8 passe à « vérifié sur le Mac », reste la relance finale et l'accès du jury.
- `JOURNAL.md` : entrée 08:05.
- `shared/verification-zero-secret.md` : étape 1 de la liste « avant de donner l'accès au jury » cochée.

## Prochaines étapes
- Relancer `npm run zero-secret` après le dernier commit, juste avant midi.
- Décider à deux : inviter le jury en lecture sur le dépôt privé ou rendre le dépôt public (et dans ce cas activer Secret scanning + Push protection côté GitHub, action réservée à Romain).
