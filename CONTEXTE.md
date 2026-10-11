# Contexte — Secure Horizons

Source : [Candidate Guide — Track Guidance (EN)](https://app.notion.com/p/Candidate-Guide-Track-Guidance-EN-3f400920c77e81beb3b4fad01fc5eeda), complété par les slides du kick-off et la page [Luma](https://luma.com/cky3ka9w?tk=Pbeaic).

Hackathon **blue team** de 36 h : construire les outils des défenseurs, là où l'IA protège et là où l'IA doit être protégée.

- **Quand :** 10–11 octobre 2026
- **Où :** ESSEC Business School, 3 Av. Bernard Hirsch, 95000 Cergy
- **Dotation :** 20 000 € en cash selon le guide Notion (Luma annonce 15 000 € en cash et crédits)
- **Organisation :** Utopia, Kryptosphère ESSEC, METALAB ESSEC, Team1 France

**Notre choix (décidé le 10/10 à 16:35) :** **Track 1 — Fintech Security, axe 2** (SOC antifraude), appliqué à la trésorerie crypto des petites et moyennes organisations (multisig sans équipe de sécurité). **Breaker n'est pas un coffre : une garde qui se greffe sur le multisig existant du client** (`shared/ce-que-breaker-est.md`). Détail : `PLAN.md` et `shared/cible-et-modele-economique.md`.

---

## ⏰ Planning

| Quoi | Quand |
|---|---|
| Kick-off (Grand Amphi) | Sam. 10:00 |
| Formation des équipes | Sam. 10:50–11:30 |
| 🚀 **Début du hacking** + mentorat d'idéation par track | **Sam. 11:30** |
| Checkpoint mi-parcours (formulaire problème / solution / stack). **Dernier moment pour confirmer le track.** | **Sam. 18:30** |
| Atelier coaching pitch | Dim. 10:00 |
| 🧊 **Rendu, gel définitif** | **Dim. 12:00** |
| Round 1 par track (une salle par track, au moins 3 experts) | Dim. 13:00–14:30 |
| Annonce des finalistes (2 par track), finale et remise des prix | Dim. 15:00 (finale 15:25–16:10) |

**Format du pitch :** le guide Notion annonce 5 min + 2 min de questions au Round 1, puis 3 min + 3 min de Q&A en finale devant le grand jury. La slide du kick-off disait 4 + 2 puis 6 + 4. **À reconfirmer sur place.** Tous les juges sont dans la salle, sans visio.

---

## 📦 Livrables communs (avant dim. 12:00)

1. **Repo Git accessible au jury**, avec un README clair : problème, architecture, installation, limites connues.
   ⚠️ Notre repo est privé : il faudra inviter le jury ou le passer en public avant le rendu.
2. **Vidéo démo de 2–3 min** montrant le PoC en action (filet de sécurité si la démo live plante).
3. **Pitch deck**, 8 slides max recommandées : problème, cible, solution, démo, business model, équipe.
4. **Fiche défense (1 page)** : scénario de menace, fonctions NIST CSF couvertes, techniques ATT&CK / ATLAS ou risques OWASP traités, métriques obtenues (taux de détection, faux positifs, temps de détection et de réponse), limites connues.
5. **Le livrable spécifique au track** (voir plus bas).

## 🚫 Règles non négociables

- **Code écrit pendant l'événement :** les librairies, modèles et API existants sont autorisés, mais le cœur du projet doit être développé entre sam. 11:30 et dim. 12:00.
- **Aucune action sur un système réel sans autorisation écrite.** Une attaque ne peut être simulée que pour générer des données de test, sur nos propres environnements.
- **Aucune donnée personnelle réelle :** uniquement des datasets publics ou synthétiques (RGPD).
- **Zéro secret dans le repo** (clés API, tokens, mots de passe). Le jury vérifiera.
- Équipes de 5 personnes maximum.

## 🧭 Fil rouge : penser comme un défenseur

Chaque projet doit couvrir au moins une fonction du **NIST CSF 2.0**, idéalement **Detect** ou **Respond** :

| Fonction | Question clé |
|---|---|
| 🏛️ Govern | Qui décide, selon quelles règles, et comment le prouver ? |
| 🔎 Identify | Que faut-il protéger (actifs, données, identités, agents IA) ? |
| 🧱 Protect | Comment réduire la surface d'attaque ? |
| 📡 **Detect** | Comment repérer une attaque en cours, vite, sans noyer l'analyste ? |
| 🚨 **Respond** | Comment contenir, enquêter et notifier ? |
| ♻️ Recover | Comment restaurer et tirer les leçons ? |

**Référentiels à citer :** MITRE ATT&CK (techniques d'attaque), MITRE ATLAS (menaces propres à l'IA), MITRE D3FEND (contre-mesures), OWASP Top 10 for Agentic Applications (déc. 2025).

**Contexte 2026 utile pour le pitch :**
- OWASP Agentic Top 10 (fin 2025) : détournement d'objectif, mauvais usage d'outils, abus d'identité et de privilèges.
- EchoLeak (CVE-2025-32711) : un seul e-mail piégé ingéré par un assistant RAG a suffi à exfiltrer des données, sans aucun clic.
- Incident Hugging Face (mai–juillet 2026) : des agents IA ont enchaîné des intrusions autonomes pendant des tests de cybersécurité.
- NIS2 impose une notification précoce sous 24 h. DORA encadre la résilience du secteur financier. L'AI Act imposera la robustesse des IA « à haut risque » d'ici déc. 2027.
- Les assureurs excluent de plus en plus les incidents liés à une IA non contrôlée.

---

## 🏦 Track 1 — Fintech Security : Guardians of Value

Surveiller, détecter et répondre aux menaces qui visent l'argent, de la banque à la DeFi.

**Problèmes**
- **Analystes submergés :** l'IA générative industrialise le phishing, les faux documents et les voix clonées. Les moteurs à règles noient les équipes fraude et conformité sous les faux positifs.
- **Agents IA qui manipulent de l'argent :** un agent de recherche peu privilégié, manipulé par un document piégé, ordonne à un agent financier d'exécuter une transaction. Sans vérification de la chaîne d'autorité, elle passe (**OWASP ASI03, ASI07**).
- **Incidents à déclarer vite :** DORA impose de détecter, classer et déclarer rapidement les incidents TIC majeurs, y compris aux prestataires crypto MiCA. En DeFi, un exploit se joue en minutes.
- Les solutions doivent être **efficaces et explicables** à un régulateur, un auditeur ou un assureur.

**Pistes suggérées**
1. **Poste de l'analyste LCB-FT :** détection de blanchiment et de réseaux de mules par graph ML et détection d'anomalies, score de risque explicable, priorisation des alertes, réduction mesurée des faux positifs. *(Detect, Respond)*
2. **SOC anti-fraude à l'ère de l'IA générative :** prise de contrôle de compte, arnaques au paiement, fraude au président par voix clonée. Signaux comportementaux (appareil, géoloc, navigation), faux documents KYC, réponse graduée (authentification renforcée, mise en attente, gel, alerte client). *(Detect, Respond)*
3. **Supervision et confinement des agents IA financiers :** journal de chaque action d'agent avec sa chaîne d'autorité (quel humain ou agent l'a demandée), détection des transactions hors périmètre, tokens courts et révocables, kill switch automatique au-delà d'un seuil de risque, validation humaine des actions sensibles. *(Identify, Detect, Respond)*
4. **Détection et réponse DeFi / DORA :** monitoring on-chain d'un contrat (ex. testnet Avalanche Fuji), playbook (pause du contrat, alertes, traçage des fonds), classification automatique selon les critères DORA, rapport pré-rempli, cartographie des prestataires critiques. *(Detect, Respond, Recover)*

**Livrables spécifiques**
- PoC fonctionnel de bout en bout, de la détection à la réponse, sur un scénario concret de fraude ou d'incident (données synthétiques ou rejouées).
- Playbook de réponse : qui est alerté, quelles actions sont automatiques, lesquelles restent humaines, comment c'est documenté.
- Slide « conformité » : DORA, LCB-FT, MiCA ou AI Act, et comment un auditeur peut vérifier les décisions.

**Grille**
| Critère | Poids | Ce que regarde le jury |
|---|---|---|
| Efficacité de détection | **30 %** | Précision, taux de faux positifs, temps de détection, sur un scénario réaliste |
| Qualité de la réponse | 20 % | Réponse proportionnée, actionnable, utile à l'analyste |
| Faisabilité & intégration | 20 % | Le PoC marche-t-il ? S'intégrerait-il chez une banque, une fintech ou un protocole ? |
| Conformité & explicabilité | 15 % | Décisions traçables et défendables devant un régulateur ou un auditeur |
| Pitch & démo | 15 % | Clarté, démo convaincante, gestion du temps et des questions |

**Mentors :** Team1 Avalanche (on-chain, DeFi), KPMG (fraude, LCB-FT, DORA), Kryptosphère (crypto, sécurité des protocoles), Utopia (ML, LLM, agents), AWS (crédits cloud).

**Conseils :** un seul scénario, traité parfaitement de l'alerte à la réponse. Montrer des chiffres. Préparer la réponse à : *« Si votre modèle se trompe, qui est responsable ? »*

---

## 🤖 Track 2 — AI for Security & Secure AI : Defenders Augmented

Construire le SOC de demain : augmenté par l'IA, et capable de superviser l'IA. Deux faces, toutes deux défensives.

**Problèmes**
- **SOC surchargés :** un copilote qui hallucine est pire que pas de copilote. L'enjeu est la fiabilité : scores d'incertitude, vérification contre les sources, humain dans la boucle.
- **Agents IA sans supervision :** mémoire, planification, appels d'outils via MCP. Des instructions malveillantes peuvent se cacher dans la description d'un outil (« tool poisoning »). OWASP place en tête **ASI01** (détournement d'objectif), **ASI02** (mauvais usage d'outils) et **ASI03** (abus d'identité et de privilèges).
- **Identités hors de contrôle :** des agents tournent sur des comptes de service sur-privilégiés ou héritent de la session complète de l'utilisateur. Personne ne sait quels agents existent ni ce qu'ils ont le droit de faire.
- **Fuites de l'intérieur :** selon Gartner, la plupart des incidents IA viendront de violations internes (partage excessif, permissions mal configurées). EchoLeak en est l'illustration.

> ⚠️ **Signal marché :** Lakera (racheté par Check Point) et Prompt Security (racheté par SentinelOne) en 2025. **Un énième filtre de prompts n'impressionnera pas.** Viser la supervision de la couche outils, l'identité des agents, la sécurité des données RAG ou la fiabilité du copilote.

**Pistes suggérées**
1. **Copilote SOC fiable & détection augmentée :** score d'incertitude sur chaque conclusion, vérification automatique contre les logs sources (« trust but verify »), escalade vers un humain si la confiance est basse, conversion de threat intel en règles de détection testées sur logs rejoués et mappées ATT&CK, reconstruction de timeline, notification NIS2 sous 24 h. *(Detect, Respond)*
2. **Supervision de la couche outils des agents (MCP) :** gateway d'observabilité qui loggue les appels d'outils et leurs paramètres, détection d'appels anormaux (séquence inhabituelle, exfiltration, commande dangereuse), analyse des descriptions d'outils MCP pour repérer les instructions cachées, alertes vers un SIEM, kill switch et sandbox contre les défaillances en cascade (**ASI08**). *(Detect, Respond)*
3. **Identité, secrets & privilèges des agents :** inventaire automatique des identités non humaines (agents, comptes de service, clés API), secrets exposés dans les prompts, logs et configs MCP, escalade de privilèges ou communication inter-agents non vérifiée (**ASI03, ASI07**), tokens limités à une tâche et révoqués automatiquement. *(Identify, Protect, Detect)*
4. **RAG sous surveillance, anti-fuite et anti-empoisonnement :** audit des permissions avant indexation vectorielle, détection de documents à instructions cachées (**ASI06**), surveillance des sorties qui exfiltrent (liens et images Markdown vers des domaines externes, façon EchoLeak), traçabilité de l'origine de chaque information générée. *(Identify, Protect, Detect)*

**Livrables spécifiques**
- PoC fonctionnel branché sur un flux réaliste : logs SOC, agent instrumenté, pipeline RAG (même simplifié).
- Métriques défensives : temps gagné par l'analyste, précision des détections, couverture ATT&CK / ATLAS / OWASP Agentic.
- Section « comment l'humain garde le contrôle » : seuils d'escalade, traçabilité des décisions de l'IA, gestion des erreurs.

**Grille**
| Critère | Poids | Ce que regarde le jury |
|---|---|---|
| Efficacité défensive | **30 %** | Détection, couverture des menaces, précision, sur un scénario réaliste |
| Valeur opérationnelle pour l'analyste | 20 % | Temps gagné, clarté des alertes, réponse actionnable |
| Fiabilité & contrôle de l'IA | 20 % | Hallucinations, traçabilité, humain dans la boucle. **Va-t-on au-delà d'un filtre de prompts ?** |
| Intégration technique | 15 % | Compatibilité SIEM / SOAR / MCP, latence, passage à l'échelle, **aucun secret dans le repo** |
| Pitch & démo | 15 % | Clarté, démo convaincante, gestion du temps et des questions |

**Mentors :** GitGuardian (secrets, identités non humaines, supervision d'agents), METALAB ESSEC (IA responsable), KPMG (confiance IA, AI Act, NIS2), Utopia (LLM, RAG, agents, atelier « copilote SOC fiable »), AWS (crédits cloud).

**Conseils :** partir d'un flux réel ou rejoué et montrer ce que l'analyste voit, décide et fait. **Nommer** le risque OWASP ou la technique ATLAS / ATT&CK détectée. Être honnête sur les limites : *« voici ce qu'on ne détecte pas encore »* inspire plus confiance que *« on voit tout »*.

---

## 🌐 Track 3 — Open Track (pour mémoire)

Thème libre en IA × cyber défensive : OT/ICS, supply chain logicielle et IA, conformité continue AI Act, PME et citoyens. Grille orientée startup : problème 25 %, efficacité 25 %, impact 20 %, viabilité business 20 %, pitch 10 %.
