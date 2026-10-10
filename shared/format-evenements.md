# Format des événements et des alertes

> **Statut : proposition de Timéo (ia-2), à amender par Romain.** C'est l'interface entre le contrat et le générateur de trafic (`ia-2/`) et le moniteur (`ia-1/`). Une fois d'accord, on ne la change plus sans se prévenir dans `JOURNAL.md`.

Les ABI des contrats sont dans `shared/abi/` (régénérées par `npm run export-abi` dans `ia-2/`).

## 1. Ce que le contrat émet

### Coffre `BreakerVault`

| Événement | Arguments | Sens pour le moniteur |
|---|---|---|
| `Deposited` | `account`, `amount` | Entrée de fonds, trafic normal |
| `Withdrawn` | `account`, `amount` | Sortie de fonds d'un déposant |
| `Borrowed` | `account`, `amount`, `debtAfter` | Sortie de fonds contre collatéral. **C'est par là que passe le vidage** |
| `Repaid` | `account`, `amount`, `debtAfter` | Retour de fonds |
| `CollateralDeposited` | `account`, `token`, `amount` | Dépôt de collatéral |
| `CollateralWithdrawn` | `account`, `token`, `amount` | Retrait de collatéral |
| `CollateralProposed` | `token`, `priceSource`, `ltvBps`, `readyAt` | Nouveau collatéral proposé. À croiser avec la liquidité du pool `priceSource` |
| `CollateralListed` | `token`, `priceSource`, `ltvBps` | Collatéral accepté. **Signe précurseur** si le pool est mince ou le jeton récent |
| `ListingDelayChanged` | `previousDelay`, `newDelay` | **Signe précurseur** dès que le délai baisse |
| `RoleGranted` (OpenZeppelin) | `role`, `account`, `sender` | **Signe précurseur** si `CONFIG_ROLE` va à une adresse neuve |
| `RoleRevoked` (OpenZeppelin) | `role`, `account`, `sender` | Changement de pouvoirs |
| `GuardLevelChanged` | `previousLevel`, `newLevel`, `by`, `reason` | Trace de la réponse : 0 = Normal, 1 = Limited, 2 = Paused |

### Pool `SimplePool` (sert d'oracle de prix)

| Événement | Arguments | Sens pour le moniteur |
|---|---|---|
| `LiquidityAdded` | `provider`, `tokenAmount`, `quoteAmount` | Profondeur du pool |
| `Swapped` | `trader`, `quoteIn`, `amountIn`, `amountOut`, `priceAfter` | **Signe précurseur** : prix multiplié en quelques échanges, toujours par la même adresse |

### Lectures utiles (appels sans transaction)

- Coffre : `liquidity()`, `totalDeposits()`, `totalDebt()`, `guardLevel()`, `listingDelay()`, `borrowLimit(compte)`, `remainingOutflow()`.
- Pool : `reserveToken()`, `reserveQuote()`, `price()`.

Tous les montants sont en unités de base à 18 décimales (1 mUSD = `1000000000000000000`).

## 2. Événement normalisé (JSON)

Une ligne JSON par événement, dans l'ordre de la chaîne. Le générateur de trafic peut aussi écrire ce format dans un fichier pour rejouer une session sans chaîne.

```json
{
  "chain_id": 43113,
  "block": 41250311,
  "timestamp": 1760104800,
  "tx_hash": "0x…",
  "log_index": 2,
  "tx_from": "0x…",
  "contract": "vault",
  "address": "0x…",
  "event": "Borrowed",
  "args": { "account": "0x…", "amount": "32258064516129032258064", "debtAfter": "96774193548387096774192" }
}
```

- `contract` vaut `vault`, `pool` ou `token`.
- `tx_from` est l'adresse qui a signé la transaction (utile pour repérer une adresse neuve).
- Les entiers de `args` sont des chaînes, pour ne pas perdre de précision en JSON.
- Les fichiers de mesure ajoutent un champ `label` (`normal` ou `attack`) et un champ `scenario`. **Le moniteur ne doit jamais lire ces deux champs** : ils ne servent qu'au calcul des taux de détection.

## 3. Alerte (JSON)

```json
{
  "id": "2026-10-10T18:42:07Z-0007",
  "block": 41250311,
  "timestamp": 1760104927,
  "score": 0.93,
  "level": "paused",
  "reasons": [
    { "code": "LISTING_DELAY_LOWERED", "detail": "délai passé de 3600 s à 0 s", "tx_hashes": ["0x…"] },
    { "code": "THIN_LIQUIDITY_COLLATERAL", "detail": "pool du collatéral : 100 mUSD de réserve", "tx_hashes": ["0x…"] },
    { "code": "BORROW_BURST", "detail": "3 emprunts en 40 s, 9,7 % de la liquidité", "tx_hashes": ["0x…", "0x…", "0x…"] }
  ],
  "action": { "type": "escalate", "to": "paused", "tx_hash": "0x…" }
}
```

- `level` vaut `normal`, `limited` ou `paused`, comme `GuardLevel` dans le contrat.
- Chaque raison cite les transactions qui la prouvent : c'est ce qui alimente le rapport DORA et le journal d'audit.
- `action` est absent si l'alerte n'a déclenché aucune transaction.

## 4. Les trois temps du scénario et ce qu'ils émettent

| Temps | Transactions de l'attaquant | Événements |
|---|---|---|
| 1. Préparation | Déploie un faux jeton et un pool mince, gonfle le prix | `LiquidityAdded`, `Swapped` (sur un pool que le coffre ne connaît pas encore) |
| 2. Prise de pouvoir | Obtient `CONFIG_ROLE`, ramène le délai à zéro, liste le faux jeton | `RoleGranted`, `ListingDelayChanged`, `CollateralProposed`, `CollateralListed` |
| 3. Vidage | Dépose le faux collatéral, emprunte en N transactions | `CollateralDeposited`, puis N × `Borrowed` |

Le temps 2 se passe **avant** le premier mUSD sorti : c'est la fenêtre où une pause sauve tout. Les tests de `ia-2/test/` vérifient les deux cas (pause au listing : 100 % sauvés ; pause après 3 emprunts sur 31 : plus de 90 % sauvés).
