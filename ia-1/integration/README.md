# Démo de bout en bout en local (jalon de la phase 2) ✅

Testée sur le Mac de Romain le 10/10 vers 18h40 : chaîne Hardhat + contrats et relais de Timéo + moteur de score (avec R2) + oracle Bedrock + tableau de bord.

## Lancer (6 terminaux, dans cet ordre)
```bash
# 1. chaîne locale
cd ia-2 && npx hardhat node
# 2. contrats + carnet d'adresses de la démo (fournisseur habituel du scénario)
cd ia-2 && npm run deploy:local && npx hardhat run ../ia-1/integration/carnet.js --network localhost
#    (repartir de fichiers vides : rm -f ../shared/events.jsonl; : > ../shared/alerts.jsonl; : > ../shared/flags.jsonl)
# 3. relais (AVANT le moteur : il réécrit shared/events.jsonl)
cd ia-2 && npm run relay:local
# 4. moteur de score en direct, avec le modèle d'anomalie
cd ia-1 && .venv/bin/python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl \
  --carnet integration/carnet-local.json --modele modeles/anomalie.joblib --suivre
# 5. tableau de bord → http://localhost:8599
cd ia-1 && .venv/bin/streamlit run dashboard/app.py --server.port 8599
# 6a. scénario de Timéo : paiement normal + fraude en rafale + réponse d'un signataire
cd ia-2 && RESPOND=1 npm run scenario:local
# 6b. Web2 → Web3 : l'oracle signale une adresse (partage de connexion pour Bedrock !), puis on tente de la payer
cd ia-1 && .venv/bin/python -m oracle.oracle oracle/corpus_demo/01-forum-arnaque.html --out ../shared/flags.jsonl
cd ia-2 && ADRESSE=0x6253540229bdcc8ae009fe075005a3fa5137c352 npx hardhat run ../ia-1/integration/scenario_oracle.js --network localhost
```

## Résultats obtenus
| Étape | Sans moteur (1er passage) | Avec moteur + oracle |
|---|---|---|
| Paiement normal au fournisseur habituel (3 150 mUSD) | exécuté | **exécuté, aucune friction** |
| Fraude en rafale : 3 virements (280 500 mUSD) vers une adresse inconnue | **95 000 mUSD partis** (seul le plafond du contrat a freiné les 2 suivants) | **0 mUSD parti** : 3 × `hold` (score 0,93) inscrits sur la chaîne **dans la seconde** (délai disponible : 30 s) |
| Adresse signalée sur le Web par l'oracle, puis paiement banal de 4 800 mUSD | — | oracle : signalée `hold` (0,95), adresse de dons rejetée ; registre on-chain mis à jour ; paiement **bloqué** par le contrat (registre) **et** par le moteur (0,98) ; **0 mUSD parti** |

## Ce que l'intégration a révélé
- **Bug corrigé :** le modèle R2 enregistré par `python -m score.anomalie` ne se rechargeait pas dans le moteur (nom de module `__main__` dans la sauvegarde). Corrigé + test de non-régression.
- `OFF_HOURS` se déclenche pendant la démo du samedi (week-end) : c'est juste, mais à expliquer au jury (ou faire la démo filmée un jour de semaine, ou régler les heures ouvrées).
- `BURST` s'ajoute au paiement vers l'adresse signalée parce qu'il suit de près la rafale du scénario : artefact de démo, sans effet sur le résultat.
- Hardhat installé sur le Mac : `npm install` a demandé des réessais (réseau lent en partage de connexion).
