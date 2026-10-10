# Rapport d'incident — garde de trésorerie Breaker

*Généré le 10/10/2026 22:28. Faits établis par le code à partir des événements de la chaîne ; synthèse rédigée par us.anthropic.claude-opus-4-8, vérifiée (aucun montant ni hash hors des faits).*

## 1. Synthèse

**Ce qui s'est passé**

Entre le 10/10/2026 à 22:23:06 et le 10/10/2026 à 22:26:26, deux paiements ont été proposés depuis le portefeuille de trésorerie, pour un montant total tenté de 140 000 mUSD. Le premier paiement, de 80 000 mUSD vers l'adresse 0x3ae7…0720, portait le libellé « Règlement fournisseur - urgent » et comptait 2 approbations. Le second, de 60 000 mUSD vers l'adresse 0x6257…1316, portait le libellé « Règlement partenaire » et comptait également 2 approbations. Un remplacement de signataire a par ailleurs été enregistré le 10/10/2026 à 22:23:16.

**Réaction du garde et décisions des signataires**

Le garde a signalé les deux paiements, dans un délai maximal de 12 secondes après leur proposition. Le paiement n° 0 a été mis en « hold » sur la base de plusieurs motifs : nouveau destinataire avec demande pressante, paiement atypique pour ce portefeuille (weekend, libellé urgent), premier paiement vers cette adresse et libellé pressant. Il a ensuite été annulé, la clé d'Emma ayant été révoquée par elle-même au motif qu'elle était compromise. Le paiement n° 1 a fait l'objet d'une demande de vérification renforcée (« step_up ») en raison de la cadence (2 paiements en 200 s), du caractère nouveau du destinataire et du remplacement récent d'un signataire ; il demeure en attente. Au total, 0 mUSD sont sortis et 140 000 mUSD ont été protégés.

**Ce qu'il reste à faire**

Le paiement n° 1, toujours en attente, doit faire l'objet d'une vérification humaine avant toute décision, notamment concernant le destinataire 0x6257…1316 et le libellé « Règlement partenaire ». Le remplacement de signataire du 10/10/2026 à 22:23:16 et la révocation de la clé d'Emma justifient une revue complète des accès et des droits de signature. Il convient enfin de documenter l'incident pour l'auditeur et de procéder aux signalements internes appropriés, en conservant les éléments techniques (y compris les identifiants de transaction figurant dans le rapport détaillé).

## 2. Chiffres clés

| | |
|---|---|
| Paiements signalés | 2 |
| Montant tenté | 140 000 mUSD |
| Montant sorti | 0 mUSD |
| **Montant protégé** | **140 000 mUSD** |
| Délai maximal de signalement | 12 s |

## 3. Faits

Période : du 10/10/2026 22:23:06 au 10/10/2026 22:26:26.
Paiements signalés par le garde : 2.
Montant total tenté : 140 000 mUSD. Sorti : 0 mUSD. Protégé : 140 000 mUSD.
Délai maximal entre la proposition d'un paiement et son signalement : 12 s.
- Paiement n° 0 : 80 000 mUSD vers 0x3ae7…0720, libellé « Règlement fournisseur - urgent », proposé le 10/10/2026 22:23:06, 2 approbation(s), signalé « hold » 12 s après (PAYMENT_FRAUD_PATTERN;ANOMALY_MODEL;NEW_RECIPIENT;URGENCY_MEMO), raisons du moteur : nouveau destinataire avec une demande pressante ou un changement de coordonnées ; paiement atypique pour ce portefeuille (surtout : weekend, libelle_urgent) ; premier paiement vers cette adresse ; libellé pressant ou secret (« urgent »). Sort : annulé (clé d'Emma compromise, révoquée par elle-même).
- Paiement n° 1 : 60 000 mUSD vers 0x6257…1316, libellé « Règlement partenaire », proposé le 10/10/2026 22:26:26, 2 approbation(s), signalé « step_up » 12 s après (BURST;NEW_RECIPIENT;RECENT_OWNER_CHANGE), raisons du moteur : 2 paiements proposés en 200 s ; premier paiement vers cette adresse ; signataire remplacé il y a 0 h. Sort : en attente.
- Le 10/10/2026 22:23:16, un signataire a été remplacé.

## 4. Preuves (vérifiables sur l'explorateur de la chaîne)

| Paiement | Événement | Transaction / preuve |
|---|---|---|
| 0 | proposition | `0xf2a8a1865023c5d7ad6178810988dd3fa2c29e54c0d4816e5b6ee32b5c8f8de5` |
| 0 | signalement hold | `0xb32b44a22030ea3601cf4d55cb78563d8080cc224ea29102a715bccb8fceb065` |
| 0 | annulé | `0xe5f2394868402e3654f80799fc774cb391f174c07b60d06310a275353ebf52cc` |
| 1 | proposition | `0xc95c15d574a049cca740148e9bd6caf42c086ced9037561c7c79ba43c069d813` |
| 1 | signalement step_up | `0x3acdd2ed24371826f367102af7a96a92601e34890d3012c456cce80f9ecd5765` |
| — | owner_replaced | `0x4518801bddca733de0da83b75c82c9c9a88a7de15576876e7832f78d368f8a20` |

## 5. Chronologie complète

| Heure | Événement | Paiement |
|---|---|---|
| 10/10/2026 22:23:06 | payment_proposed | 0 |
| 10/10/2026 22:23:06 | payment_approved | 0 |
| 10/10/2026 22:23:10 | payment_approved | 0 |
| 10/10/2026 22:23:16 | owner_replaced |  |
| 10/10/2026 22:23:18 | risk_flagged | 0 |
| 10/10/2026 22:23:20 | payment_cancelled | 0 |
| 10/10/2026 22:26:26 | payment_proposed | 1 |
| 10/10/2026 22:26:26 | payment_approved | 1 |
| 10/10/2026 22:26:30 | payment_approved | 1 |
| 10/10/2026 22:26:38 | risk_flagged | 1 |

## 6. Suites à donner (humaines)

- [ ] Contacter le demandeur de chaque paiement signalé par un autre canal et consigner la réponse.
- [ ] Si une clé de signataire est suspectée : la remplacer, puis dégeler le portefeuille.
- [ ] Confirmer ou contester les signalements d'adresses (registre).
- [ ] Classer l'incident (impact, clients touchés) et, si l'organisation est régulée, notifier dans les délais applicables.
