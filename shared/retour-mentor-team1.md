# Retour du mentor Team1 (Avalanche) et ce qu'on en fait

Échange du 10 octobre vers 16h00. Notes prises par Granola (titre « Avalanche security tool plan », partagées par Romain), relues et confrontées au plan par Claude côté Timéo à 16h20. La première partie rapporte ce qui a été dit ; la seconde est une analyse, à valider par Romain et Timéo.

## 1. Ce que dit la note

**Projet et contexte**
- Track 1, axe 4 sur Avalanche : outil de protection pour des dApps de prêt décentralisées.
- Inspiration : l'exploit de Drift, en plusieurs transactions.
- Cible : grandes entreprises qui gèrent des fonds sur des protocoles DeFi.

**Architecture**
- Un agent IA lit la blockchain en temps réel pour détecter des anomalies.
- Deux composantes : un tableau de bord de surveillance (hors chaîne) et un smart contract qui réagit aux alertes de l'agent (sur la chaîne).
- Mécanismes évoqués : pause des transactions ; plafond de sorties par période (exemple : 10 % de la trésorerie sans autorisation supplémentaire) ; rotation automatique des clés du multisig ; déplacement des fonds vers des portefeuilles sécurisés si un exploit est détecté.

**Décentralisation contre sécurité**
- Bloquer des transactions, c'est renoncer à la décentralisation totale.
- Solution hybride : l'agent détecte, le smart contract exécute. L'IA inscrit une transaction sur Avalanche, le contrat réagit.
- Ne pas gérer directement les fonds des clients, pour ne pas tomber sous MiCA.

**Modèle économique et marché**
- Abonnement mensuel qui inclut une estimation des frais de gas ; le gas est mineur face aux autres coûts.
- Prestations complémentaires : mises à jour, audits, réparations.
- Marché : protocoles de prêt à grosses trésoreries. États-Unis et Asie plus mûrs que l'Europe.

**Exemple et recommandations**
- Drift (Solana) recommandé comme cas principal. Peu d'exploits majeurs sur Avalanche depuis un an et demi à deux ans ; Benqi y est le principal protocole de prêt.
- On peut justifier Avalanche même si l'exploit de référence vient d'ailleurs.
- Piste KYC : accord récent entre les Émirats arabes unis et Avalanche.

**Prochaines étapes notées**
1. Valider l'architecture en deux composantes.
2. S'assurer qu'une transaction est bien faite sur la chaîne, pour justifier Avalanche devant le jury.
3. Documenter l'exploit de référence et argumenter pourquoi Avalanche l'aurait empêché.
4. Préparer une estimation brute des frais de gas et segmenter le marché.

## 2. Analyse : ce qui est déjà fait, ce qui change, ce qu'on refuse

| Point du mentor | État | Ce qu'on fait |
|---|---|---|
| Deux composantes (tableau de bord + contrat qui réagit) | **Déjà notre architecture** | Rien à changer |
| L'IA inscrit une transaction, le contrat réagit | **Déjà fait** : `escalate(niveau, raison)` est une transaction signée par le gardien, la raison est gravée dans l'événement `GuardLevelChanged` | Précision technique : un contrat ne peut pas « lire » une autre transaction. Le moniteur appelle directement une fonction du coffre, ce qui revient au même pour le jury |
| Une transaction sur la chaîne pour justifier Avalanche | **Déjà fait** dans les tests locaux | À montrer sur Fuji, avec le lien de l'explorateur dans la démo |
| Plafond de sorties par période (10 %) | **Partiel** : le plafond n'existe qu'au niveau `Limited`, que le gardien doit activer | **À ajouter** : un plafond permanent dès le niveau `Normal`, en pourcentage de la liquidité. Il borne aussi la perte d'une attaque en une seule transaction, notre principale limite |
| Estimation des frais de gas | **Fait** (mesures ci-dessous) | À reprendre dans la slide du modèle économique |
| Déplacer les fonds vers un portefeuille sécurisé | **À refuser** | Voir plus bas |
| Rotation automatique des clés du multisig | **Hors périmètre** | Feuille de route seulement |
| Piste KYC, Émirats | Non vérifié, hors sujet | Ne pas citer sans source |

### Pourquoi refuser le déplacement des fonds
Notre réponse à « si le modèle se trompe, qui est responsable ? » repose sur une règle : le gardien peut seulement mettre en pause, jamais toucher aux fonds. Un agent qui déplace les fonds casse cette règle. Il contredit aussi l'autre conseil du mentor (ne pas gérer les fonds des clients, sinon MiCA). Et il crée la cible idéale pour un attaquant : compromettre l'agent suffit à vider le coffre. On garde la pause et le plafond.

### Conformité : deux questions à ne pas mélanger
- **Nous, éditeur de l'outil :** nous ne détenons jamais de fonds, donc pas d'agrément MiCA. C'est l'argument du mentor, et le rôle de gardien borné le prouve dans le code.
- **Notre client :** s'il est une entité financière régulée (par exemple un prestataire crypto agréé), il reste soumis à DORA et doit classer et déclarer l'incident. C'est ce que demande l'axe 4 du guide et ce que note le critère « conformité » (15 %). Le cadrage du `PLAN.md` (client fictif agréé MiCA exposé au coffre) reste donc valable.
- À confirmer avec le mentor KPMG, plus compétent que Team1 sur ce point : vis-à-vis d'un tel client, nous serions un prestataire tiers de services TIC au sens de DORA.

### « Pourquoi Avalanche aurait empêché l'exploit » : ne pas le dire comme ça
Avalanche n'aurait pas empêché Drift : la manipulation d'oracle et la prise de contrôle des droits d'administration par ingénierie sociale ne dépendent pas de la chaîne. Un jury d'experts le relèvera. Ce qu'on peut défendre :
- Notre outil aurait eu de quoi agir (trois semaines de signaux, puis 12 minutes de vidage), et sur Avalanche la transaction de pause est définitive en une à deux secondes pour une fraction de centime.
- Le vecteur précis de Drift, les « durable nonces », est une fonction propre à Solana. Des transactions de multisig signées à l'avance posent un risque voisin sur les chaînes EVM, donc l'argument est à manier avec prudence.
- Avalanche permet à une institution de lancer sa propre chaîne (L1) avec ses règles. C'est une piste de feuille de route, pas un élément de la démo.

Le délai de finalité et les L1 sont cités de mémoire : à vérifier dans la documentation d'Avalanche avant de les mettre sur une slide.

### Écart de chiffre
La note dit 255 M$ pour Drift. Nos sources (Halborn, Bloomberg, Decrypt) donnent **280 à 285 M$**. Garder le chiffre sourcé.

## 3. Frais de gas mesurés

Gas mesuré sur la chaîne locale (`cd ia-2 && npm run gas`). Prix relevés le 10 octobre à 16h17 : gas de la C-Chain à 5 nAVAX (`eth_gasPrice` sur le RPC public), AVAX à 10,47 $ (CoinGecko).

| Transaction | Gas | Coût en AVAX | Coût en dollars |
|---|---|---|---|
| Passage au niveau `Limited` | 36 854 | 0,00018 | 0,002 $ |
| Passage au niveau `Paused` | 34 389 | 0,00017 | 0,002 $ |
| Relance par un humain | 33 275 | 0,00017 | 0,002 $ |
| Déploiement du coffre (une fois) | 1 894 222 | 0,0095 | 0,10 $ |

Conclusion pour le modèle économique : une intervention coûte moins d'un centime, et le moniteur ne paie rien tant qu'il ne fait que lire. Le gas est négligeable dans le prix de l'abonnement, comme le disait le mentor. Le prix du gas varie avec la charge du réseau : même multiplié par cent, une pause resterait sous 0,20 $.
