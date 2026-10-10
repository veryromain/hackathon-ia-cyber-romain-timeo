# B1 — Bilan de la démo : ce qui marche, ce qu'on garde, enlève, modifie, améliore

> **Décisions de Romain prises le 10/10 à 20:39** (sections 2, 3, 4 et 7). Reste à Timéo : son avis sur le contrat (probation) et le module Safe, et à Romain le ressenti sur le tableau de bord. Base : démo de bout en bout en local (18:40) et sur Fuji (19:29), mesures de `shared/mesures.md`, jeu de généralisation de Timéo (19:47).
> Ce bilan répond à la question de la phase business : **l'outil fait-il ce qu'on promet, et qu'est-ce qui doit changer avant de le vendre ?**

## 1. Ce qui marche (à garder tel quel)

| Brique | Preuve | Verdict |
|---|---|---|
| **La réponse appliquée par le contrat du client** (signature en plus, mise en attente, gel, plafond) | 0 mUSD perdu sur 280 500 tentés, en local et sur Fuji ; sans le garde, 95 000 sortaient | ✅ **Cœur du produit.** Conforme au conseil du mentor : nous ne détenons aucun pouvoir sur les fonds |
| **La détection par règles explicables** | 100 % des fraudes du test freinées ou arrêtées, 0,9–1,6 % de faux positifs ; chaque alerte cite ses raisons et ses transactions | ✅ Garder. L'explicabilité est un argument conformité (AI Act) |
| **Le relais chaîne ↔ moteur** | A marché du premier coup sur Mac, PC Windows et Fuji ; signalement en ≤ 1 s (local) / 5–6 s (Fuji) | ✅ Garder pour la démo ; **à remplacer** en production par un module Safe (voir § 4) |
| **L'oracle Web2 → Web3 avec citation vérifiée** | 100 % précision / rappel sur 35 adresses, 7 injections déjouées, empoisonnement par source répétée rejeté | ✅ **Différenciateur n° 1.** Garder, étendre aux vraies sources (§ 4) |
| **Les explications et le rapport Bedrock, vérifiés par le code** | 0 fait inventé sur toutes les alertes et le rapport ; résiste aux libellés à injection | ✅ Garder. « Trust but verify » est un bon argument jury |
| **Le tableau de bord avec actions** | Valider / annuler / geler / contester testés sur la chaîne | ✅ Garder, c'est ce que le jury verra |

## 2. Ce qui ne marche pas assez (à modifier)

| Faiblesse | Constat | Décision prise (10/10, 20:00) |
|---|---|---|
| **Fraude « Bybit »** (intrus installé comme signataire, puis vidage) | Seulement freinée dans 3 cas sur 7 sur le jeu de généralisation ; une signature de plus n'arrête rien si l'attaquant tient 3 clés | ✅ **Décidé : les deux volets.** **Moteur :** clé de moins de 7 jours + gros montant vers un inconnu → mise en attente ; une clé neuve qui apporte la signature manquante re-déclenche l'alerte (fait, 20:00). **Contrat (Timéo) :** *période de probation* des clés neuves, qui ne comptent ni pour les signatures supplémentaires ni pour le dégel |
| **Mise en confiance** (2 petits paiements puis le gros) | Le gros paiement n'est que freiné : le destinataire est devenu « connu » | ✅ **Décidé : garder.** **Fait :** un destinataire reste « récent » 30 jours et moins de 3 paiements ; montant > 5 × ce qu'il a reçu → mise en attente |
| **Fractionnement** (6 à 8 petits paiements vers des adresses différentes) | Chaque paiement pris seul est petit | ✅ **Décidé : garder dans le moteur, rien de plus dans le contrat ce week-end.** **Fait :** cumul du jour vers ≥ 3 adresses récentes au-dessus des gros paiements habituels → mise en attente |
| **Surpaiement d'un vrai fournisseur** (10 à 20 ×) | Seulement freiné | ✅ **Décidé : garder, seuil réglable par le client** dans les limites du § 7. **Fait :** ≥ 10 × l'habitude du destinataire → mise en attente à lui seul (coût : les grosses factures annuelles passent plus souvent en attente, seuil réglable par le client) |
| **Généralisation** | 95 % freinées, 51 % arrêtées, 65 % des montants sur des formes jamais vues | ✅ **Décidé : mesure finale sur le 4ᵉ jeu, montrée telle quelle, même si elle est moins bonne.** Corrections ci-dessus, **mesurées sur un 4ᵉ jeu à nouvelles graines (Timéo)**, jamais sur celui qu'on a regardé |
| **Faux positifs sur les nouveaux fournisseurs** | 36–57 % des gros premiers paiements à un nouveau prestataire en attente après corrections | ✅ **Décidé : assumé et présenté comme une fonctionnalité** (vérification de tout nouveau bénéficiaire, comme une banque). Si les entretiens B5 disent non : seuil de `hold` à 0,8 pour ce cas. **À confirmer par les entretiens clients (B5)** : acceptent-ils 24 h d'attente sur un premier paiement important ? |
| `OFF_HOURS` un samedi | Déclenché sur la démo du week-end | **Levé pour la démo (décision Romain, 20:25)**, en tant que **réglage client** : jours et heures ouvrés dans `ia-1/config/client.demo-samedi.json`. La détection du week-end reste disponible (réglage par défaut : lundi–vendredi, 7h–20h) |

## 3. Ce qu'on enlève ou qu'on n'a pas fait (et qu'on assume)

**Décisions prises (Romain, 20:25) : deux seulement.**
- ✅ **Scraping de vrais sites : non pendant le hackathon.** À la place, **une source publique en lecture seule** (liste ouverte d'adresses signalées ou de sanctions) chargée dans le registre, pour prouver que l'oracle n'est pas une maquette.
- ✅ **Blocage d'une adresse ou d'un paiement : jamais.** Principe inscrit dans la slide conformité : « l'outil ne peut que ralentir ».

Les autres lignes ci-dessous sont des constats, pas des décisions.


- **Fraude bancaire classique, voix clonées, faux KYC** : hors périmètre, décidé à 16:35.
- **Blocage** d'une adresse ou d'un paiement : jamais. Friction seulement (conseil du mentor, réponse à « qui est responsable »).
- **Scraping de vrais sites** : démo sur pages synthétiques ; conditions d'utilisation et RGPD à traiter avant.
- **Traçage des fonds à plusieurs sauts** : volontairement limité à 1 intermédiaire (effet boule de neige).
- **Signalement à l'émetteur du stablecoin** : écarté par Romain.
- **Modèle d'anomalie sous Windows** : bloqué par la machine de Timéo, pas par le code ; argument chiffré seulement.

## 4. Ce qu'il faut améliorer avant de vendre (feuille de route)

**Toutes les décisions ci-dessous sont prises (Romain, 20:25).** Pendant le hackathon : (1) module Safe = slide d'architecture, pas de code ; (2) signature navigateur = feuille de route ; (3) **notifications : le minimum visible, un e-mail ou un message Telegram à chaque mise en attente** si le temps le permet ; (4) une source publique pour l'oracle ; (5) **mode observation + bouton « vraie / fausse alerte » = condition de vente** (« on signe sur vos chiffres, pas sur les nôtres »), bouton dans le dashboard ce soir ; (6) réglages client = slide, la logique existe ; (7) probation des clés neuves = contrat, ce soir (Timéo).


1. **Module Safe** à la place de notre multisig et de notre relais : les clients y sont déjà (Guard de Safe, service de transactions). C'est aussi ce que fait Hypernative Guardian ; notre différence : friction graduée sans blocage, petites organisations, oracle Web, **Avalanche uniquement**.
2. **Signature dans le navigateur** (le signataire signe avec son propre portefeuille) à la place du fichier d'actions de démo.
3. **Notifications** (e-mail de l'entreprise, Slack, Telegram) : aujourd'hui, il faut regarder l'écran.
4. **Vraies sources pour l'oracle** (Chainabuse, ScamSniffer, listes de sanctions) avec réputation apprise, et procédure de contestation.
5. **Mode observation** 2 à 4 semaines chez chaque nouveau client, puis **bouton « vraie / fausse alerte »** et rapport mensuel : la seule façon d'avoir des chiffres réels.
6. **Réglages par client** : signatures en plus, durée d'attente, seuils, liste de confiance, heures ouvrées.
7. **Probation des clés neuves** dans le contrat (voir § 2).

## 5. Ce que ça change pour la phase business

- **Le besoin à valider en entretien (B5) :** « accepteriez-vous qu'un premier paiement important attende 24 h et une signature de plus ? » et « qui, chez vous, reçoit l'alerte ? ».
- **Le prix se justifie** par le montant protégé (0 perdu sur 280 500 en démo, 97 % des montants frauduleux sur le test) contre un coût marginal de 0,002 $ par alerte.
- **Les concurrents à étudier d'abord (B4) :** Hypernative Guardian (le plus proche), Safe Shield, Fireblocks.

## 6. À compléter

- [ ] Timéo : ton avis sur chaque ligne, surtout § 2 (contrat) et § 4 (module Safe).
- [ ] Romain : ce que tu as ressenti en manipulant le tableau de bord (clarté des explications, ce qui manque).
- [ ] Les deux : décision go / ajustement (B8) après les entretiens (B5).

## 7. Les réglages du client et le conflit d'intérêts (question de Romain, 20:25)

**Le conflit existe** : un client peut desserrer ses seuils pour avoir moins de friction puis nous reprocher une fraude ; et celui qui règle peut être le fraudeur ou son complice (la forme de Bybit appliquée aux réglages). **Parades retenues :**
1. **Un réglage n'est jamais changé par une personne seule** : il passe par le portefeuille, comme un paiement (proposition, signatures, délai). Déjà le cas dans le contrat pour le seuil de signatures et le remplacement de signataire ; à étendre aux seuils de montant.
2. **Un changement de réglage est un signal pour le moteur** (`THRESHOLD_LOWERED` pèse déjà dans le score).
3. **Des planchers fixés par l'éditeur**, en dessous desquels le client ne peut pas descendre (ex. : mise en attente dès 5 × l'habitude, au moins une signature en plus).
4. **Tout réglage est inscrit sur la chaîne et figure dans le rapport mensuel** : l'auditeur voit qui a desserré quoi, et quand.
5. **Responsabilité contractuelle** : garantie dans les planchers ; au-delà de nos recommandations, le client accepte le risque, et c'est tracé.

Phrase pour le jury : *« le client règle sa tolérance, mais jamais seul, jamais en dessous de nos planchers, et toujours sous les yeux de ses signataires et de son auditeur. »*

## 8. Corrections du contrat après ce bilan — 2026-10-10 21:16, Codex / Timéo

À la demande de Timéo d'améliorer les faiblesses grâce aux documentations concurrentes : **probation de deux jours implémentée**, délai de gouvernance préservé même à l'unanimité, anciennes approbations invalidées lors du retrait/réajout d'une adresse. **30 tests locaux passent (10 nouveaux).** Les interfaces du relais restent compatibles et l'ABI est actualisée. **Pas encore déployé sur Fuji.**

Les corrections du moteur de Romain et les jeux de mesure sont conservés. Cela ne démontre pas une hausse de nos taux de détection. Les gros premiers paiements, le mode observation, le module Safe et la récupération indépendante restent des points à valider ou à construire selon les sections précédentes. Détails des garanties, limites et inspirations Squads / Safe / Fireblocks / Blockaid : [améliorations après bilan](ameliorations-apres-bilan.md).
