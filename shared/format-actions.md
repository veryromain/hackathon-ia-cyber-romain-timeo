# Format des actions des signataires (R5b)

> Proposition de Romain (ia-1), 10/10 vers 19:50. Complète `shared/format-evenements.md` sans le modifier.
> **Timéo :** c'est ce que ton relais devra lire sur Fuji (les clés des signataires ne sont que sur ton PC). **Depuis 19:53, le relais de Timéo (`npm run relay:local` / `relay:fuji`) lit ce fichier** : ne pas lancer `ia-1/integration/actions.js` en même temps (chaque action partirait deux fois).

Le tableau de bord n'a **aucune clé**. Quand un signataire clique sur un bouton, il écrit une ligne dans `shared/actions.jsonl` ; l'exécuteur (relais) signe la transaction avec la clé de test de ce signataire et écrit le résultat dans `shared/actions-resultats.jsonl`. Le tableau de bord affiche l'état (en attente, fait, erreur). En production, le signataire signerait dans son navigateur avec son propre portefeuille : le fichier n'existe que pour la démo.

## `actions.jsonl` (écrit par le tableau de bord, lu par l'exécuteur)

```json
{"id": "act-2026-10-10T19:52:03Z-a1b2", "created_at": 1760118723, "action": "cancel", "payment_id": 4,
 "by": "0x…adresse du signataire", "reason": "Demande non confirmée par le fournisseur"}
```

| `action` | Champs | Transaction signée | Qui peut |
|---|---|---|---|
| `approve` | `payment_id`, `by` | `wallet.approve(id)` | un signataire actif |
| `cancel` | `payment_id`, `by`, `reason` | `wallet.cancel(id, reason)` | un signataire actif |
| `freeze` | `by`, `reason` | `wallet.freeze(reason)` | un signataire actif (un seul suffit) |
| `unfreeze` | `by` | `wallet.approveUnfreeze()` | il faut `threshold` signataires différents |
| `execute` | `payment_id`, `by` | `wallet.execute(id)` | un signataire actif, une fois les signatures réunies et le délai écoulé (ajouté par Timéo, 19:53) |

Un signalement d'adresse se **conteste** sans passer par ce fichier : une ligne `{"address": "0x…", "remove": true}` dans `flags.jsonl` (déjà géré par le relais, rôle oracle).

## `actions-resultats.jsonl` (écrit par l'exécuteur, lu par le tableau de bord)

```json
{"id": "act-…", "status": "done", "tx_hash": "0x…", "at": 1760118731}
{"id": "act-…", "status": "error", "error": "NotEnoughApprovals(2, 3)", "at": 1760118731}
```

Règles : l'exécuteur ne traite une ligne qu'une fois (il garde sa position dans le fichier) ; une action inconnue ou mal formée donne un `error`, jamais un arrêt ; `by` doit être un signataire connu du déploiement, sinon `error: unknown_signer` ; erreurs du contrat rendues par leur nom (`AlreadyApproved()`, `WalletFrozen()`, `NotEnoughApprovals(2, 3)`), plus `unknown_action` et `invalid_payment_id`.
