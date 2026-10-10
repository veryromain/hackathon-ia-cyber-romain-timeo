# 2026-10-10 — Romain : rejouer la démo complète sur Fuji depuis le Mac

## Demande
Le Claude de Timéo a listé, dans son entrée de 19:57, « rejouer la démo complète sur Fuji avec ton tableau de bord (actions et traçage) ». Romain veut la rejouer **depuis sa propre console et son tableau de bord**, sur le Mac.

## Ce qui a été vérifié (20:05 → 20:20)
- **Le Mac lit Fuji sans clé** : nouveau script `ia-1/integration/etat-fuji.js` (lecture seule). État à 20:16 : portefeuille non gelé, 996 850 mUSD, 4 paiements (le normal exécuté, les 3 frauduleux annulés), 0,25 AVAX au déployeur, 0,035 AVAX par compte.
- **Rien ne peut être signé depuis le Mac** : `ia-2/.env` n'existait pas, donc pas de `FUJI_MNEMONIC`. Le relais de Timéo exige dès le démarrage les clés du moniteur et de l'oracle (`signerOf` lève une erreur sinon). Scénario, oracle, actions du tableau de bord et traçage passent tous par le relais.
- Bedrock joignable depuis le Mac, identifiants AWS valides, modèle R2 présent, 43 tests `ia-1` au vert.
- Le tableau de bord choisit `localhost.json` avant `fuji.json` quand les deux existent : sur le Mac, lancer avec `BREAKER_DEPLOIEMENT=…/fuji.json`.
- Une autre session travaille en parallèle sur R9 (moteur, tests, bouton « Exécuter » du tableau de bord) : non touché.

## Ce qui a été fait
- `ia-2/.env` créé sur le Mac depuis `.env.example` (phrase vide ; fichier ignoré par Git).
- `ia-1/integration/etat-fuji.js` : état du déploiement Fuji sans clé.
- `ia-1/integration/README.md` : section « Rejouer la démo complète sur Fuji depuis le Mac » (relais, moteur avec R2 + Bedrock + services, tableau de bord, scénario sans `RESPOND=1` pour que le signataire agisse depuis les boutons, oracle, traçage, rapport).

## Décision à prendre (Romain + Timéo)
**Comment donner au Mac le droit de signer sur Fuji ?**
1. **Recommandé :** Timéo tape la phrase de test directement dans `ia-2/.env` sur le Mac (même salle, rien ne circule). Mêmes contrats, mêmes liens Snowtrace, démo complète avec R2 et Bedrock en 2 minutes.
2. Sinon : phrase neuve sur le Mac + 0,1 AVAX envoyés par Timéo + redéploiement (adresses à changer dans `ia-2/README.md` et `shared/mesures.md`).
3. Sinon : la démo reste sur le PC de Timéo (règles seules, sans R2), avec le tableau de bord de Romain qui y tourne aussi.

## Prochaine étape
Dès que la phrase est dans `ia-2/.env` : dérouler la section Fuji du README, puis mettre à jour `shared/mesures.md` et `ia-2/README.md` avec les nouveaux liens.
