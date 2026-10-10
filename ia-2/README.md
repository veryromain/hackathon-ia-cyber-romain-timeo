# ia-2 : contrats, trafic et attaques simulées

Partie de Timéo dans le projet « Breaker » (voir `PLAN.md`) : le coffre surveillé, son disjoncteur, et de quoi produire du trafic normal et des attaques pour mesurer le moniteur de `ia-1/`.

## État

| Brique | État |
|---|---|
| Contrat `BreakerVault` (coffre de prêt, disjoncteur à trois niveaux, rôles séparés) | Écrit, 13 tests passent sur la chaîne locale |
| `SimplePool` (pool d'échange minimal, sert d'oracle de prix) et `MockToken` | Écrits, testés |
| Scénario d'attaque inspiré de Drift | Rejoué dans les tests ; pas encore de script autonome |
| Générateur de trafic normal | À faire |
| Déploiement sur Avalanche Fuji | À faire (portefeuilles de test et faucet) |

## Le coffre en bref

- Les déposants apportent du mUSD (faux dollar de test) ; les emprunteurs le sortent contre un collatéral listé, dans la limite d'un ratio.
- Le prix d'un collatéral est lu sur un pool d'échange. Avec un pool mince, ce prix se manipule : c'est la faiblesse rejouée.
- Trois niveaux de garde : `Normal`, `Limited` (sorties plafonnées par fenêtre de temps), `Paused`.
- Quatre rôles séparés :
  - `DEFAULT_ADMIN_ROLE` distribue les rôles ;
  - `CONFIG_ROLE` liste les collatéraux, après un délai de sécurité ;
  - `GUARDIAN_ROLE` (le moniteur) ne peut que durcir le niveau de garde ;
  - `RESUME_ROLE` (un humain) est le seul à pouvoir relancer.
- Aucun rôle ne peut déplacer les fonds des déposants.

## Le scénario d'attaque

1. L'attaquant crée un faux jeton et un pool de 1 000 jetons contre 10 mUSD, puis achète pour 90 mUSD : le prix passe de 0,01 à 1 mUSD.
2. Il obtient `CONFIG_ROLE` (signataire trompé), ramène le délai de sécurité à zéro et liste son jeton.
3. Il dépose 4 000 000 de faux jetons et vide le coffre en 31 emprunts.

Résultats des tests : sans disjoncteur, le coffre est vidé ; avec une pause après le troisième emprunt, plus de 90 % des fonds restent ; avec une pause au listing, rien ne sort.

## Installation et tests

Il faut Node.js 20 ou plus récent.

```bash
cd ia-2
npm install
npm test            # compile et lance les 13 tests sur la chaîne locale de Hardhat
npm run export-abi  # régénère shared/abi/*.json pour le moniteur
```

Pour Fuji, copier `.env.example` en `.env` et y mettre les clés de portefeuilles **de test**. `.env` est ignoré par Git.

## Limites connues

- Prototype non audité. Pas d'intérêts, pas de liquidations, jetons à 18 décimales seulement.
- Le délai de sécurité se modifie sans délai : c'est la faiblesse voulue du scénario.
- Si l'attaquant obtient aussi `DEFAULT_ADMIN_ROLE`, il peut s'accorder `RESUME_ROLE` et lever la pause. Le disjoncteur suppose que la clé de relance est tenue à part.
- Une attaque qui tient en une seule transaction passe avant toute réaction du moniteur.
