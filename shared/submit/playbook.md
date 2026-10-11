# Breaker - playbook de réponse

Track 1 / axe 4. Scénario : des signataires trompés approuvent une rafale de paiements à un nouveau bénéficiaire sur notre portefeuille de test Avalanche Fuji.

## Responsabilités

Le client fixe le mode, le quorum, les délais et un responsable d'incident avec suppléant. L'agent analyse et relève le risque ; le responsable coordonne la vérification. Les signataires humains annulent, gèlent, remplacent les clés et autorisent la reprise. Aucun signalement Web ne doit être traité comme un jugement de culpabilité.

## Marche à suivre

| Étape | Automatique | Action humaine | Preuve / fin d'étape |
|---|---|---|---|
| Détecter | Relais lit la proposition ; règles / modèle / agent analysent ; oracle cherche les éléments disponibles. | Responsable vérifie montant, adresse complète et contexte métier. | Identifiant du paiement, codes des règles, sources et horodatages. |
| Contenir | Risque moyen : signature supplémentaire. Risque élevé : attente et quorum renforcé. En cosignataire : refus de signature et signalement, sans veto définitif. | Prévenir les collègues par un canal indépendant ; en cas de doute, ne pas signer. Geler les paiements si plusieurs propositions sont suspectes. | Transaction RiskFlagged, notification, état et échéance du contrat. |
| Vérifier | Le dashboard explique les faits et conserve la chronologie. | Vérifier la facture directement auprès du prestataire via un contact déjà connu. Ne pas se fier à un contact reçu dans le message suspect. | Confirmation indépendante, vrai / faux positif consigné. |
| Éradiquer | Aucune suppression automatique de clé humaine. | Annuler les propositions frauduleuses. Clé volée : utiliser sa clé d'identité froide ; collègues annulent les opérations. Retirer les autorisations compromises et contrôler le carnet. | Tx d'annulation / révocation ; probation de la nouvelle clé. |
| Rétablir | Contrat vérifie quorum, délai, probation et gel. | Si faux positif : dérogation humaine renforcée après délai ; ne pas affaiblir le garde immédiatement. Si contrainte : collègues résolvent le gel, annulent le paiement concerné et créent une proposition propre. | Paiement autorisé après vérification ; contrôle du solde et test d'un paiement légitime. |
| Documenter | `score.rapport` construit les faits à partir des journaux ; synthèse de secours si Bedrock indisponible. | Responsable valide le rapport et décide de la classification réglementaire / de la notification applicable. | Rapport daté, hashes, montants tentés / sortis / en attente, causes et actions correctives. |

La démo utilise 30 s d'examen et 180 s d'attente ; ce ne sont pas des recommandations universelles. L'unanimité peut raccourcir l'attente d'un paiement ordinaire jusqu'au délai initial, jamais rendre exécutable une proposition signée sous contrainte. Configurer le quorum pour que les humains seuls puissent exercer le dernier recours.

## Pannes et fausses alertes

- Bedrock indisponible : règles et explication déterministe continuent ; l'agent utilise son plancher de risque. Vérifier l'état du relais et le traitement effectif des décisions.
- RPC / relais indisponible : vérifier les transactions dans l'explorateur ; ne pas supposer qu'une alerte affichée est déjà on-chain. Suspendre les nouvelles opérations sensibles jusqu'à restauration.
- Source Web erronée : conserver la preuve initiale, contester, obtenir une corroboration indépendante ; retirer le signalement par la procédure prévue, sans effacer la trace d'incident.
- Éviter toute collecte de secrets ou données personnelles dans le rapport. Les jeux du hackathon sont synthétiques ; le dashboard et le relais restent locaux.

## Mesures à relever à chaque exercice

Temps proposition -> alerte locale -> inscription on-chain -> notification -> annulation/reprise ; taux hold et step_up séparés ; faux hold sur paiements normaux ; montants mis en attente et montants réellement sortis ; disponibilité RPC / modèle ; succès du dernier recours humain. Le temps de réponse humain n'a pas encore été mesuré. Les chiffres synthétiques ne constituent pas une garantie de protection.

## Référentiels

[NIST CSF 2.0](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=957258) : Detect (analyse), Respond (confinement, vérification et communication), Recover (reprise) ; Protect (quorum, délai, clés séparées).

[MITRE ATT&CK T1078 - Valid Accounts](https://attack.mitre.org/techniques/T1078/) : rapprochement avec l'usage abusif d'identités valides, adapté au contexte de signataires Web3 ; nous ne prétendons pas détecter toutes les techniques associées. [MITRE ATLAS AML.T0051](https://atlas.mitre.org/techniques/AML.T0051) : injection de prompt dans les pages Web ou les libellés ; garde-fous, citations vérifiées et risque minimal indépendant du LLM.

## Conformité - support du track

Le rapport fournit une chronologie et des preuves pour le responsable d'incident ; ce n'est pas une certification DORA, une classification juridique automatique fiable ni une déclaration envoyée au régulateur. L'applicabilité de DORA, MiCA, LCB-FT et AI Act doit être examinée selon le client et les droits effectifs du service. L'agent peut influer sur le risque et cosigner : dire que le LLM « ne décide rien » serait incorrect. La qualification hors garde de fonds reste à valider ; la démo détient des jetons fictifs dans son contrat.
