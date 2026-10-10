# Contexte — Secure Horizons

Hackathon de 36 h sur l'IA et la cybersécurité, organisé par Team1 France avec UTOPIA, KRYPTOSPHERE et ESSEC MetaLab.

- **Quand :** 10–11 octobre 2026. Jugement le dimanche après-midi.
- **Où :** ESSEC Business School, 3 Av. Bernard Hirsch, 95000 Cergy
- **Dotation :** 15 000 € en cash et en crédits
- **Guide candidat :** [Notion — Candidate Guide & Track Guidance](https://app.notion.com/p/Candidate-Guide-Track-Guidance-EN-3f400920c77e81beb3b4fad01fc5eeda) (connexion nécessaire)
- **Événement :** [Luma](https://luma.com/cky3ka9w?tk=Pbeaic)

---

## Track 01 — Fintech Security

Partenaires : Team1 Avalanche, KPMG, Kryptosphere France, Utopia, AWS

**Problèmes**
- **Analystes submergés :** l'IA générative industrialise le phishing, les faux documents et les voix clonées. Les moteurs à règles fixes ne suivent pas et noient les équipes sous les faux positifs.
- **Agents IA qui manipulent de l'argent :** un agent peu privilégié, nourri d'un document piégé, demande à un agent financier d'exécuter un paiement. Sans contrôle de la chaîne d'autorité, le paiement passe (OWASP ASI03, ASI07).
- **Incidents à déclarer vite :** DORA oblige les acteurs financiers, y compris les prestataires crypto agréés MiCA, à détecter, classer et déclarer les incidents TIC majeurs. Un exploit DeFi se joue en quelques minutes.

**Livrables attendus** (en plus des livrables communs)
- **PoC fonctionnel de bout en bout :** de la détection à la réponse, sur un scénario concret de fraude ou d'incident (données synthétiques ou rejouées).
- **Playbook de réponse :** qui est alerté, quelles actions sont automatiques, lesquelles restent humaines, comment c'est documenté.
- **Slide conformité :** comment la solution s'inscrit dans DORA, AML, MiCA ou l'AI Act, et comment un auditeur peut vérifier ses décisions.

**Notation**
| Critère | Poids |
|---|---|
| Efficacité de détection | 30 % |
| Qualité de la réponse | 20 % |
| Faisabilité & intégration technique | 20 % |
| Conformité & explicabilité | 15 % |
| Pitch & démo | 15 % |

> **Conseil des organisateurs :** choisir UN scénario de fraude ou d'incident et le maîtriser, de l'alerte à la réponse. Montrer des chiffres, même sur données synthétiques. S'attendre à la question : « Si votre modèle se trompe, qui est responsable ? »

---

## Track 02 — AI for Security & Secure AI

*Defenders Augmented :* l'IA peut rendre chaque analyste dix fois plus efficace, à condition qu'on puisse lui faire confiance. Et les agents IA déployés en entreprise doivent eux aussi être surveillés.

**Problèmes**
- **SOC sous pression :** un copilote qui hallucine est pire que pas de copilote. Tout l'enjeu est la fiabilité : scores d'incertitude, vérification des sources, humain dans la boucle.
- **Agents IA sans supervision :** les agents planifient et appellent des outils, souvent via MCP. Des instructions malveillantes peuvent se cacher dans la description d'un outil (« tool poisoning »). L'OWASP classe le détournement d'objectif et le mauvais usage d'outils en tête.
- **Identités et données hors de contrôle :** la plupart des agents tournent avec des comptes sur-privilégiés, et personne ne sait lesquels existent. EchoLeak a montré qu'un seul e-mail piégé pouvait exfiltrer des données, sans aucun clic.

> **Ce qui gagne :** un énième filtre de prompts n'impressionnera pas le jury, Lakera et Prompt Security ont été rachetés en 2025. Il faut aller plus loin.

---

## Track 03 — Open Track (Uncharted Frontiers)

Usines, réseaux électriques, chaînes logicielles, PME : partout où les défenseurs manquent, il y a un projet à construire. Une seule règle : IA × cybersécurité, côté défense.

**Pistes**
- **Infrastructures critiques :** l'énergie, l'eau et l'industrie tournent sur des systèmes OT/ICS conçus pour durer des décennies, rarement surveillés comme un SI moderne.
- **Chaîne d'approvisionnement logicielle :** des centaines de dépendances, de tiers et de modèles IA téléchargés. Une seule bibliothèque compromise ou un seul modèle empoisonné suffit.
- **Conformité continue :** l'AI Act européen imposera aux IA à haut risque de prouver leur robustesse dans la durée. Des audits annuels ne peuvent pas suivre des modèles mis à jour en continu.
- **PME et citoyens :** premières cibles des arnaques dopées à l'IA, sans RSSI ni SOC, avec en plus du Shadow AI. Trustee, lauréat 2025, a montré qu'un projet grand public peut devenir une startup.

> **Ce qui gagne :** des projets qui ont une vraie chance de devenir une entreprise. Penser clients dès le premier jour.

---

## Jugement — dimanche après-midi

| Tour | Pitch | Questions |
|---|---|---|
| Round 1 | 4 min | 2 min |
| Round 2 | 6 min | 4 min |

Tous les juges sont dans la salle, sans panel à distance ni visio.
