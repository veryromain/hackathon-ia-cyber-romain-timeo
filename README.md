# Breaker - ralentir une mauvaise signature avant que les fonds sortent

Secure Horizons, 10-11 octobre 2026. Romain et Timéo. **Track 1, Fintech Security, axe 4 : détection et réponse aux incidents DeFi.**

Une trésorerie multisignature peut payer un fraudeur même lorsque son contrat fonctionne correctement : les signataires ont été trompés. Breaker analyse le paiement, explique le risque en français et donne aux signataires le temps de vérifier.

## Ce qui fonctionne dans le prototype

- Contrats Solidity sur Avalanche Fuji et Hardhat : multisignature, délai d'examen, signature supplémentaire, mise en attente, annulation, gel et probation des nouvelles clés.
- Moteur de règles et Isolation Forest sur l'historique du portefeuille.
- Agent : simulation du transfert ERC-20 par `eth_call`, analyse du dossier et avis Bedrock ; les règles imposent un risque minimal que le modèle ne peut pas diminuer.
- Oracle Web : lecture de pages, citations vérifiées, croisement des sources ; listes publiques et historique on-chain facultatifs.
- Dashboard de démonstration, explications simples, journal de preuves et rapport d'incident.
- Clé de contrainte et clé d'identité séparée pour révoquer sa propre clé volée.

**Deux modes seulement.** Protection : alerte, attente et validation humaine renforcée. Cosignataire : l'agent peut ajouter sa signature, ou refuser de signer ; le quorum humain renforcé permet une dérogation après délai. L'agent n'a pas de veto définitif. Le quorum doit être configuré de façon à rester atteignable par les humains seuls. Dans la démo : 2 signatures sur 5 normalement, 3 sur 5 sur un paiement risqué.

L'unanimité peut raccourcir l'attente d'un paiement ordinaire, mais ne supprime jamais le délai d'examen initial. **Un paiement signé sous contrainte reste inexécutable : il faut le faire annuler, résoudre l'incident et proposer un nouveau paiement.** Les changements du seuil et des signataires suivent une proposition avec délai ; le moniteur et le registre sont immuables dans ce prototype. Le retrait d'un futur Guard Safe devra suivre la même protection : ce greffon n'est pas encore implémenté.

## Architecture

```text
Avalanche Fuji / Hardhat -> relais Node -> events.jsonl
  -> moteur / agent Python -> alerts.jsonl / décisions -> relais -> TreasuryGuard
Pages Web -> oracle -> flags.jsonl -> relais -> RiskRegistry
Dashboard -> actions.jsonl -> relais de démonstration -> contrat
```

Le relais détient les clés **de test**. Le navigateur n'a pas de secret. Le moniteur ne peut que relever le risque, jamais transférer des fonds. Le contrat de démonstration détient des jetons fictifs mUSD ; l'intégration prévue dans le Safe du client reste à développer. Cela ne constitue pas une qualification juridique « hors garde » acquise.

## Installation et vérification hors chaîne

Prérequis : Python 3.12 et Node.js 20 ou 22, npm, Git. Depuis la racine :

```powershell
# Windows / PowerShell
$env:PYTHONUTF8='1'
python -m venv ia-1/.venv
ia-1/.venv/Scripts/python.exe -m pip install -r ia-1/requirements.txt
cd ia-2
npm ci
npm test
npm run zero-secret
cd ../ia-1
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe -m eval.evaluer_donnees --modele
```

Sous macOS/Linux, remplacer `.venv/Scripts/python.exe` par `.venv/bin/python` et utiliser `export PYTHONUTF8=1`. Aucun accès AWS n'est nécessaire pour les tests hors ligne. Le premier téléchargement npm/compilateur nécessite Internet. Ne charger que les modèles joblib produits par ce dépôt, jamais un fichier fourni par un inconnu.

## Démo locale de bout en bout

Utiliser un checkout de démonstration séparé : le relais réécrit les journaux de travail. Dans des terminaux distincts, avec `PYTHONUTF8=1` sous Windows :

1. `cd ia-2` puis `npm run node`.
2. Autre terminal, `cd ia-2` : `npm run deploy:local`, puis `npx hardhat run ../ia-1/integration/carnet.js --network localhost`.
3. `cd ia-2` : `npm run relay:local`. Un seul relais à la fois.
4. `cd ia-1` : `.venv/Scripts/python.exe -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl --carnet integration/carnet-local.json --suivre`. Sans Bedrock : explications de secours déterministes.
5. `cd ia-1` : `.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8599`.
6. `cd ia-2` : `npm run scenario:local`. Relire puis annuler les paiements suspects depuis le dashboard.

Pour le modèle, entraîner avec `python -m score.anomalie --events ../shared/donnees/train.events.jsonl --carnet ../shared/donnees/carnet.json --sortie modeles/anomalie.joblib`, puis ajouter `--modele modeles/anomalie.joblib` au moteur. Pour l'IA et l'agent, voir [guide d'intégration](ia-1/integration/README.md) et [agent](ia-1/agent/agent.py). Pour Fuji : [contrats, adresses et commandes](ia-2/README.md). Ne pas lancer de second relais contre le même déploiement.

## Résultats et limites

[Mesures et protocole](shared/mesures.md) : sur le jeu final synthétique de 274 paiements (40 frauduleux, 234 normaux), 95 % des fraudes freinées ou mises en attente, 78 % mises en attente, 91 % des montants frauduleux en attente et 5,1 % de faux hold. **Freiner ne prouve pas empêcher un vol.** L'attaque en rafale démontrée sur Fuji : 280 500 mUSD tentés, 0 sorti. Le temps de signalement historique de 5-6 s dépend du réseau et ne garantit pas la latence de l'agent complet avec lecture Web / LLM.

Tests hors ligne : 80 Python et 51 Solidity. [Analyse statique et invariants](shared/audit-contrat.md) : contrôles internes, pas un audit indépendant.

- Contrat non audité ; aucun fonds réel, aucun mainnet. Un bug peut entraîner des pertes ou une indisponibilité. Le jeton mUSD a 18 décimales : USDC réel en a 6 et nécessite une adaptation.
- Données synthétiques préparées par notre équipe ; aucune preuve d'efficacité chez des clients réels. La simulation du transfert n'est pas une simulation exhaustive de l'exécution du Guard ni de tous les protocoles DeFi.
- Sélecteur de signataire et file d'actions du dashboard réservés à la démo locale : aucune authentification de production. Ne jamais exposer ce dashboard ou le relais publiquement.
- La contrainte peut se déduire de la chaîne : pas de garantie d'indétectabilité pour l'agresseur.
- Oracle sensible à la qualité des sources ; texte hostile traité comme une donnée, citations et sources contrôlées. Une absence de preuve Web n'est pas une preuve d'innocuité.
- Coupure du RPC, clés indisponibles ou quorum mal configuré peuvent immobiliser des paiements. Mesurer séparément disponibilité et faux positifs avant toute utilisation réelle.

## Livrables pour le jury

[Dossier de soumission](shared/submit/README.md) : pitch relu, fiche de défense d'une page, playbook, conformité et texte du formulaire. Vidéo finale de 2-3 minutes en finalisation. Le dépôt est privé : son accès jury doit être assuré avant envoi. La vitrine commerciale est facultative et ne réalise aucun encaissement.

Les secrets restent dans `.env` et `ia-2/.env`, ignorés par Git ; seuls les exemples sans valeur réelle sont fournis. Tests et scénarios uniquement sur nos environnements, avec données synthétiques ou sources publiques. Le code central a été développé pendant le hackathon ; bibliothèques et outils tiers sont identifiés dans les dépendances.
