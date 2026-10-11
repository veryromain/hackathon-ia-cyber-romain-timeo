# Rapport d'incident — garde de trésorerie Breaker

*Généré le 11/10/2026 07:37. Faits établis par le code à partir des événements de la chaîne ; synthèse rédigée par code, vérifiée (aucun montant ni hash hors des faits).*

## 1. Synthèse

5 paiement(s) ont été signalés par le garde entre le 11/10/2026 07:32:30 et le 11/10/2026 07:36:42, pour un total de 395 500 mUSD. 0 mUSD sont sortis ; 395 500 mUSD ont été protégés. 5 paiement(s) ont été annulés par les signataires. Les vérifications humaines (contact du demandeur par un autre canal, revue des accès des signataires, contestation ou confirmation des signalements) restent à documenter.

## 2. Chiffres clés

| | |
|---|---|
| Paiements signalés | 5 |
| Montant tenté | 395 500 mUSD |
| Montant sorti | 0 mUSD |
| **Montant protégé** | **395 500 mUSD** |
| Délai maximal de signalement | 35 s |

## 3. Faits

Période : du 11/10/2026 07:32:30 au 11/10/2026 07:36:42.
Paiements signalés par le garde : 5.
Montant total tenté : 395 500 mUSD. Sorti : 0 mUSD. Protégé : 395 500 mUSD.
Délai maximal entre la proposition d'un paiement et son signalement : 35 s.
- Paiement n° 1 : 95 000 mUSD vers 0xb1c1…941e, libellé « URGENT - virement confidentiel, acquisition en cours », proposé le 11/10/2026 07:32:30, 2 approbation(s), signalé « hold » 5 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 2 paiements proposés en 42 s ; premier paiement vers cette adresse ; libellé pressant ou secret (« URGENT ») ; proposé le 11/10 à 07h32 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 2 : 93 500 mUSD vers 0xb1c1…941e, libellé « Très urgent : à traiter avant ce soir, ne pas ébruiter », proposé le 11/10/2026 07:32:41, 2 approbation(s), signalé « hold » 35 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 3 paiements proposés en 53 s ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent ») ; proposé le 11/10 à 07h32 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 3 : 92 000 mUSD vers 0xb1c1…941e, libellé « Opération confidentielle validée par la direction », proposé le 11/10/2026 07:32:55, 2 approbation(s), signalé « hold » 26 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 4 paiements proposés en 67 s ; premier paiement vers cette adresse ; libellé pressant ou secret (« confidentiel ») ; proposé le 11/10 à 07h32 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 4 : 25 000 mUSD vers 0x098b…2f96, libellé « Facture fournisseur, règlement à réception », proposé le 11/10/2026 07:34:27, 3 approbation(s), signalé « hold » 0 s après (FLAGGED_ADDRESS), raisons du moteur : destinataire signalé par l'oracle (sanctions) ; 5 paiements proposés en 159 s ; premier paiement vers cette adresse ; proposé le 11/10 à 07h34 (heure de Paris). Sort : annulé (destinataire sous sanctions).
- Paiement n° 5 : 90 000 mUSD vers 0x8cb7…885e, libellé « Règlement urgent, dossier confidentiel », proposé le 11/10/2026 07:35:46, 2 approbation(s), signalé « hold » 3 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 6 paiements proposés en 238 s ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent ») ; proposé le 11/10 à 07h35 (heure de Paris). Sort : annulé (approuvé sous contrainte).
- Le 11/10/2026 07:32:47, l'oracle a inscrit l'adresse 0x0872… au registre (niveau hold).
- Le 11/10/2026 07:32:51, l'oracle a inscrit l'adresse 0x098b… au registre (niveau hold).
- Le 11/10/2026 07:32:55, l'oracle a inscrit l'adresse 0x35fb… au registre (niveau hold).
- Le 11/10/2026 07:32:58, l'oracle a inscrit l'adresse 0x3cff… au registre (niveau hold).
- Le 11/10/2026 07:33:01, l'oracle a inscrit l'adresse 0x3e37… au registre (niveau hold).
- Le 11/10/2026 07:33:04, l'oracle a inscrit l'adresse 0x53b6… au registre (niveau hold).
- Le 11/10/2026 07:33:09, l'oracle a inscrit l'adresse 0xa0e1… au registre (niveau hold).
- Le 11/10/2026 07:33:13, l'oracle a inscrit l'adresse 0xf7b3… au registre (niveau hold).
- Le 11/10/2026 07:33:37, un signataire a gelé le portefeuille (motif : « Alerte du garde, vérification en cours »).
- Le 11/10/2026 07:34:04, le portefeuille a été dégelé par plusieurs signataires.
- Le 11/10/2026 07:36:36, le portefeuille a été dégelé par plusieurs signataires.
- Signalement Web : 0x0872… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x08723392Ed15743cc38513C4925f5e6be5c17243 ».
- Signalement Web : 0x098b… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x098B716B8Aaf21512996dC57EB0615e2383E2f96 ».
- Signalement Web : 0x35fb… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x35fB6f6DB4fb05e6A4cE86f2C93691425626d4b1 ».
- Signalement Web : 0x3cff… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x3Cffd56B47B7b41c56258D9C7731ABaDc360E073 ».
- Signalement Web : 0x3e37… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x3e37627dEAA754090fBFbb8bd226c1CE66D255e9 ».
- Signalement Web : 0x53b6… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0x53b6936513e738f44FB50d2b9476730C0Ab3Bfc1 ».
- Signalement Web : 0xa0e1… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0xa0e1c89Ef1a489c9C7dE96311eD5Ce5D32c20E4B ».
- Signalement Web : 0xf7b3… (sanctions, confiance 0.97), source https://sanctionssearch.ofac.treas.gov/Details.aspx?id=27307, citation : « Digital Currency Address - ETH 0xF7B31119c2682c88d88D455dBb9d5932c65Cf1bE ».

## 4. Preuves (vérifiables sur l'explorateur de la chaîne)

| Paiement | Événement | Transaction / preuve |
|---|---|---|
| 1 | proposition | `0xe181b57d74a970b608dcc8ebd9193a1bedc7c0721ca3098968dfadeb036e6424` |
| 1 | signalement hold | `0x8e98efc65f216d7b22c40b900655ef387578857011de21dd2ec9a83b4ed3095f` |
| 1 | annulé | `0xc9bebff4b52aa786778b581517ec1199580ea4d7c805db05e5854b8106a56e9f` |
| 2 | proposition | `0x6b5dce0e8b112adc36bd0e3318a7b7eb670e609f3dd7a17fef16a12ca9b136b2` |
| 2 | signalement hold | `0x661f804c09dcfd4b50b110b84f6026149fb8bc0dd7cb7088f6b79e6ad8e0417e` |
| 2 | annulé | `0x48e470bce50a189da0f55b975ea524be2b850df28457448961fcab753578a6f7` |
| 3 | proposition | `0x231c11e388d3e923ef74b79e4a4104c83fc008f8b0fc4c658d76f383d734d4fd` |
| 3 | signalement hold | `0x15cf626a73fdc54dd44c695756229d4e94b752fb50bfaa96e2fe576aef467524` |
| 3 | annulé | `0x9c4adbe8d175b68f5bf56bf75a2810fe9440869b17d52ac5239d9da9550e17af` |
| 4 | proposition | `0xb94eae9e2b9180d0324c29a977540d0ed55a9085dae2e689026175066cea35aa` |
| 4 | signalement hold | `0xb94eae9e2b9180d0324c29a977540d0ed55a9085dae2e689026175066cea35aa` |
| 4 | annulé | `0x730b51d1adb56ebf6918f9268635f25b61cfca12c76ef25cebe81940c7da0614` |
| 5 | proposition | `0xcee0b8e5f484e1f59944acd9d1c49c28a434183e6e96755ca3ffa62be17b26e4` |
| 5 | signalement hold | `0x01aa395d8d4dc6363972ce31166ba6cc9669eea6ff0b5d9597e80e6338d4b93d` |
| 5 | annulé | `0xcaa62d26797a20ba9efb5ad343a010e10b91bc4fc8a7d073db0e99519bcb8e02` |
| — | address_flagged | `0xad5d234fc21b3e7491aa3104a1ea66cc6f36f7e028015a9f40ae14d8ccac93b7` |
| — | address_flagged | `0x209245806d2384cb716f59d9ec0319c483b33b20b33e1670b82405ac7ff8daab` |
| — | address_flagged | `0x449d32c7f87d3876966509b01d578951d691dde5f23c0c87e0ecc5800a48a3f9` |
| — | address_flagged | `0xf7f102dd1e8433b407450d8c29bf20bee3ebdf4e7734149b56544374552fe184` |
| — | address_flagged | `0x02e98f4c5d628fb78e92b8de01da8d2cd373589ade6e69973fde0ec38ddc2467` |
| — | address_flagged | `0x0da3b9fcef86c5b9585729b86b599dbc0a811162b38e222dee82b6cd8908c4e7` |
| — | address_flagged | `0xc0830078b23223a922c91f8fab07b460b75ad57d322d14a8d114b14f23f3fdbb` |
| — | address_flagged | `0x9832d64f369c0140fd423ae505eff0d53c839a8e32051275f93ca734c173989f` |
| — | wallet_frozen | `0xffe8caa1f6d4885557c61ad73d21ac5c9b78fb6c74986c74fcce4546dfce1e55` |
| — | wallet_unfrozen | `0xf9b967d2244a13fa17aa078ebf83486222a5e5f94de0f92869e42968c9fb0659` |
| — | wallet_unfrozen | `0x01a5cbd84d414e707383a5cad2c2abf30c11ff58949374f370be9b4cca4e27d2` |
| — | signalement Web 0x08723392… | preuve `0xfbc967e9ce03296c3e441365a1a562f9fbc91eb638ba1a44f6a08a449102c3a4` |
| — | signalement Web 0x098b716b… | preuve `0xb636f55f2e98f19b797c090df071c68f5c8cfd275266d30c15f257635ab8a769` |
| — | signalement Web 0x35fb6f6d… | preuve `0x17d0edfea89f147d07827aa742f672b41828aac5bbac4d32fba8ce035d22c4f0` |
| — | signalement Web 0x3cffd56b… | preuve `0x3070de2d33e2161c4bed8df03bf7b918cec2ae9db2946463e8249b77708db0cc` |
| — | signalement Web 0x3e37627d… | preuve `0xd1e65f0e61849a2230d93a0e5d8273c48fd68280b67d4716009bbbfedcef0ab1` |
| — | signalement Web 0x53b69365… | preuve `0x6cfe5d9006575d7cf77589c804dc7391f77ca8941e8b5669bde89d95cd14fcac` |
| — | signalement Web 0xa0e1c89e… | preuve `0xb9dfaea260e2f0a921991087330b7b9a4c738648b9f9eb38c000149540a6ec2a` |
| — | signalement Web 0xf7b31119… | preuve `0x8ea691984cafa8c137802d2c109d2bd036ec8a41677ab15e8bf9865e1807e648` |

## 5. Chronologie complète

| Heure | Événement | Paiement |
|---|---|---|
| 11/10/2026 07:31:48 | payment_proposed | 0 |
| 11/10/2026 07:31:48 | payment_approved | 0 |
| 11/10/2026 07:31:51 | payment_approved | 0 |
| 11/10/2026 07:32:26 | payment_executed | 0 |
| 11/10/2026 07:32:30 | payment_proposed | 1 |
| 11/10/2026 07:32:30 | payment_approved | 1 |
| 11/10/2026 07:32:34 | payment_approved | 1 |
| 11/10/2026 07:32:35 | risk_flagged | 1 |
| 11/10/2026 07:32:41 | payment_proposed | 2 |
| 11/10/2026 07:32:41 | payment_approved | 2 |
| 11/10/2026 07:32:46 | payment_approved | 2 |
| 11/10/2026 07:32:47 | address_flagged |  |
| 11/10/2026 07:32:51 | address_flagged |  |
| 11/10/2026 07:32:55 | address_flagged |  |
| 11/10/2026 07:32:55 | payment_proposed | 3 |
| 11/10/2026 07:32:55 | payment_approved | 3 |
| 11/10/2026 07:32:57 | payment_approved | 3 |
| 11/10/2026 07:32:58 | address_flagged |  |
| 11/10/2026 07:33:01 | address_flagged |  |
| 11/10/2026 07:33:04 | address_flagged |  |
| 11/10/2026 07:33:09 | address_flagged |  |
| 11/10/2026 07:33:13 | address_flagged |  |
| 11/10/2026 07:33:16 | risk_flagged | 2 |
| 11/10/2026 07:33:21 | risk_flagged | 3 |
| 11/10/2026 07:33:37 | wallet_frozen |  |
| 11/10/2026 07:33:40 | payment_cancelled | 1 |
| 11/10/2026 07:33:43 | payment_cancelled | 2 |
| 11/10/2026 07:33:48 | payment_cancelled | 3 |
| 11/10/2026 07:33:58 | unfreeze_approved |  |
| 11/10/2026 07:34:01 | unfreeze_approved |  |
| 11/10/2026 07:34:04 | unfreeze_approved |  |
| 11/10/2026 07:34:04 | wallet_unfrozen |  |
| 11/10/2026 07:34:27 | payment_proposed | 4 |
| 11/10/2026 07:34:27 | payment_approved | 4 |
| 11/10/2026 07:34:27 | risk_flagged | 4 |
| 11/10/2026 07:34:31 | payment_approved | 4 |
| 11/10/2026 07:34:34 | payment_approved | 4 |
| 11/10/2026 07:35:14 | payment_cancelled | 4 |
| 11/10/2026 07:35:46 | payment_proposed | 5 |
| 11/10/2026 07:35:46 | payment_approved | 5 |
| 11/10/2026 07:35:49 | risk_flagged | 5 |
| 11/10/2026 07:35:51 | payment_approved | 5 |
| 11/10/2026 07:36:32 | unfreeze_approved |  |
| 11/10/2026 07:36:34 | unfreeze_approved |  |
| 11/10/2026 07:36:36 | unfreeze_approved |  |
| 11/10/2026 07:36:36 | wallet_unfrozen |  |
| 11/10/2026 07:36:42 | payment_cancelled | 5 |

## 6. Suites à donner (humaines)

- [ ] Contacter le demandeur de chaque paiement signalé par un autre canal et consigner la réponse.
- [ ] Si une clé de signataire est suspectée : la remplacer, puis dégeler le portefeuille.
- [ ] Confirmer ou contester les signalements d'adresses (registre).
- [ ] Classer l'incident (impact, clients touchés) et, si l'organisation est régulée, notifier dans les délais applicables.
