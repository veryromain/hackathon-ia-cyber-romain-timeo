# Plan d'action — projet « Breaker » (nom provisoire)

> **Statut : proposition à valider** avec Timéo et le mentor Team1 avant le checkpoint de **sam. 18:30**.
> Track 1 — Fintech Security, axe 4 (Détection & réponse DeFi / DORA).

## 1. Le projet en une phrase

**Un disjoncteur automatique pour protocoles DeFi.** Il repère un vidage de fonds en cours, met le contrat en pause en quelques secondes et transforme l'incident en déclaration DORA pré-remplie, chaque chiffre étant relié à une transaction on-chain.

## 2. Le scénario de démo (un seul, maîtrisé de bout en bout)

1. **Avant :** notre coffre (vault) tourne sur le testnet Avalanche Fuji avec du trafic normal simulé (dépôts et retraits de plusieurs utilisateurs).
2. **Attaque :** un vidage étalé sur plusieurs transactions, comme Nomad, Ronin ou Drift (31 retraits en 12 min).
   - **Variante proposée :** l'attaquant est un **agent IA de trésorerie piégé** par un document empoisonné (OWASP ASI01/ASI07). Elle relie l'idée de Romain et celle de Timéo dans un seul scénario.
3. **Détection :** le moniteur calcule un score de risque à chaque bloc et le seuil est franchi en moins de N blocs.
4. **Réponse graduée :** alerte → limitation des retraits → **pause**, déclenchée par un rôle « gardien » aux pouvoirs bornés (il peut mettre en pause, jamais déplacer de fonds).
5. **Après :** l'incident est classé selon les critères DORA. Un rapport pré-rempli est généré par un LLM (Bedrock), avec preuves (hash de transactions), chronologie et montants sauvés. **La levée de la pause exige une validation humaine.**
6. **Chiffres à l'écran :** temps de détection, % des fonds sauvés, faux positifs sur le trafic normal rejoué.

## 3. Architecture

```
 [Générateur de trafic]──┐            ┌──> [Dashboard analyste]
   normal + attaques      │            │     alertes, score, chronologie,
                          v            │     bouton « lever la pause » (humain)
              [Contrat Vault sur Fuji] │
               pause() + rate-limit    │
               rôle GUARDIAN borné     │
                          │ événements │
                          v            │
                 [Moniteur on-chain] ──┤
                  features par bloc    │
                  score de risque      │
                  ── seuil ──> tx pause()
                          │
                          v
               [Module conformité DORA]
                classification (règles)
                + rapport rédigé par LLM (Bedrock)
                + journal d'audit horodaté et haché
```

**Où est l'IA ?**
- **Détection :** un score d'anomalie appris sur le trafic normal (ex. Isolation Forest), combiné à des règles explicables. Chaque alerte donne ses raisons.
- **Réponse :** un LLM rédige la notification DORA et la chronologie. Il ne décide jamais de la pause : la décision vient du score et des seuils, pas du LLM.
- **Variante :** l'agent IA de trésorerie piégé sert de vecteur d'attaque réaliste.

**Stack proposée :**
| Brique | Choix | Pourquoi |
|---|---|---|
| Contrat | Solidity + **Hardhat** (Node) | Fonctionne sous Windows sans Docker. Foundry est plus confortable sous WSL |
| Chaîne | Avalanche **Fuji testnet** | Mentors Team1, faucet gratuit, compatible EVM |
| Moniteur / détection | Python 3.12 + web3.py + scikit-learn | Déjà installé chez Timéo |
| LLM | AWS Bedrock (Claude) | Crédits du hackathon |
| Dashboard | Streamlit | Une démo visuelle en quelques heures |

## 4. Répartition du travail

| Qui | Dossier | Périmètre |
|---|---|---|
| **Timéo** (crypto) | `ia-2/` | Contrat Vault (pause, rate-limit, rôle gardien), déploiement Fuji, générateur de trafic et scénarios d'attaque |
| **Romain** | `ia-1/` | Moniteur, features et score de risque, module DORA (classification + rapport Bedrock), dashboard |
| **Ensemble** | `shared/` | Format des événements, mesures, pitch deck, vidéo, fiche défense |

**Interface à figer dès le début :** le format JSON d'un événement (bloc, tx, from, montant, type) et d'une alerte (score, raisons, tx liées). C'est ce qui permet de travailler en parallèle.

## 5. Planning jusqu'au rendu (dim. 12:00, gel définitif)

| Créneau | Objectif | Livrable de contrôle |
|---|---|---|
| **Sam. 14:00–15:30** | Valider l'idée avec le mentor Team1. Wallets Fuji + faucet. Test d'un appel Bedrock. Figer le format des événements | Décision écrite dans `JOURNAL.md` |
| **Sam. 15:30–18:30** | Contrat Vault déployé sur Fuji. Générateur de trafic normal. Moniteur qui lit les événements en direct | Un dépôt et un retrait visibles dans le moniteur |
| **Sam. 18:30** | ✅ **Checkpoint officiel** (formulaire problème / solution / stack, confirmation du track) | — |
| **Sam. 18:30–23:00** | Scénarios d'attaque (au moins 2). Features et score. Pause automatique déclenchée par le moniteur | **Première démo de bout en bout**, même moche |
| **Sam. 23:00–03:00** | Module DORA (classification + rapport LLM). Dashboard. Bouton de levée de pause humaine | Rapport généré sur une attaque réelle sur Fuji |
| **Dim. 03:00–08:00** | Mesures : N exécutions (trafic normal + attaques) → taux de détection, faux positifs, temps de détection, fonds sauvés. Corrections | Tableau de chiffres dans `shared/` |
| **Dim. 08:00–10:00** | Enregistrement de la **vidéo démo** (2–3 min), README final, fiche défense, slide conformité, playbook | — |
| **Dim. 10:00** | Atelier coaching pitch | — |
| **Dim. 10:00–12:00** | Deck (8 slides), répétition, **vérifier zéro secret dans le repo**, donner l'accès au jury | 🧊 **Rendu 12:00** |
| **Dim. 13:00** | Round 1 | — |

**Règle d'or :** une démo de bout en bout qui marche à 23:00 samedi vaut mieux que trois briques parfaites séparées. On ajoute la finition ensuite.

## 6. Livrables (rappel)

- [ ] Repo + README (problème, architecture, installation, limites connues)
- [ ] Vidéo démo de 2–3 min
- [ ] Pitch deck (8 slides max)
- [ ] Fiche défense : scénario, fonctions NIST CSF (Detect, Respond, Recover), techniques ATT&CK et risques OWASP, métriques, limites
- [ ] PoC de bout en bout
- [ ] **Playbook de réponse** : qui est alerté, ce qui est automatique (alerte, rate-limit, pause), ce qui reste humain (levée de pause, notification au régulateur)
- [ ] **Slide conformité** : DORA (classification et notification), MiCA (prestataires crypto), journal d'audit vérifiable

## 7. Limites et risques

### Techniques
| Risque | Impact | Parade |
|---|---|---|
| **Attaque en une seule transaction** (flash loan : Beanstalk, Euler) | Le disjoncteur arrive trop tard | On l'assume et on le dit. Notre cible, ce sont les vidages étalés ou précédés de signes. On peut citer la piste future (surveillance du mempool, ERC-7265) |
| Timéo connaît Solana, pas Solidity | Retard sur le contrat | Contrat **minimal** (≈100 lignes), en partant d'OpenZeppelin (`Pausable`, `AccessControl`) |
| Faucet Fuji limité, limites de débit du RPC public | Moins de transactions | Montants minuscules. RPC de secours. Option : réseau local Hardhat pour les mesures en masse, Fuji pour la démo |
| Windows sans Docker chez Timéo | Problèmes d'outillage | Hardhat (Node), pas Foundry ni Docker |
| Accès AWS Bedrock inconnu (identifiants, région, modèles) | Pas de rapport LLM | **À débloquer dès maintenant.** Plan B : rapport par template, sans LLM |
| Démo live qui plante | Perte de points | Vidéo enregistrée + scénario rejouable sur réseau local |

### Données et mesures
- **Tout le trafic est synthétique**, fabriqué par nous. Les chiffres seront donc favorables par construction. Il faut le dire et montrer comment on a évité le sur-apprentissage : seeds différentes, trafic de test séparé du trafic d'entraînement.
- Peu de scénarios d'attaque, donc la généralisation n'est pas prouvée. Il faut le présenter comme une limite connue.

### Réglementaires (questions probables du jury)
- **Un protocole DeFi pur n'est pas soumis à DORA ni à MiCA.** Notre client cible doit donc être une **entité régulée exposée à la DeFi**. → **Choix de cadrage :** la démo met en scène un **prestataire crypto agréé MiCA fictif** (nom inventé, pas une vraie entreprise) qui propose à ses clients un produit « Earn » reposant sur notre coffre on-chain. Pour lui, le contrat est un actif TIC critique : un exploit est un incident TIC qui relève de DORA. Les protocoles DeFi purs restent un second marché, avec la même détection et la même pause, mais un post-mortem public à la place du rapport DORA. À valider avec le mentor.
- Les délais et seuils DORA sont **à vérifier dans les textes** (RTS sur la classification des incidents). De mémoire : notification initiale sous 4 h après la classification comme incident majeur, et au plus tard 24 h après sa détection ; rapport intermédiaire sous 72 h ; rapport final sous 1 mois.
- **« Si votre modèle se trompe, qui est responsable ? »** Notre réponse :
  - Le modèle ne peut que **mettre en pause**, une action réversible et bornée. Il ne déplace jamais de fonds.
  - La levée de la pause et l'envoi au régulateur restent humains.
  - Chaque décision est journalisée avec ses raisons, et un auditeur peut la rejouer.
- **Une pause, c'est de la centralisation** (critique classique en DeFi). Parade : pouvoirs du gardien bornés et publics, pause limitée dans le temps, levée possible par un multisig ou un timelock.

### Organisation
- Deux personnes, environ 22 h restantes, sommeil compris : **il faut couper dans le périmètre, pas dans la démo**.
- Le sujet n'est pas encore validé à deux. Chaque heure de débat est une heure de code en moins. Il faut décider avant 15:30.

## 8. Idées bonus (si on est en avance)

1. **L'agent IA piégé comme vecteur d'attaque.** Un agent de trésorerie lit un document empoisonné et vide le coffre en plusieurs fois. Le disjoncteur l'arrête. C'est la jonction avec l'idée de Romain et avec le contexte 2026 (OWASP Agentic). Ça fait une démo très parlante.
2. **Réponse graduée plutôt que binaire :** alerte, puis plafond de retrait par fenêtre (inspiré de la proposition de standard **ERC-7265 « Circuit Breaker »**), puis pause. C'est plus proportionné, et donc mieux noté sur la qualité de la réponse.
3. **Journal d'audit inviolable :** hachage chaîné des décisions, avec le hash final publié on-chain. Un auditeur peut vérifier que rien n'a été modifié après coup. C'est un vrai plus pour la conformité et l'explicabilité.
4. **Rejeu d'un vrai exploit :** reproduire la *forme* d'un incident connu (cadence des retraits de Drift ou Nomad) sur notre propre contrat pour rendre la démo crédible.
5. **Cartographie des tiers critiques** (exigence DORA) : lister les oracles, ponts et RPC dont dépend le protocole, et les inclure dans le rapport.
