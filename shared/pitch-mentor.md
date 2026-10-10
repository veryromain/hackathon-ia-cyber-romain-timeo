# Pitch mentor Team1 — 2 minutes

À dire à l'oral, sans slides. Le but est d'obtenir un avis franc, pas de convaincre.

---

## 🎤 Le pitch (≈ 1 min 30)

**Le problème.**
En DeFi, un exploit se joue en quelques minutes. Drift, en avril 2026 : 31 retraits en 12 minutes, environ 280 M$ partis. Il y a eu des signes avant, et le vidage s'est étalé sur plusieurs transactions : il y avait une fenêtre pour agir, personne n'a coupé à temps.
Côté réglementaire, DORA oblige les acteurs financiers, y compris les prestataires crypto agréés MiCA, à détecter, classer et déclarer vite leurs incidents majeurs. Aujourd'hui, c'est manuel.

**Notre solution : « Breaker », un disjoncteur DeFi relié à la conformité.**
1. Un moniteur surveille un contrat en temps réel et calcule un score de risque à chaque bloc.
2. Quand un vidage démarre, il réagit de façon graduée : alerte, plafond de retrait, puis **pause automatique**. La pause passe par un rôle « gardien » aux pouvoirs bornés : il peut tout arrêter, mais il ne peut jamais toucher aux fonds.
3. L'incident est **classé selon DORA** et le rapport est **pré-rempli**. Chaque chiffre est relié à une transaction on-chain, et un auditeur peut tout vérifier.
4. **Redémarrer exige un humain.** L'IA arrête l'hémorragie, l'humain décide de la suite.

**La démo.**
Notre propre coffre sur **Avalanche Fuji**, avec du trafic normal puis une attaque simulée en plusieurs transactions. Dans une variante, l'attaque vient d'un **agent IA de trésorerie piégé** par un document empoisonné. On affiche le temps de détection, le % des fonds sauvés et le nombre de faux positifs.

**Ce qui est nouveau.**
La détection on-chain existe déjà (Forta, Hypernative, Hexagate). Ce qui manque, c'est le pont **incident on-chain → réponse automatique → déclaration réglementaire vérifiable**.

---

## ❓ Nos questions pour le mentor (le vrai but de l'échange)

1. **Le client :** un protocole DeFi pur n'est pas soumis à DORA. Pour vous, le bon client est-il un prestataire crypto agréé MiCA qui place de la trésorerie en DeFi, un protocole, ou un autre acteur ?
2. **La pause :** un rôle gardien qui met en pause, est-ce acceptable pour l'écosystème Avalanche, ou trop centralisé ? Comment les protocoles le font-ils aujourd'hui (multisig, timelock, ERC-7265) ?
3. **Le scénario :** quel type d'exploit étalé dans le temps serait le plus crédible à rejouer pour un jury ?
4. **Technique :** des pièges connus sur Fuji (faucet, limites du RPC public, indexation des événements) ? Un outil Avalanche à utiliser plutôt que de tout coder ?
5. **Le périmètre :** en 22 h et à deux, qu'est-ce que vous couperiez ?
6. **La variante agent IA piégé :** est-ce qu'elle renforce le projet ou est-ce qu'elle le disperse ?

---

## 🛡️ Réponses prêtes si le mentor challenge

- **« Une attaque en une seule transaction (flash loan) passe quand même. »** → Oui, et on l'assume. On cible les vidages étalés ou précédés de signes, qui sont nombreux (Nomad, Ronin, Drift). Pour l'attaque instantanée, la piste est la surveillance du mempool et des plafonds au niveau du contrat.
- **« Et si votre modèle se trompe ? »** → Le pire cas est une pause injustifiée : réversible, limitée dans le temps et levée par un humain. Le modèle ne peut jamais déplacer de fonds, et chaque décision est journalisée avec ses raisons.
- **« Vos données sont synthétiques. »** → Oui, c'est imposé par les règles du hackathon. On sépare le trafic d'entraînement du trafic de test, et on présente nos limites honnêtement.
