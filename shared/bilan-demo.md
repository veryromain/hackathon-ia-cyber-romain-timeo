# B1 — Bilan de la démo : ce qui marche, ce qu'on garde, enlève, modifie, améliore

> **Brouillon de Romain (avec Claude), 10/10 vers 20:05, à compléter et valider par Timéo et Romain.** Base : démo de bout en bout en local (18:40) et sur Fuji (19:29), mesures de `shared/mesures.md`, jeu de généralisation de Timéo (19:47).
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
| **Fraude « Bybit »** (intrus installé comme signataire, puis vidage) | Seulement freinée dans 3 cas sur 7 sur le jeu de généralisation ; une signature de plus n'arrête rien si l'attaquant tient 3 clés | **Moteur :** clé de moins de 7 jours + gros montant vers un inconnu → mise en attente ; une clé neuve qui apporte la signature manquante re-déclenche l'alerte (fait, 20:00). **Contrat (Timéo) :** *période de probation* des clés neuves, qui ne comptent ni pour les signatures supplémentaires ni pour le dégel |
| **Mise en confiance** (2 petits paiements puis le gros) | Le gros paiement n'est que freiné : le destinataire est devenu « connu » | **Fait :** un destinataire reste « récent » 30 jours et moins de 3 paiements ; montant > 5 × ce qu'il a reçu → mise en attente |
| **Fractionnement** (6 à 8 petits paiements vers des adresses différentes) | Chaque paiement pris seul est petit | **Fait :** cumul du jour vers ≥ 3 adresses récentes au-dessus des gros paiements habituels → mise en attente |
| **Surpaiement d'un vrai fournisseur** (10 à 20 ×) | Seulement freiné | **Fait :** ≥ 10 × l'habitude du destinataire → mise en attente à lui seul (coût : les grosses factures annuelles passent plus souvent en attente, seuil réglable par le client) |
| **Généralisation** | 95 % freinées, 51 % arrêtées, 65 % des montants sur des formes jamais vues | Corrections ci-dessus, **mesurées sur un 4ᵉ jeu à nouvelles graines (Timéo)**, jamais sur celui qu'on a regardé |
| **Faux positifs sur les nouveaux fournisseurs** | 36–57 % des gros premiers paiements à un nouveau prestataire en attente après corrections | Assumé (décision 3) : c'est la vérification de tout nouveau bénéficiaire. **À confirmer par les entretiens clients (B5)** : acceptent-ils 24 h d'attente sur un premier paiement important ? |
| `OFF_HOURS` un samedi | Déclenché sur la démo du week-end | Garder, mais le dire ; réglage client des heures ouvrées |

## 3. Ce qu'on enlève ou qu'on n'a pas fait (et qu'on assume)

- **Fraude bancaire classique, voix clonées, faux KYC** : hors périmètre, décidé à 16:35.
- **Blocage** d'une adresse ou d'un paiement : jamais. Friction seulement (conseil du mentor, réponse à « qui est responsable »).
- **Scraping de vrais sites** : démo sur pages synthétiques ; conditions d'utilisation et RGPD à traiter avant.
- **Traçage des fonds à plusieurs sauts** : volontairement limité à 1 intermédiaire (effet boule de neige).
- **Signalement à l'émetteur du stablecoin** : écarté par Romain.
- **Modèle d'anomalie sous Windows** : bloqué par la machine de Timéo, pas par le code ; argument chiffré seulement.

## 4. Ce qu'il faut améliorer avant de vendre (feuille de route)

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
