# Rapport d'incident — garde de trésorerie Breaker

*Généré le 10/10/2026 21:08. Faits établis par le code à partir des événements de la chaîne ; synthèse rédigée par us.anthropic.claude-opus-4-8, vérifiée (aucun montant ni hash hors des faits).*

## 1. Synthèse

**Synthèse de l'incident de sécurité**

**1. Ce qui s'est passé.** Entre le 10/10/2026 19:31:00 et le 10/10/2026 21:07:22, le garde a signalé 10 paiements pour un montant total tenté de 577 600 mUSD. Aucun fonds n'est sorti (0 mUSD sorti ; 577 600 mUSD protégés). Deux salves de trois virements de montants élevés (95 000, 93 500 et 92 000 mUSD) ont été proposées vers deux nouvelles adresses distinctes (0xcd96…14e1 puis 0x908c…54b5), avec des libellés pressants ou confidentiels (« URGENT », « ne pas ébruiter », « Opération confidentielle validée par la direction ») ; ces six paiements ont été annulés (fraude confirmée). Quatre autres paiements de montants plus faibles (4 800, 4 800, 2 000 et 5 000 mUSD) restent en attente : l'un vers une adresse signalée par l'oracle au titre de sanctions (0x0330…), un autre vers une adresse ayant reçu 26 % des fonds sortis de l'adresse signalée 0x2e1d…, et deux vers de nouveaux destinataires. Le délai maximal entre proposition et signalement a été de 15 s.

**2. Réaction du garde et décisions des signataires.** Le garde a détecté chaque paiement en 15 s au plus (plusieurs en quelques secondes), en s'appuyant sur des motifs tels que salve de propositions, nouveau destinataire, libellé pressant, horaires inhabituels, adresse signalée (sanctions) et fonds entachés. Un signataire a gelé le portefeuille le 10/10/2026 à 19:32:10, puis le portefeuille a été dégelé par plusieurs signataires à 19:33:56 ; un second gel est intervenu à 21:04:25, suivi d'un dégel par plusieurs signataires à 21:05:20. Sur la période, l'oracle a inscrit au registre (niveau hold) les adresses 0x0330… (21:01:50), 0x0000… (21:02:01) et 0x2e1d… (21:06:50). Les six paiements des deux salves ont été annulés ; les quatre paiements restants demeurent en attente.

**3. Ce qu'il reste à faire.** Il convient de procéder à une vérification humaine des quatre paiements en attente avant toute décision, en particulier ceux liés à l'adresse sous sanctions (0x0330…, confiance 0.98, source OFAC/SDN citée d

## 2. Chiffres clés

| | |
|---|---|
| Paiements signalés | 10 |
| Montant tenté | 577 600 mUSD |
| Montant sorti | 0 mUSD |
| **Montant protégé** | **577 600 mUSD** |
| Délai maximal de signalement | 15 s |

## 3. Faits

Période : du 10/10/2026 19:31:00 au 10/10/2026 21:07:22.
Paiements signalés par le garde : 10.
Montant total tenté : 577 600 mUSD. Sorti : 0 mUSD. Protégé : 577 600 mUSD.
Délai maximal entre la proposition d'un paiement et son signalement : 15 s.
- Paiement n° 1 : 95 000 mUSD vers 0xcd96…14e1, libellé « URGENT - virement confidentiel, acquisition en cours », proposé le 10/10/2026 19:31:00, 2 approbation(s), signalé « hold » 6 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 2 paiements proposés en 44 s ; paiement atypique pour ce portefeuille (surtout : weekend, propositions_10_min) ; premier paiement vers cette adresse ; libellé pressant ou secret (« URGENT »). Sort : annulé (fraude confirmée).
- Paiement n° 2 : 93 500 mUSD vers 0xcd96…14e1, libellé « Très urgent : à traiter avant ce soir, ne pas ébruiter », proposé le 10/10/2026 19:31:14, 2 approbation(s), signalé « hold » 5 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 3 paiements proposés en 58 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent »). Sort : annulé (fraude confirmée).
- Paiement n° 3 : 92 000 mUSD vers 0xcd96…14e1, libellé « Opération confidentielle validée par la direction », proposé le 10/10/2026 19:31:26, 2 approbation(s), signalé « hold » 6 s après (PAYMENT_FRAUD_PATTERN;BURST;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 4 paiements proposés en 70 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« confidentiel »). Sort : annulé (fraude confirmée).
- Paiement n° 5 : 95 000 mUSD vers 0x908c…54b5, libellé « URGENT - virement confidentiel, acquisition en cours », proposé le 10/10/2026 21:02:56, 2 approbation(s), signalé « hold » 14 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 2 paiements proposés en 47 s ; paiement atypique pour ce portefeuille (surtout : weekend, propositions_10_min) ; premier paiement vers cette adresse ; libellé pressant ou secret (« URGENT »). Sort : annulé (fraude confirmée).
- Paiement n° 6 : 93 500 mUSD vers 0x908c…54b5, libellé « Très urgent : à traiter avant ce soir, ne pas ébruiter », proposé le 10/10/2026 21:03:11, 2 approbation(s), signalé « hold » 13 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 3 paiements proposés en 62 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent »). Sort : annulé (fraude confirmée).
- Paiement n° 7 : 92 000 mUSD vers 0x908c…54b5, libellé « Opération confidentielle validée par la direction », proposé le 10/10/2026 21:03:26, 2 approbation(s), signalé « hold » 12 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 4 paiements proposés en 77 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« confidentiel »). Sort : annulé (fraude confirmée).
- Paiement n° 8 : 4 800 mUSD vers 0x0330…e54a, libellé « Facture prestation octobre », proposé le 10/10/2026 21:05:25, 2 approbation(s), signalé « hold » 0 s après (FLAGGED_ADDRESS), raisons du moteur : destinataire signalé par l'oracle (sanctions) ; 5 paiements proposés en 196 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse. Sort : en attente.
- Paiement n° 9 : 4 800 mUSD vers 0x933d…3c37, libellé « Facture prestataire Atlas Conseil », proposé le 10/10/2026 21:07:04, 2 approbation(s), signalé « hold » 11 s après (TAINTED_FUNDS;BURST;ANOMALY_MODEL;NEW_RECIPIENT), raisons du moteur : a reçu 26% des fonds sortis de l'adresse signalée 0x2e1d… il y a 0 h ; 6 paiements proposés en 295 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse. Sort : en attente.
- Paiement n° 10 : 2 000 mUSD vers 0xad67…f1c8, libellé « Facture traduction de la documentation », proposé le 10/10/2026 21:07:11, 2 approbation(s), signalé « hold » 15 s après (BURST;ANOMALY_MODEL;NEW_RECIPIENT), raisons du moteur : 7 paiements proposés en 302 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse. Sort : en attente.
- Paiement n° 11 : 5 000 mUSD vers 0xd0bf…d2c0, libellé « Conversion de trésorerie sur la plateforme d'échange », proposé le 10/10/2026 21:07:22, 2 approbation(s), signalé « hold » 12 s après (BURST;ANOMALY_MODEL;NEW_RECIPIENT), raisons du moteur : 8 paiements proposés en 313 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse. Sort : en attente.
- Le 10/10/2026 19:32:10, un signataire a gelé le portefeuille (motif : « Alerte du garde, vérification en cours »).
- Le 10/10/2026 19:33:56, le portefeuille a été dégelé par plusieurs signataires.
- Le 10/10/2026 21:01:50, l'oracle a inscrit l'adresse 0x0330… au registre (niveau hold).
- Le 10/10/2026 21:02:01, l'oracle a inscrit l'adresse 0x0000… au registre (niveau hold).
- Le 10/10/2026 21:04:25, un signataire a gelé le portefeuille (motif : « Alerte du garde, vérification en cours »).
- Le 10/10/2026 21:05:20, le portefeuille a été dégelé par plusieurs signataires.
- Le 10/10/2026 21:06:50, l'oracle a inscrit l'adresse 0x2e1d… au registre (niveau hold).
- Signalement Web : 0x0330… (sanctions, confiance 0.98), source https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/lists/sanctioned_addresses_ETH.txt, citation : « Adresse figurant sur la liste SDN de l'OFAC (sanctions), extraction publique du dépôt 0xB10C. ».
- Signalement Web : 0x0000… (phishing, confiance 0.9), source https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/address.json, citation : « Adresse figurant dans la base publique d'adresses de phishing de ScamSniffer. ».

## 4. Preuves (vérifiables sur l'explorateur de la chaîne)

| Paiement | Événement | Transaction / preuve |
|---|---|---|
| 1 | proposition | `0xc10d4c72af80c11696a5ec795889b261da8a77cc7b4fc24c1fa218a32f4f6555` |
| 1 | signalement hold | `0x396d108192305d1c9da8a0adbf2975c76821c46585cbf158084bcf4941a30ef1` |
| 1 | annulé | `0x7d418a0eff68c81a77465ee7657f76030f0b482bd9302f881496a3caf226b285` |
| 2 | proposition | `0xdbc7c16e8e0416ba2c26aee7d38243f0e7be6cccfceecb2e5150aca893b42a31` |
| 2 | signalement hold | `0x6b79fc2689a88fc31ff929b7ba4b07780199c73f89d918d8d8ff68b7644dc9bd` |
| 2 | annulé | `0xe268a7b1c8b119e7616187ffcbb8ce927fc03fb71718ce123130ad9a504784d6` |
| 3 | proposition | `0xca8aa79934df175a9752524de00d6a35a018ca5f4f5a365abcb22fbdb11a27c5` |
| 3 | signalement hold | `0x6b03e5bbcae8409a0d27421c4c13e06de0106f88742aa86b77c68498de2e59fd` |
| 3 | annulé | `0x8e6ed6aadf10e5156cc3a2e3e8650ce6a8e73d34dbcf2e86e0337ce3cf546a62` |
| 5 | proposition | `0xafc7ab36d86fc566657f3f7eeb8951e656e82490cc92175781b204845ebe2e6b` |
| 5 | signalement hold | `0x9c53b49e305266c64e0f09646b1c20a3056e63d0cd3e9cea8269aa07b184513f` |
| 5 | annulé | `0xa57fc3b1f58c755e2ccd01d2ca20b7ad6f35a22243dfe8815042f0c0f682c603` |
| 6 | proposition | `0x1e51ad797e290bff778019cc9bf6748cfe7172c805fb3b73cd8e1a79459a4250` |
| 6 | signalement hold | `0x4d470f51b120aa4bc90a78667e4fdbcb35d6d2f0341a31c9c9057cf15019206b` |
| 6 | annulé | `0xc4968fd61822f15fc78fcfb5e6bbde15ac7725dcd8f506c5a07ce6d5d1b1963c` |
| 7 | proposition | `0xec5bed5501311406e9334ea99df4ef8e8cd71947f8a854143ce210c60f0aec47` |
| 7 | signalement hold | `0x5475b9515e4cb85b5f7ba3944ce0a582459c1dd11231e3828a603a229bca831d` |
| 7 | annulé | `0x38df733c417944d8bece45b8117316f641b181945b93f39b094e099cfe713e8d` |
| 8 | proposition | `0x4353b39ce5ccfa21539e87f338b30f1f75fa7d60a387914a28d8c5d828d12b45` |
| 8 | signalement hold | `0x4353b39ce5ccfa21539e87f338b30f1f75fa7d60a387914a28d8c5d828d12b45` |
| 9 | proposition | `0xe40de5a777917855fb208566277e9adb3cc92ac256034c6569e07685f068ccc8` |
| 9 | signalement hold | `0x88991efafc8c453fe6a646f8c071bf555c1dbcfc7e5b28489e78d3bd014e21d9` |
| 10 | proposition | `0x6a811c4de4a0f9f4af27ff3e8390b3fda11df8f90a4eee63e65e1743e6a0e2aa` |
| 10 | signalement hold | `0x17f1d656425f88b815f0e8cb4149aef0d8826a750bb3c520492afcd84908ce6e` |
| 11 | proposition | `0x6a16e1a936cac100db791a98fbbeab195e45afc93fdb41e5e8045fd39a1f1f73` |
| 11 | signalement hold | `0x02fc748c0092fd83ce571033a6f1d8c5781765fabc4b7a1614cedbe732654457` |
| — | wallet_frozen | `0xadc503aceb8de75877481fccaf0f1ed312b5c2f726e005912fc65f4a7d5c857b` |
| — | wallet_unfrozen | `0x2fd0656647257732f1225f136d6fbc54d3b54aa6cf13bbe4e014f0f35843eb97` |
| — | address_flagged | `0x97357f67f11459cab8d918c70f9efde01d2cb3f153f6007499fcbdd0d7a35bff` |
| — | address_flagged | `0x409c7a82a751283168487dc28378c015388838e14bf268eb3859d438a91967d7` |
| — | wallet_frozen | `0x47f7d6f24d7c2b407b62285f2e7fc1d64ef0ec5c2e2a021adbe547cfcb1b3a42` |
| — | wallet_unfrozen | `0x1d6654b9afbc521d38e18fa0513d1114ba12b8a672d05240d6da700361961f87` |
| — | address_flagged | `0x0f2f7fd0150ad79b1a9aad61a26e971752c73b23bff01b1b6be0c5dba00ad848` |
| — | signalement Web 0x0330070f… | preuve `0xf34a740b751534abd3f665664ba7acfdde98aee80cfc3f032cdf851f56653e0a` |
| — | signalement Web 0x00000000… | preuve `0xb8798f4ed9471119dcaf12bff1a36ece0fe8a39030b35e8ec8aa665ef991a6e5` |

## 5. Chronologie complète

| Heure | Événement | Paiement |
|---|---|---|
| 10/10/2026 19:30:16 | payment_proposed | 0 |
| 10/10/2026 19:30:16 | payment_approved | 0 |
| 10/10/2026 19:30:21 | payment_approved | 0 |
| 10/10/2026 19:30:56 | payment_executed | 0 |
| 10/10/2026 19:31:00 | payment_proposed | 1 |
| 10/10/2026 19:31:00 | payment_approved | 1 |
| 10/10/2026 19:31:04 | payment_approved | 1 |
| 10/10/2026 19:31:06 | risk_flagged | 1 |
| 10/10/2026 19:31:14 | payment_proposed | 2 |
| 10/10/2026 19:31:14 | payment_approved | 2 |
| 10/10/2026 19:31:16 | payment_approved | 2 |
| 10/10/2026 19:31:19 | risk_flagged | 2 |
| 10/10/2026 19:31:26 | payment_proposed | 3 |
| 10/10/2026 19:31:26 | payment_approved | 3 |
| 10/10/2026 19:31:31 | payment_approved | 3 |
| 10/10/2026 19:31:32 | risk_flagged | 3 |
| 10/10/2026 19:32:10 | wallet_frozen |  |
| 10/10/2026 19:32:12 | payment_cancelled | 1 |
| 10/10/2026 19:32:14 | payment_cancelled | 2 |
| 10/10/2026 19:32:20 | payment_cancelled | 3 |
| 10/10/2026 19:33:49 | unfreeze_approved |  |
| 10/10/2026 19:33:51 | unfreeze_approved |  |
| 10/10/2026 19:33:56 | unfreeze_approved |  |
| 10/10/2026 19:33:56 | wallet_unfrozen |  |
| 10/10/2026 21:01:50 | address_flagged |  |
| 10/10/2026 21:02:01 | address_flagged |  |
| 10/10/2026 21:02:09 | payment_proposed | 4 |
| 10/10/2026 21:02:09 | payment_approved | 4 |
| 10/10/2026 21:02:13 | payment_approved | 4 |
| 10/10/2026 21:02:52 | payment_executed | 4 |
| 10/10/2026 21:02:56 | payment_proposed | 5 |
| 10/10/2026 21:02:56 | payment_approved | 5 |
| 10/10/2026 21:02:56 | risk_flagged | 5 |
| 10/10/2026 21:03:02 | payment_approved | 5 |
| 10/10/2026 21:03:10 | risk_flagged | 5 |
| 10/10/2026 21:03:11 | payment_proposed | 6 |
| 10/10/2026 21:03:11 | payment_approved | 6 |
| 10/10/2026 21:03:15 | payment_approved | 6 |
| 10/10/2026 21:03:24 | risk_flagged | 6 |
| 10/10/2026 21:03:26 | payment_proposed | 7 |
| 10/10/2026 21:03:26 | payment_approved | 7 |
| 10/10/2026 21:03:31 | payment_approved | 7 |
| 10/10/2026 21:03:38 | risk_flagged | 7 |
| 10/10/2026 21:04:25 | wallet_frozen |  |
| 10/10/2026 21:04:31 | payment_cancelled | 5 |
| 10/10/2026 21:04:38 | payment_cancelled | 6 |
| 10/10/2026 21:04:42 | payment_cancelled | 7 |
| 10/10/2026 21:05:12 | unfreeze_approved |  |
| 10/10/2026 21:05:17 | unfreeze_approved |  |
| 10/10/2026 21:05:20 | unfreeze_approved |  |
| 10/10/2026 21:05:20 | wallet_unfrozen |  |
| 10/10/2026 21:05:25 | payment_proposed | 8 |
| 10/10/2026 21:05:25 | payment_approved | 8 |
| 10/10/2026 21:05:25 | risk_flagged | 8 |
| 10/10/2026 21:05:43 | payment_approved | 8 |
| 10/10/2026 21:06:50 | address_flagged |  |
| 10/10/2026 21:06:31 | token_transfer |  |
| 10/10/2026 21:06:34 | token_transfer |  |
| 10/10/2026 21:06:38 | token_transfer |  |
| 10/10/2026 21:06:43 | token_transfer |  |
| 10/10/2026 21:06:46 | token_transfer |  |
| 10/10/2026 21:07:04 | payment_proposed | 9 |
| 10/10/2026 21:07:04 | payment_approved | 9 |
| 10/10/2026 21:07:07 | payment_approved | 9 |
| 10/10/2026 21:07:11 | payment_proposed | 10 |
| 10/10/2026 21:07:11 | payment_approved | 10 |
| 10/10/2026 21:07:15 | risk_flagged | 9 |
| 10/10/2026 21:07:16 | payment_approved | 10 |
| 10/10/2026 21:07:22 | payment_proposed | 11 |
| 10/10/2026 21:07:22 | payment_approved | 11 |
| 10/10/2026 21:07:26 | payment_approved | 11 |
| 10/10/2026 21:07:26 | risk_flagged | 10 |
| 10/10/2026 21:07:34 | risk_flagged | 11 |

## 6. Suites à donner (humaines)

- [ ] Contacter le demandeur de chaque paiement signalé par un autre canal et consigner la réponse.
- [ ] Si une clé de signataire est suspectée : la remplacer, puis dégeler le portefeuille.
- [ ] Confirmer ou contester les signalements d'adresses (registre).
- [ ] Classer l'incident (impact, clients touchés) et, si l'organisation est régulée, notifier dans les délais applicables.
