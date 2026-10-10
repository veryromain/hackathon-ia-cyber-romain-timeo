# Positionnement de Breaker après l'étude de marché (décisions et recommandations business)

> Romain (avec Claude), 11/10 vers 00:35. Réponses business et positionnement aux dix questions de Romain après B4. La partie technique (agent cosignataire de simulation) est traitée par Timéo dans sa conversation.

## 1. Bloquer ou ralentir ? → Ralentir par défaut, le client choisit le pouvoir délégué
Trois modes au choix du client : **Observation** (l'agent simule, analyse, explique, rien ne change), **Friction** (défaut : signature en plus / mise en attente, les signataires décident), **Cosignataire** (l'agent est signataire du multisig et refuse de signer ; dérogation possible par une majorité renforcée de signataires établis, après délai).
Pourquoi pas le blocage par défaut : responsabilité (un paiement légitime bloqué est un dommage dont nous sommes la cause ; un retard, non) ; cible sans RSSI pour arbitrer ; hors périmètre de garde (MiCA) tant qu'on ne peut pas retenir les fonds ; différenciation face à Blockaid Cosigner.
**Exception nommée :** adresses sanctionnées (OFAC) : le client régulé peut activer un refus pur dans *son* contrat (obligation légale, tracée). Ce n'est pas nous qui bloquons.

## 2. Cible → gardée : les équipes de 10 à 30 personnes qui gardent des millions sans équipe de sécurité
Originale et libre (les concurrents vendent aux institutions, sans prix public). Risques à anticiper : petits budgets → libre-service et prix affiché ; taille du marché sur Avalanche → B3 ; fidélité sans incident → rapport mensuel + observation gratuite. Tête de pont vers les fonds et fondations.

## 3. Prix → B6. Cadre : abonnement mensuel par portefeuille, paliers selon la trésorerie, sans engagement, prix affiché. Fourchette annoncée au pitch comme hypothèse.

## 4. Chaîne → « Né sur Avalanche », contrat Solidity portable sur toute chaîne EVM ; élargissement = décision commerciale, secondaire.

## 5. Autres informations pour nourrir les agents (par intérêt décroissant, côté légal et public)
Historique on-chain du destinataire (âge, contreparties, mixeur/pont, étiquettes Snowtrace) ; vérification du contrat destinataire ; bases communautaires (Chainabuse, ScamSniffer, SEAL 911, domaines de phishing) ; registres d'entreprises (Sirene) croisés avec le libellé ; contexte de la demande (e-mail déclencheur, âge du domaine ; RGPD, opt-in) ; réseaux sociaux et forums via Apify ; rapprochement avec la facturation du client (question de contexte métier) ; empreinte comportementale des signataires. **À éviter :** biométrie, analyse de pièces jointes par l'IA.

## 6. Explication pour non-expert → norme en 3 lignes : ce qui est inhabituel / ce que le garde a fait / ce que vous devez faire maintenant (verbe obligatoire).

## 7. Verrou de sortie → deux verrous séparés
**Commercial : aucun** (mensuel, sans engagement, données exportables, contrat open source). **Sécurité : oui, au client** : retirer ou affaiblir le garde passe par la procédure d'un paiement (proposition, signatures renforcées, délai), sinon un attaquant à deux clés retire le garde avant de vider. « Vous partez quand vous voulez, mais jamais en une seule transaction. »

## 8. Contrat non audité → analyse statique + fuzzing + open source cette nuit ; audit externe avant le premier client payant (surface petite : pas de garde de fonds, donc audit court ; mentors Kryptosphère / Team1 pour l'intro, subventions Avalanche) ; prime aux bugs ensuite. Argument : le pire bug possible est un faux ralentissement, jamais une perte.

## 9. Données réelles et preuve d'efficacité → (1) rejouer les séquences on-chain publiques de Bybit et Drift dans le moteur (faisable avant dimanche) ; (2) mesurer l'oracle sur des listes publiques étiquetées ; (3) mode observation gratuit chez des équipes pilotes (à recruter au hackathon) ; (4) équipe d'attaque externe (mentors, autre équipe).

## 10. Entrée sur le marché et personnalisation
Parcours : **libre-service** (connecter son multisig en 5 min) → **observation gratuite 2 à 4 semaines** avec rapport → **activation de la friction** en un clic, abonnement → « demander une démo » en second, pour les grands comptes. Distribution : catalogue d'applications Safe, écosystème Avalanche (Team1, subventions, forums de DAO), auditeurs partenaires, analyses publiques d'incidents.
Personnalisation : trois **profils** (prudent, standard, réactif) avec planchers ; carnet d'adresses construit automatiquement depuis l'historique du multisig ; heures ouvrées, pièges, liste de confiance ; tout réglage se change comme un paiement ; politiques sur mesure pour les grands comptes.
