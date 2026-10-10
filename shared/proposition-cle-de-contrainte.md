# Proposition : la clé de contrainte (idée 5) — pour Timéo

> Demandée par Romain le 10/10 vers 21:30, en priorité avec les idées 1, 3 et 4. Elle touche au contrat `TreasuryGuard`, donc à ton dossier : voici la spécification, à toi de dire si c'est faisable ce soir (estimation : 1 h 30 à 2 h avec les tests, puis redéploiement Fuji) ou si on la garde pour le pitch.

## Le problème qu'elle résout
Tous nos contrôles protègent la **clé**. Aucun ne protège la **personne**. Un signataire menacé physiquement, ou sous forte pression hiérarchique, signera ce qu'on lui demande. C'est le scénario du « $5 wrench attack » et, sous une forme moins violente, de la fraude au président.

## Le principe
Chaque signataire enregistre **deux clés** : sa clé normale et une **clé de contrainte**. Les deux signent de la même façon à l'écran. Mais quand la clé de contrainte est utilisée :
1. le contrat enregistre une approbation **en apparence** (événement `Approved` normal) ;
2. le paiement devient **inexécutable** (toute tentative d'`execute` échoue avec l'erreur générique « TooEarly ») ;
3. le portefeuille passe en **gel silencieux** : les paiements en cours n'avancent plus, mais aucun événement `Frozen` n'est émis ;
4. le moniteur (hors chaîne) voit l'approbation venir de l'adresse de contrainte et **alerte les autres signataires** par un canal privé.

## Ce qu'il faut dans le contrat (à ton estimation)
- `setDuressKey(address duress)` : un signataire déclare sa clé de contrainte (une seule, modifiable par lui seul, jamais exposée dans une liste publique de « signataires »).
- `approve(id)` accepte aussi un appel depuis une clé de contrainte : il est compté comme approbation dans `approvals`, émet `Approved(id, owner, …)` avec l'adresse de l'**owner** (pas celle de contrainte), et marque `proposal.duress = true` et `silentFreeze = true`.
- `execute(id)` : si `proposal.duress` ou `silentFreeze`, revert avec `TooEarly(uint64.max)` (pas une nouvelle erreur, pour ne pas trahir le mécanisme).
- Levée du gel silencieux : par une majorité de signataires **sans** la clé compromise (comme `approveUnfreeze`), ce qui émet alors un événement normal.
- Les clés de contrainte comptent-elles pour `threshold` ? Non : elles ne peuvent jamais rendre un paiement exécutable, c'est tout l'intérêt.

## Ce qu'il faut dire honnêtement
- **Sur une chaîne publique, rien n'est vraiment secret** : un attaquant qui lit le code du contrat et la liste des clés de contrainte peut comprendre. La discrétion vaut pour l'attaquant qui regarde l'écran de sa victime, pas pour un expert qui audite la chaîne. C'est déjà beaucoup : dans une attaque sous contrainte, l'attaquant est à côté de la victime, pas devant un explorateur.
- La liste des clés de contrainte doit donc être stockée **hachée** (`keccak256(adresse)`) dans le contrat, pas en clair.
- Le mécanisme ne protège pas contre un attaquant qui connaît la clé de contrainte de sa victime.

## Côté Romain (déjà prévu)
- Le moteur apprend les adresses de contrainte (fichier hors chaîne, hachées) et émet une alerte `DURESS_SIGNATURE` de niveau `hold` vers les autres signataires, sans l'inscrire sur la chaîne (sinon l'attaquant la verrait).
- Le tableau de bord n'affiche rien de différent pour un paiement approuvé sous contrainte : c'est voulu.

## Pour la démo
Un signataire « sous pression » approuve un gros paiement avec sa clé de contrainte ; l'écran dit « approuvé » ; le fraudeur tente d'exécuter : « trop tôt », indéfiniment ; les autres signataires reçoivent une notification privée et gèlent officiellement.

**Dis dans le journal : faisable ce soir, ou slide seulement.**
