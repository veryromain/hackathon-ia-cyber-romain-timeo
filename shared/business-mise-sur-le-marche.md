# B7 — Mise sur le marché (feuille de route 6 mois) et B8 — Décision go / ajustement

> Romain (avec Claude), 11/10 vers 08:30. Assemble B1 à B6 en une feuille de route datée et une décision. Même règle : chaque chiffre renvoie à sa source ou à son calcul (`shared/business-marche.md` D1-D11, `shared/business-prix.md`, `shared/mesures.md`, `shared/audit-contrat.md`). Les hypothèses sont nommées (H3-H4 viennent de B3, H9-H10 sont nouvelles).

## 1. Le canal : par où entrent les clients, dans l'ordre
| Ordre | Canal | Pourquoi dans cet ordre | Chiffre associé |
|---|---|---|---|
| 1 | **Écosystème Avalanche** : présentations par Team1 et la Fondation (mentors du hackathon), cohorte Retro9000, équipes de L1 servies par Ash Wallet | le seul canal où quelqu'un nous présente ; il porte tout l'entonnoir du SOM | 62 organisations contactables (C : 30 + 10 + 22, B3 § 3) |
| 2 | **Catalogue d'applications Safe** (Safe Apps) | libre-service là où tous nos clients sont déjà ; gratuit ; entrées spontanées non chiffrables | 61 M de comptes Safe (S : Safe Foundation T1 2026) ; part sur Avalanche inconnue |
| 3 | **Auditeurs et analyses publiques d'incidents** | prescripteurs : un auditeur recommande une protection d'exploitation après son audit ; chaque incident public est une occasion de montrer ce que Breaker aurait vu (rejeu Bybit / Drift, chantier Timéo) | introduction demandée aux mentors (S : `shared/audit-contrat.md` § 5) |
| 4 | **Démo sur demande** pour grands comptes (palier Premium / Entreprise) | en second : une vente assistée coûte du temps fondateur ; on la réserve à > 10 M$ | Fireblocks Essentials 999 $/mois comme repère (D9) |

## 2. Le parcours client (décidé le 10/10, chiffré ici)
1. **Connexion en libre-service** : l'organisation branche Breaker sur son Safe (lecture seule) ; carnet d'adresses construit depuis l'historique.
2. **Observation gratuite 30 jours** : alertes et explications, rien ne change à ses paiements ; rapport de fin d'observation (ce qu'on aurait freiné, faux positifs). C'est aussi notre seule source de **données réelles** (décision B1 § 4.5).
3. **Activation de la friction** : un clic, choix d'un profil (prudent / standard / réactif) avec planchers, abonnement mensuel sans engagement (B6).
4. **Rapport mensuel + bouton « vraie / fausse alerte »** : la boucle qui améliore le moteur et prouve la valeur au renouvellement.

## 3. Feuille de route datée (du 12 octobre 2026 à avril 2027)
| Quand | Produit (Timéo) | Marché (Romain) | Jalon mesurable |
|---|---|---|---|
| **Oct. 2026** (semaines 1-3) | corrections cosmétiques du contrat ; notifications e-mail / Telegram ; rejeu Bybit / Drift sur données réelles | dépôt public (livrable L8) ; demande d'introduction aux 62 organisations via Team1 / Fondation ; dossier subvention Avalanche (Retro9000) et Bpifrance | **≥ 10 organisations en observation** d'ici fin octobre (C : moitié des 20 premières approchées, H4) |
| **Nov.-déc. 2026** | **portage de la garde en Safe Guard** (`checkTransaction`), signature dans le navigateur, sources d'oracle en réputation apprise | observation sur ≥ 20 organisations ; premiers rapports de fin d'observation ; **mesure de H4** (part qui accepte l'essai) et du taux de faux hold réel | **H4 mesurée** ; faux hold réel < 5 % (jeu final : 5,1 %, `shared/mesures.md`) |
| **Janv. 2027** | gel du contrat ; **audit externe** (ordre de 10 à 25 k$, non devisé, financé par la subvention) ; prime aux bugs ensuite | **premiers clients payants** : 3 à 6 attendus (C : 31 × 8,9-18,5 %, B3 § 3) ; publication du catalogue Safe Apps | **premier client payant après l'audit**, jamais avant (décision `shared/audit-contrat.md`) |
| **Févr.-mars 2027** | déploiement sur une 2e chaîne EVM (Base ou Arbitrum : même code Solidity) ; mode Cosignataire (Premium) | ouverture EVM : SAM × 6 à 8 (C : 675-895 / 32-121) ; partenariats auditeurs | **10 clients payants** ; taux de conversion observation → payant mesuré (remplace D10) |
| **Avr. 2027** | — | revue du prix avec les données réelles (B8 bis) ; 2e écosystème EVM abordé | **point mort à 10 clients Standard visé entre le T3 2027 et la mi-2028** (§ 3 bis) |

### 3 bis. Quand le point mort est-il atteignable ? (recalculé le 11/10 à 09:40 : fondateurs à 2 000 €)
Coûts fixes révisés par Romain : 2 × 2 000 € + 300 € = **4 300 €/mois** → point mort à **10 clients Standard** (C : 4 300 / 449 = 9,6), ou 5 Premium, ou 1 Premium + 8 Standard.
Entonnoir à l'envers, avec les mêmes taux : 10 clients ÷ 8,9-18,5 % (D10) = **54 à 112 organisations en observation** ; ÷ 50 % (H4) = **108 à 225 organisations à contacter**. Avalanche en fournit **62** d'ici décembre 2026 (B3 § 3).
- **Levier 1, rythme d'écosystèmes (H11)** : chaque écosystème EVM abordé rapporte comme Avalanche (62 contactables par semestre via sa fondation et son programme de subventions) : il faut **1 à 3 écosystèmes de plus**, soit un point mort entre le **T3 2027** (conversion à 18,5 %) et la **mi-2028** (conversion à 8,9 %). Avant la révision (7 300 €/mois, 17 clients), c'était T4 2027 à T2 2028 avec 3 à 6 écosystèmes.
- **Levier 2, mix de paliers** : un seul client Premium (990 €) remplace 2,2 clients Standard et avance la date d'un trimestre : la démo sur demande reste un canal.
- **Ce qu'on dit au jury** : « coûts fixes 4 300 € par mois, deux fondateurs à 2 000 € ; point mort à 10 clients, entre le T3 2027 et la mi-2028 selon la conversion ; plus tôt avec un client Premium ».

**Mesure de H4** : part des organisations présentées qui branchent Breaker en lecture seule dans les 30 jours = connectées ÷ présentées, sur les 62 du canal Avalanche. Précision à 95 % : ± 12 points (C : 1,96 × √(0,5 × 0,5 / 62) = 0,124), suffisante pour distinguer 50 % du signal d'arrêt à 25 %. Se mesure avant tout développement du Guard.

**H9** : la subvention couvre l'audit et neuf à douze mois de coûts fixes jusqu'au point mort (ordre de 50 à 75 k€ : 10-25 k$ d'audit + 4 300 €/mois × 9 à 12 ; montant Retro9000 et Bpifrance **non vérifiés**, à demander aux mentors). **H10** : le portage Safe Guard prend 6 à 8 semaines à un développeur (estimation de Timéo à confirmer ; la doc Safe prévoit le mécanisme, le risque est d'intégration, pas de concept).

## 4. B8 — Décision : **GO, avec quatre ajustements**
**Le besoin est-il confirmé ?** Par les faits, oui : les plus grosses pertes de 2025-2026 viennent de signataires trompés ou de clés compromises dans le processus de signature (Bybit 1,46 Md$, Drift ≈ 280 M$, `shared/business-probleme.md`), et nos cibles n'ont pas d'équipe pour y répondre. Par les clients, **pas encore** : aucun entretien n'a été mené (B5 non fait). La décision est donc un **go d'amorçage** : on investit dans l'observation gratuite, qui est précisément le moyen de confirmer le besoin avec des données, pas avec des avis.

**Les quatre ajustements décidés ce week-end (et pourquoi)**
1. **Hybride au lieu de bloquer ou freiner** : Protection (attente + signature en plus) par défaut, Cosignataire (refus avec dérogation humaine) en Premium ; jamais de veto définitif. Pourquoi : un faux blocage coûte au client, un faux ralentissement non ; et c'est ce qui rend l'avertissement de Safe sur les Guards sans objet pour nous (décision Timéo 01:25, `shared/decisions.md`).
2. **Cible gardée, risques notés** : organisations sans équipe sécurité, trésorerie ≥ 1 M$. Risque : marché Avalanche étroit (32-121), d'où la portabilité EVM en mars 2027.
3. **Prix ancré sur la valeur, Safe Pro comme repère** : 0 / 149 / 449 / 990 € ; Breaker est un service de sécurité à part entière qui se branche sur le Safe existant, pas un « complément » (décision Romain 11/10 08:00).
4. **Audit externe avant le premier euro encaissé**, financé par subvention ; d'ici là, analyse statique + 50 tests + fuzzing publics (`shared/pitch-argumentaire-audit.md`).

**Ce qui nous ferait réviser (signaux d'arrêt, à relire en avril 2027)**
- H4 mesurée **< 25 %** (moins d'une organisation sur quatre accepte l'observation gratuite) : le problème n'est pas ressenti ; revoir la cible (entreprises classiques payant en stablecoins ?) ou le canal.
- Conversion observation → payant **< 5 %** (sous le plancher des benchmarks D10) : revoir le prix ou l'offre (Essentiel trop proche de Safe Shield gratuit ?).
- Faux hold réel **> 10 %** sur les données d'observation : le moteur n'est pas prêt à vendre ; prolonger l'observation.
- Safe Labs lance une détection comportementale incluse dans Safe Pro : accélérer le portage Guard et jouer la personnalisation + protection de la personne (clé d'identité, contrainte), que Safe n'a pas.

## 5. Les trois phrases pour la slide « go-to-market »
1. « Le client a déjà le coffre : Breaker se branche dessus en 5 minutes, observe gratuitement 30 jours, puis s'active en un clic. »
2. « Première année : 62 organisations présentées par l'écosystème Avalanche, 3 à 6 clients payants, l'audit externe avant le premier euro. »
3. « Coûts fixes 4 300 € par mois : point mort à 10 clients, entre le T3 2027 et la mi-2028 en abordant un écosystème EVM par semestre, le même code tournant sur toute chaîne compatible ; plus tôt avec un seul client Premium. »
