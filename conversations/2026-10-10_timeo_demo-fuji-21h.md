# Démo rejouée sur Fuji depuis le PC de Timéo (10 octobre, 21h15)

Timéo avec Claude. Demande : « lance une démo sur le testnet Fuji ».

## Ce qui a été fait

1. Lecture du journal : Romain avait arrêté son relais à 21h08, aucun relais ne tournait sur le PC. État de Fuji lu sans rien signer : non gelé, 993 700 mUSD, 12 paiements dont quatre en attente (8 à 11, démo de Romain).
2. Annonce du relais dans `JOURNAL.md`, poussée avant de démarrer (règle : un seul relais Fuji à la fois).
3. Lancement, depuis `ia-2/` et `ia-1/` :
   - relais : `npx hardhat run --no-compile scripts/relay.js --network fuji` ;
   - moteur : `python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl --carnet ../ia-2/deployments/fuji-carnet.json --services ../shared/services-connus.json --client config/client.demo-samedi.json --listes-publiques ../shared/listes-publiques.jsonl --suivre` (avec `PYTHONUTF8=1` et `.venv/Scripts/python.exe`) ;
   - tableau de bord : `streamlit run dashboard/app.py --server.port 8599 --server.address 127.0.0.1`, avec `BREAKER_DEPLOIEMENT` sur `ia-2/deployments/fuji.json` ;
   - scénario : `RESPOND=1 npx hardhat run --no-compile scripts/demo-scenario.js --network fuji`.
4. Dégel du portefeuille, arrêt du relais et du moteur, annonce « relais Fuji arrêté » dans le journal.

## Résultat

0 mUSD parti chez le fraudeur sur 280 500 tentés. Paiement normal exécuté en 43 s ; les trois paiements frauduleux mis en attente 6 s, 6 s et 5 s après leur proposition (score 0,97), bloqués à 2 signatures sur 3, puis annulés après le gel. Liens Snowtrace dans l'entrée de 21h23 du journal.

## Choix faits en route

- **Sans `--expliquer`.** Un appel d'essai à Bedrock a échoué au bout de 19 s (connexion fermée, Wi-Fi de l'école). Le moteur demande l'explication avant d'écrire l'alerte : avec 30 s de délai d'examen, il aurait signalé trop tard.
- **`--no-compile` partout.** Codex modifiait `TreasuryGuard.sol` au même moment ; l'ABI recompilée à 21h11 ajoute des éléments sans en changer, elle reste compatible avec le contrat déployé.
- **Tableau de bord limité à ce PC.** Streamlit s'ouvre par défaut sur le réseau ; ses boutons font signer le relais, donc relancé avec `--server.address 127.0.0.1`.
- **Paiements 8 à 11 laissés en attente** : ils viennent de la démo de Romain.

## À savoir

- `unfreeze.js` s'est terminé en erreur alors que le dégel était passé : il relit `frozen()` avant que le nœud ait vu le troisième vote, puis tente un quatrième vote que le contrat refuse. Non corrigé.
- Le tableau de bord tourne encore sur `http://127.0.0.1:8599`, sans relais.

## Prochaines étapes

- Corriger `unfreeze.js` si l'on rejoue souvent sur Fuji.
- Pour une démo avec explications Bedrock depuis ce PC : partage de connexion, puis ajouter `--expliquer` au moteur.
