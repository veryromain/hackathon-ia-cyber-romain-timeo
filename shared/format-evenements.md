# Format des fichiers échangés entre `ia-2/` et `ia-1/`

> **Version 2 (samedi 16h50), pour l'axe 2.** Elle remplace le format du coffre de prêt. Écrite par Timéo (ia-2) avec Claude ; Romain, dis dans `JOURNAL.md` ce que tu veux changer. Ensuite on ne modifie plus ce format sans se prévenir.

Quatre fichiers JSON Lines (un objet JSON par ligne, UTF-8). Des exemples complets sont dans `shared/echantillons/`.

| Fichier | Écrit par | Lu par | Contenu |
|---|---|---|---|
| `events.jsonl` | Relais de Timéo | Moteur de score de Romain | Ce qui se passe sur la chaîne, dans l'ordre |
| `alerts.jsonl` | Moteur de score de Romain | Relais de Timéo | Le verdict sur un paiement proposé |
| `flags.jsonl` | Oracle Web2 → Web3 de Romain | Relais de Timéo | Les adresses signalées sur le Web |
| `labels.jsonl` | Générateur de Timéo | Évaluation de Romain **uniquement** | La vérité : normal ou fraude |

**Le moteur de score ne lit jamais `labels.jsonl`.** Ce fichier ne sert qu'à calculer les taux de détection après coup.

Conventions communes :
- Les adresses et les hash sont en minuscules, préfixés par `0x`.
- Les montants sont des chaînes en unités de base à 18 décimales (1 mUSD = `"1000000000000000000"`), pour ne pas perdre de précision.
- Les dates sont des secondes Unix (heure du bloc pour les événements).

## 1. `events.jsonl`

```json
{"seq": 16, "chain_id": 43113, "block": 41259100, "timestamp": 1760126111,
 "tx_hash": "0x09ca…", "log_index": 0, "tx_from": "0x…",
 "contract": "wallet", "address": "0x…",
 "type": "payment_proposed",
 "data": {"payment_id": 4, "proposer": "0x…", "to": "0x…", "token": "0x…",
          "amount": "95000000000000000000000",
          "memo": "URGENT confidentiel - acquisition, ne pas en parler",
          "required_approvals": 2, "executable_after": 1760126171}}
```

Champs communs : `seq` (numéro d'ordre, croissant), `chain_id` (43113 sur Fuji, 31337 en local), `block`, `timestamp`, `tx_hash`, `log_index`, `tx_from` (qui a signé la transaction), `contract` (`wallet` ou `registry`), `address` (adresse du contrat), `type`, `data`.

| `type` | `data` | Sens |
|---|---|---|
| `payment_proposed` | `payment_id`, `proposer`, `to`, `token`, `amount`, `memo`, `required_approvals`, `executable_after` | Un signataire propose un paiement. **C'est ici que le moteur doit rendre son verdict** |
| `payment_approved` | `payment_id`, `owner`, `approvals`, `required_approvals` | Un signataire approuve |
| `risk_flagged` | `payment_id`, `level`, `reason`, `by`, `required_approvals`, `executable_after` | Un signalement est inscrit sur la chaîne. `by` dit qui l'a émis : le moniteur, le registre (`FLAGGED_ADDRESS`) ou le portefeuille lui-même (`OVER_PERIOD_CAP`) |
| `payment_executed` | `payment_id`, `to`, `token`, `amount`, `executor` | L'argent est parti |
| `payment_cancelled` | `payment_id`, `by`, `reason` | Paiement annulé par un signataire |
| `unfreeze_approved` | `owner`, `approvals`, `required_approvals` | Un signataire vote la levée du gel |
| `wallet_frozen` | `by`, `reason` | Portefeuille gelé : plus aucun paiement ne s'exécute |
| `wallet_unfrozen` | `by` | Gel levé |
| `config_proposed` | `proposal_id`, `change` (`replace_owner` ou `change_threshold`), `proposer`, `new_owner`, `previous_owner`, `new_threshold`, `required_approvals`, `executable_after` | Un signataire propose de remplacer un signataire ou de changer le seuil. **Signal fort**, surtout avant de gros paiements |
| `owner_replaced` | `previous_owner`, `new_owner`, `key_expires_at` | Le remplacement est effectif. Les approbations de l'ancienne clé ne comptent plus |
| `threshold_changed` | `previous_threshold`, `new_threshold` | Nombre de signatures requis modifié. **Signal fort s'il baisse** |
| `address_flagged` | `flagged`, `level`, `category`, `evidence_hash`, `expires_at` | L'oracle a inscrit une adresse au registre |
| `address_unflagged` | `flagged`, `by` | Signalement retiré ou contesté avec succès |

### Le délai d'examen

Les identifiants de paiement et de proposition de configuration partagent la même numérotation, qui commence à 0.

Tout paiement attend au moins `executable_after` avant de pouvoir s'exécuter (60 secondes dans la démo). **Le verdict du moteur doit arriver dans ce délai**, sinon le paiement part sans avoir été noté. C'est la mesure « délai de signalement » : `timestamp` de `risk_flagged` moins `timestamp` de `payment_proposed`.

## 2. `alerts.jsonl`

Une ligne par paiement jugé risqué. Pas de ligne, pas de signalement.

```json
{"payment_id": 4, "created_at": 1760126113, "score": 0.94, "level": "hold",
 "reasons": [
   {"code": "NEW_RECIPIENT", "detail": "adresse jamais payée", "evidence": ["0x09ca…"]},
   {"code": "AMOUNT_OUTLIER", "detail": "95 000 mUSD, 7 fois le paiement médian", "evidence": ["0x09ca…"]},
   {"code": "URGENCY_MEMO", "detail": "libellé : urgence et secret", "evidence": []}
 ],
 "explanation": "Paiement inhabituel par son montant et son destinataire…"}
```

| Champ | Valeurs | Remarque |
|---|---|---|
| `payment_id` | entier | Celui de `payment_proposed` |
| `score` | 0 à 1 | Libre côté moteur ; seul `level` agit sur la chaîne |
| `level` | `step_up` ou `hold` | Voir le tableau des niveaux ci-dessous |
| `reasons[].code` | majuscules et tirets bas | Les codes sont joints par `;` et inscrits sur la chaîne. Rester court : chaque caractère coûte du gas |
| `reasons[].evidence` | liste de `tx_hash` | Les transactions qui prouvent la raison. Sert au rapport d'incident |
| `explanation` | texte | Facultatif. Non inscrit sur la chaîne, affiché dans le tableau de bord |

| `level` | Ce que fait le portefeuille |
|---|---|
| `step_up` | Exige des signatures supplémentaires |
| `hold` | Exige des signatures supplémentaires **et** impose un délai d'attente pendant lequel un signataire peut annuler |

Un niveau ne peut que monter : après `hold`, un `step_up` sur le même paiement est ignoré.

Codes de raison proposés (Romain peut en ajouter) : `NEW_RECIPIENT`, `AMOUNT_OUTLIER`, `BURST`, `OFF_HOURS`, `STALE_APPROVAL`, `RECENT_OWNER_CHANGE`, `THRESHOLD_LOWERED`, `OVER_PERIOD_CAP`, `FLAGGED_ADDRESS`, `URGENCY_MEMO`, `ANOMALY_MODEL`.

## 3. `flags.jsonl`

Sortie de l'oracle Web2 → Web3 (section 4 bis de `PLAN.md`).

```json
{"address": "0x…", "level": "hold", "category": "scam_report", "confidence": 0.88,
 "sources_count": 2, "source_url": "https://exemple-signalements.test/fil/1842",
 "quote": "Arnaque : l'adresse 0x… a reçu les fonds de trois victimes cette semaine.",
 "evidence_hash": "0x…", "expires_at": 1762717111}
```

- Seuls `address`, `level`, `evidence_hash` et `expires_at` vont sur la chaîne. L'URL et la citation restent hors chaîne : elles coûteraient cher en gas et peuvent contenir des données personnelles.
- `evidence_hash` : SHA-256 de la chaîne `source_url + "\n" + quote`, pour qu'un auditeur vérifie que la preuve n'a pas changé.
- `level` vaut `step_up` ou `hold`, comme pour une alerte.
- Pour retirer un signalement : une ligne `{"address": "0x…", "remove": true}`.

## 4. `labels.jsonl`

```json
{"payment_id": 4, "label": "fraud", "scenario": "tricked_signers_burst"}
```

`label` vaut `normal` ou `fraud`. `scenario` nomme la variante (`payroll`, `recurring_supplier`, `new_supplier`, `tricked_signers_burst`, `stolen_key`, `slow_drip`, `threshold_lowered`…).

## 5. Les exemples de `shared/echantillons/`

`events.exemple.jsonl` raconte une petite histoire en 31 événements :
1. deux paiements normaux (salaires, fournisseur habituel) ;
2. un nouveau fournisseur légitime, signalé `step_up`, payé avec une troisième signature : **un cas où il ne faut pas bloquer** ;
3. une adresse inscrite au registre par l'oracle ;
4. une fraude : deux signataires trompés proposent trois gros paiements en moins de deux minutes vers des adresses jamais vues, dont l'adresse signalée. Chacun est mis en attente en 4 secondes, un autre signataire gèle le portefeuille puis annule tout.

Les adresses et les hash de ces exemples sont factices. `adresses.exemple.json` donne le rôle de chaque adresse.
