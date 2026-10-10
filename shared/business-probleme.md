# B2 — Le problème est-il réel ? Faits chiffrés et sourcés

> Romain (avec Claude), 11/10 vers 00:25. **Brouillon** : les chiffres ci-dessous viennent d'articles secondaires relus le 11/10 ; **à vérifier dans les rapports primaires** (Chainalysis 2026 Crypto Crime Report, CertiK / TRM H1 2026) avant de les mettre sur une slide. Les chiffres conflictuels sont signalés.

## Les 5 faits pour la slide « pourquoi ce problème »
1. **Bybit, 21 février 2025, ≈ 1,46 Md$** : le plus gros vol de l'histoire. Trois signataires sur six ont validé une transaction que leur interface leur montrait falsifiée (signature en aveugle), après compromission d'un poste de la chaîne de signature. Attribué à Lazarus (Corée du Nord). *(Déjà vérifié par Timéo le 10/10.)*
2. **Drift, 1er avril 2026, ≈ 280 à 285 M$** : compromission progressive des clés d'administration et du multisig ; les attaquants ont construit de fausses identités pendant des mois, rencontré des contributeurs en personne, déposé 1 M$ pour se rendre crédibles, puis vidé en 31 retraits et 12 minutes. *(Vérifié par Timéo ; vecteur décrit différemment selon les sources.)*
3. **2025 : ≈ 3,4 Md$ volés** (Chainalysis, janvier → début décembre 2025) ; PeckShield donne 4,04 Md$ en incluant les arnaques. **Un seul acteur étatique représente ≈ 2 Md$, soit 76 % des compromissions de services** ; Bybit seul pèse ≈ 44 % du total.
4. **La part de l'ingénierie sociale monte** : des reprises de presse de juin 2026 citent « 65 % des hacks liés à de l'ingénierie sociale » **(non confirmé : le montant associé, 17 Md$, ne correspond pas au total des hacks ; probablement un chiffre d'arnaques, à vérifier dans le rapport primaire)**. Une analyse Range sur 2026 : 366 M$ de pertes liées au phishing sur 63 incidents, dont **4 incidents d'ingénierie sociale pour 310 M$** : quelques grosses prises, pas une multitude de petites.
5. **Premier semestre 2026 : ≈ 1 à 1,3 Md$ volés sur ≈ 207 incidents** (TRM ≈ 972 M$, CertiK ≈ 1,32 Md$).

## Ce que ces faits disent pour Breaker
- **Les plus grosses pertes ne viennent plus de bugs de contrats mais de personnes trompées ou de clés compromises** dans le processus de signature. C'est exactement ce que le garde traite ; un audit de code n'y change rien.
- **Les attaques sont patientes et ciblées** (Drift : des mois de préparation) : d'où l'intérêt de la probation des clés, des explications, de la mise en attente, du traçage.
- **Les victimes connues sont des grandes plateformes et des protocoles importants** ; les pertes des petites équipes sont moins documentées : **c'est une question pour les entretiens (B5)**, et une limite à dire.

## Sources (secondaires, à remonter aux rapports primaires)
- https://www.stingrai.io/blog/crypto-hacking-statistics-2026 (reprend Chainalysis 2026)
- https://cryptorank.io/news/feed/c694b-chainalysis-crypto-hacks-social-engineering (65 %, à vérifier)
- https://range.org/blog/what-2026-onchain-losses-reveal-for-finance-teams
- https://news.dextools.io/article/crypto-hacks-2026-tracker-biggest-exploits-onchain-data
- https://arsen.co/en/blog/why-crypto-firms-are-primary-social-engineering-targets
- Bybit / Drift : voir `shared/retour-mentor-team1.md` et le journal de Timéo du 10/10 (Halborn, Bloomberg, Decrypt).
