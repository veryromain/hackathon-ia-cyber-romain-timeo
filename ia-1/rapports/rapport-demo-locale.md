# Rapport d'incident — garde de trésorerie Breaker

*Généré le 10/10/2026 19:31. Faits établis par le code à partir des événements de la chaîne ; synthèse rédigée par us.anthropic.claude-opus-4-8, vérifiée (aucun montant ni hash hors des faits).*

## 1. Synthèse

**Ce qui s'est passé**

Le 10/10/2026, entre 18:39:15 et 18:40:36 (heure de Paris), quatre paiements ont été proposés depuis le portefeuille de trésorerie, pour un montant total tenté de 285 300 mUSD. Les trois premiers paiements (95 000 mUSD, 93 500 mUSD et 92 000 mUSD) étaient destinés à une même adresse nouvelle (0xcad6…1f3f), chacun assorti d'un libellé pressant ou confidentiel et chacun doté de 2 approbations. Le quatrième paiement (4 800 mUSD, libellé « Facture prestation octobre ») visait l'adresse 0x6253…c352, également avec 2 approbations. Le moteur a détecté un enchaînement rapide de propositions en dehors des heures ouvrées, des destinataires inédits, des libellés d'urgence, et, pour le dernier, une adresse signalée par l'oracle (scam_report, confiance 0,95). À ce jour, aucun fonds n'est sorti : 285 300 mUSD ont été protégés.

**Réaction du garde et décisions des signataires**

Le garde a signalé chaque paiement en statut « hold » dans un délai maximal d'une seconde après la proposition. Le 10/10/2026 à 18:39:59, un signataire a gelé le portefeuille au motif « Alerte du garde, vérification en cours ». À 18:40:32, l'oracle a inscrit l'adresse 0x6253… au registre (niveau hold), sur la base d'un signalement web citant une arnaque. À 18:40:36, le portefeuille a été dégelé par plusieurs signataires. Les paiements n° 1, 2 et 3 ont été annulés (fraude confirmée). Le paiement n° 4 reste en attente.

**Ce qu'il reste à faire**

Il convient de statuer sur le paiement n° 4 (4 800 mUSD vers 0x6253…), toujours en attente, en tenant compte de l'inscription de cette adresse au registre de l'oracle. Une vérification humaine des circonstances et de l'origine des quatre propositions est nécessaire, ainsi qu'un signalement selon les procédures internes et réglementaires applicables. Enfin, une revue des accès et des droits d'approbation des signataires concernés est recommandée, de même qu'une documentation des hash de transactions figurant dans le rapport détaillé.

## 2. Chiffres clés

| | |
|---|---|
| Paiements signalés | 4 |
| Montant tenté | 285 300 mUSD |
| Montant sorti | 0 mUSD |
| **Montant protégé** | **285 300 mUSD** |
| Délai maximal de signalement | 1 s |

## 3. Faits

Période : du 10/10/2026 18:39:15 au 10/10/2026 18:40:36.
Paiements signalés par le garde : 4.
Montant total tenté : 285 300 mUSD. Sorti : 0 mUSD. Protégé : 285 300 mUSD.
Délai maximal entre la proposition d'un paiement et son signalement : 1 s.
- Paiement n° 1 : 95 000 mUSD vers 0xcad6…1f3f, libellé « URGENT - virement confidentiel, acquisition en cours », proposé le 10/10/2026 18:39:15, 2 approbation(s), signalé « hold » 1 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 2 paiements proposés en 32 s ; paiement atypique pour ce portefeuille (surtout : weekend, propositions_10_min) ; premier paiement vers cette adresse ; libellé pressant ou secret (« URGENT ») ; proposé le 10/10 à 18h39 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 2 : 93 500 mUSD vers 0xcad6…1f3f, libellé « Très urgent : à traiter avant ce soir, ne pas ébruiter », proposé le 10/10/2026 18:39:19, 2 approbation(s), signalé « hold » 1 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 3 paiements proposés en 36 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent ») ; proposé le 10/10 à 18h39 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 3 : 92 000 mUSD vers 0xcad6…1f3f, libellé « Opération confidentielle validée par la direction », proposé le 10/10/2026 18:39:23, 2 approbation(s), signalé « hold » 1 s après (PAYMENT_FRAUD_PATTERN;BURST;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO;OFF_HOURS), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; 4 paiements proposés en 40 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; libellé pressant ou secret (« confidentiel ») ; proposé le 10/10 à 18h39 (heure de Paris). Sort : annulé (fraude confirmée).
- Paiement n° 4 : 4 800 mUSD vers 0x6253…c352, libellé « Facture prestation octobre », proposé le 10/10/2026 18:40:36, 2 approbation(s), signalé « hold » 0 s après (FLAGGED_ADDRESS), raisons du moteur : destinataire signalé par l'oracle (scam_report) ; 5 paiements proposés en 113 s ; paiement atypique pour ce portefeuille (surtout : propositions_10_min, weekend) ; premier paiement vers cette adresse ; proposé le 10/10 à 18h40 (heure de Paris). Sort : en attente.
- Le 10/10/2026 18:39:59, un signataire a gelé le portefeuille (motif : « Alerte du garde, vérification en cours »).
- Le 10/10/2026 18:40:32, l'oracle a inscrit l'adresse 0x6253… au registre (niveau hold).
- Le 10/10/2026 18:40:36, le portefeuille a été dégelé par plusieurs signataires.
- Signalement Web : 0x6253… (scam_report, confiance 0.95), source oracle/corpus_demo/01-forum-arnaque.html, citation : « Arnaque : l'adresse 0x6253540229bdcc8ae009fe075005a3fa5137c352 a reçu les fonds de trois victimes cette semaine, toutes contactées par un faux directeur financi ».

## 4. Preuves (vérifiables sur l'explorateur de la chaîne)

| Paiement | Événement | Transaction / preuve |
|---|---|---|
| 1 | proposition | `0x284a1fd59c57725ceb8230ac74767eecf5e578eee8e24047ff36fc35e6ffb29e` |
| 1 | signalement hold | `0x09e49423b7ef0c2ecdfea7e755d66e5a712cb1c023b5465261fc1eb69c9edd4d` |
| 1 | annulé | `0xc6d79f1b1852a377e0924cacf1ade0d155d2f4a6e50a3b32db3b9063c0c5b26b` |
| 2 | proposition | `0xfe1a1cf72ff43b9a308a91b03bb09a03be16173799c254aaca894d0b2093c385` |
| 2 | signalement hold | `0xf5e69f15f3835d61410d8522e14ff5d0daab9bba2e9f7f85a5aaab58ad99d69d` |
| 2 | annulé | `0x0d15f72692692849b6122a908dd3d4eec0d6e6df2ed6c449ba67e29186aa45e7` |
| 3 | proposition | `0x1e01abc26c6d0db0fa04462b4b48c7730c81cf1fb9b4570994db206aa17e6b24` |
| 3 | signalement hold | `0x7486da889a8252c10cf2855d885dae585028d6d60c025a126f5a8d00b78d4e18` |
| 3 | annulé | `0xf600d5ecacaa2d49422481d8d4f54b3e1733191e2efa1a2e247f73a3b276274c` |
| 4 | proposition | `0x0436ec7f24bf21e2bbd257fa61ed15972cc5183cd29dfcc24336399d0af57d93` |
| 4 | signalement hold | `0x0436ec7f24bf21e2bbd257fa61ed15972cc5183cd29dfcc24336399d0af57d93` |
| — | wallet_frozen | `0x55184a317933b074b90346b53b673a6713328fc21cbe93898e48c3ec381e5078` |
| — | address_flagged | `0x8968a086b770b61db1573a62464a0de43e80843a5c421672eed7fe88cbd2a0d9` |
| — | wallet_unfrozen | `0xc46959caecec52fb15869a76d1c271c1ae97b49ee2cfa194bb3c2fe2d3a9058a` |
| — | signalement Web 0x62535402… | preuve `0x7b66923e30f0f8f1fcd15aa8f7616541967fadb86e99b6e71120cf3aa888707e` |

## 5. Chronologie complète

| Heure | Événement | Paiement |
|---|---|---|
| 10/10/2026 18:38:43 | payment_proposed | 0 |
| 10/10/2026 18:38:43 | payment_approved | 0 |
| 10/10/2026 18:38:43 | payment_approved | 0 |
| 10/10/2026 18:39:15 | payment_executed | 0 |
| 10/10/2026 18:39:15 | payment_proposed | 1 |
| 10/10/2026 18:39:15 | payment_approved | 1 |
| 10/10/2026 18:39:15 | payment_approved | 1 |
| 10/10/2026 18:39:16 | risk_flagged | 1 |
| 10/10/2026 18:39:19 | payment_proposed | 2 |
| 10/10/2026 18:39:19 | payment_approved | 2 |
| 10/10/2026 18:39:19 | payment_approved | 2 |
| 10/10/2026 18:39:20 | risk_flagged | 2 |
| 10/10/2026 18:39:23 | payment_proposed | 3 |
| 10/10/2026 18:39:23 | payment_approved | 3 |
| 10/10/2026 18:39:23 | payment_approved | 3 |
| 10/10/2026 18:39:24 | risk_flagged | 3 |
| 10/10/2026 18:39:59 | wallet_frozen |  |
| 10/10/2026 18:39:59 | payment_cancelled | 1 |
| 10/10/2026 18:39:59 | payment_cancelled | 2 |
| 10/10/2026 18:39:59 | payment_cancelled | 3 |
| 10/10/2026 18:40:32 | address_flagged |  |
| 10/10/2026 18:40:36 | unfreeze_approved |  |
| 10/10/2026 18:40:36 | unfreeze_approved |  |
| 10/10/2026 18:40:36 | unfreeze_approved |  |
| 10/10/2026 18:40:36 | wallet_unfrozen |  |
| 10/10/2026 18:40:36 | payment_proposed | 4 |
| 10/10/2026 18:40:36 | payment_approved | 4 |
| 10/10/2026 18:40:36 | risk_flagged | 4 |
| 10/10/2026 18:40:36 | payment_approved | 4 |

## 6. Suites à donner (humaines)

- [ ] Contacter le demandeur de chaque paiement signalé par un autre canal et consigner la réponse.
- [ ] Si une clé de signataire est suspectée : la remplacer, puis dégeler le portefeuille.
- [ ] Confirmer ou contester les signalements d'adresses (registre).
- [ ] Classer l'incident (impact, clients touchés) et, si l'organisation est régulée, notifier dans les délais applicables.
