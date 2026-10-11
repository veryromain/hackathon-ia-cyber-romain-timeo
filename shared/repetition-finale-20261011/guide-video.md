# Répétition Fuji proche finale — 11 octobre 2026

Tableau de bord : http://localhost:8599 (données de cette répétition uniquement).
Portefeuille : https://testnet.snowtrace.io/address/0xcbd2E98884F187DD70EFFC5bec7285A0C1e9ef24

## Parcours pour la vidéo (2 à 3 minutes)

1. Paiement normal : 3 150 mUSD au prestataire connu, deux signatures, délai d'examen, exécution. Montrer l'événement d'exécution dans le journal de la chaîne.
2. Demande pressante : trois paiements vers un nouveau bénéficiaire, 280 500 mUSD au total. Montrer la raison et la marche à suivre, puis le risque inscrit sur Fuji. Deux signatures ne suffisent plus : il en faut trois.
3. Réponse humaine : un signataire gèle et annule les trois demandes. Montrer les liens de transaction ; aucun mUSD reçu par le fraudeur. Trois votes permettent ensuite le dégel.
4. Source Web publique : signalement OFAC collecté lors de la session précédente, réinscrit au nouveau registre. Paiement de 25 000 mUSD classé Hold à la proposition ; même avec trois signatures, l'attente reste applicable. Paiement annulé. Cette séquence ne constitue pas une nouvelle collecte IA.
5. Signature sous contrainte : la seconde clé donne une approbation visible, mais empêche le transfert et déclenche l'alerte privée. Les collègues restaurent la situation et annulent.
6. Rapport : ouvrir rapport-incident.md et montrer la chronologie et les preuves.

## Limites à annoncer

- Règles seules sur ce PC : Windows bloque sklearn _liblinear ; aucun modèle d'anomalie chargé. Aucun changement des poids pour obtenir ce résultat.
- Bedrock : jeton expiré au contrôle préalable. Explications déterministes, pas de nouvelle extraction LLM dans cette répétition.
- Les 8 signalements Web proviennent de la collecte publique précédente ; leurs sources et citations sont conservées.
- Les délais sont ceux de la démonstration : 30 secondes d'examen, 180 secondes d'attente.
- Protection fonctionne dans le prototype ; le futur mode Cosignataire, sa dérogation et le retrait du garde sont des choix de conception, pas un parcours déjà implanté.
- Démo synthétique sur nos contrats de test ; aucun taux d'efficacité de production ni montant réel sauvé n'en découle.

## Processus

processes.json contient uniquement les PID du relais, du moteur et du dashboard et le chemin du dossier. Un seul relais Fuji à la fois, sur PC OU Mac. Ne pas lancer un second relais avant l'annonce de libération dans JOURNAL.md.

Les résultats précédents sont préservés ; fuji-precedent.json contient le manifeste public antérieur. Le nouveau manifeste actif est ia-2/deployments/fuji.json.