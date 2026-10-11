# B6 — Le prix et l'offre, justifiés par le marché, la valeur et les coûts

> Romain (avec Claude), 11/10 vers 01:50. Même règle qu'en B3 : chaque chiffre a une source (S), un calcul (C) ou une hypothèse nommée (H). Les données D1-D11 sont celles de `shared/business-marche.md`.

## 1. Les trois ancrages d'un prix

**A. Ce que le même acheteur paie déjà pour le même besoin (D8, D9).** Notre client a un Safe. Depuis le 8 octobre 2026, Safe lui vend Safe Pro : 189 €/mois (Starter) ou dès 669 €/mois (Business, avec les politiques de transaction). Au-dessus, Fireblocks à 999 $/mois. **Règle R1 : un complément de sécurité à Safe doit coûter moins que le palier Safe correspondant**, sinon le client arbitre contre nous. On se place à **70 à 80 % du palier Safe**.

**B. La valeur : ce que le client évite de perdre.**
- Probabilité qu'une organisation subisse un incident significatif dans l'année : C : 150 incidents significatifs en 2025 (D7, TRM) / population d'organisations avec ≥ 1 M$ ≈ 1 359 protocoles > 1 M$ + 220 DAO ≈ 1 579 (D1, D4) = **≈ 9,5 % par an**, borne haute (tous les incidents ne sont pas des fraudes de signataires ; **H5** : la part dans notre périmètre est inconnue, on la montre à 20 % et à 100 %).
- Perte médiane par incident : **1,3 M$** (D7, TRM ; Immunefi 1,5 M$ ; CertiK 104 k$ sur un périmètre plus large incluant les petits incidents).
- Part des montants frauduleux que Breaker met en attente : **91 %** sur des formes jamais vues (`shared/mesures.md`, jeu final).
- **Perte annuelle attendue évitée** : C : 9,5 % × 1,3 M$ × 91 % = **≈ 112 k$/an** si tout incident est dans notre périmètre ; **≈ 22 k$/an** si un incident sur cinq l'est (H5).
- Règle R2 (usage courant en sécurité) : **le prix ne doit pas dépasser ~10 % de la perte annuelle évitée** pour que le client n'hésite pas. Plafond : 2,2 k$ à 11 k$/an, soit **≈ 170 à 850 €/mois**.

**C. Les coûts, pour le plancher.**
| Poste | Calcul | Coût |
|---|---|---|
| Explication Bedrock d'une alerte | C : ≈ 1 200 tokens d'entrée × 5 $/M + 200 de sortie × 25 $/M (S : Opus 4.8, pricepertoken.com, spheron) | **≈ 0,011 $** |
| Rapport d'incident | C : ≈ 3 000 entrée + 600 sortie | ≈ 0,03 $ |
| Lecture d'une page par l'oracle | C : ≈ 2 000 entrée + 300 sortie | ≈ 0,018 $ |
| Alerte inscrite sur la chaîne | S : `shared/frais-gas.md` | 0,002 $ |
| **Par client et par mois** (H6 : 20 alertes, 2 rapports, 50 pages d'oracle) | C : 20 × 0,013 + 2 × 0,03 + 50 × 0,018 | **≈ 1,2 $** |
| Infrastructure (serveur, RPC, surveillance), **H7** | ordre de 100 à 300 €/mois, tous clients confondus | ≈ 5 à 15 €/client à 20 clients |

**Le coût marginal est négligeable (< 20 €/client/mois)** : le prix est entièrement dicté par A et B, pas par C. Les coûts fixes (deux fondateurs) déterminent le point mort (§ 3).

## 2. L'offre : trois paliers plus un, par taille de trésorerie

| Palier | Pour qui | Ce qui est inclus | Prix / mois HT | Justification |
|---|---|---|---|---|
| **Observation** | tout nouveau client, 30 jours | détection et explications en lecture seule, rapport de fin d'observation | **0 €** | D10 : l'essai gratuit sans carte est le parcours qui convertit en B2B ; c'est aussi notre preuve d'efficacité sur les données du client |
| **Essentiel** | 1 multisig, trésorerie < 1 M$ | friction (signature en plus, mise en attente), explications, listes publiques (OFAC, ScamSniffer), notifications | **149 €** | R1 : 79 % de Safe Starter (189 €) |
| **Standard** | jusqu'à 5 multisigs, 1 à 10 M$ | Essentiel + oracle Web, traçage des fonds, adresses sosies et pièges, clé d'identité, rapport mensuel | **449 €** | R1 : 67 % de Safe Business (669 €) ; R2 : 5,4 k€/an = 5 % de la perte évitée à périmètre complet, 25 % à périmètre H5 |
| **Avancé** | > 10 M$ ou plus de 5 multisigs | Standard + mode cosignataire (agent qui refuse, dérogation humaine), réglages sur mesure, support prioritaire, engagement de disponibilité | **990 €** | D9 : l'alternative à ce niveau est Fireblocks Essentials (999 $) |
| **Entreprise** | fonds, fondations, plusieurs entités | Avancé + audit, intégrations, contrat | sur devis | comme Safe Enterprise et Guardian |

Tous les paliers : sans engagement, mensuel, données exportables (décision « aucun verrou commercial »). Remise ≈ 10 % en annuel, comme Safe Pro (D8).

## 3. Rentabilité : point mort et chiffre d'affaires selon le SOM

**H8** : coûts fixes = deux fondateurs à 3 500 €/mois chacun + 300 € d'infrastructure = **7 300 €/mois**.
- **Point mort** : C : 7 300 / 449 ≈ **17 clients Standard** (ou 8 clients Avancé, ou 49 Essentiel).
- **SOM année 1 (B3)** : 3 à 6 clients payants par l'écosystème Avalanche → 16 à 32 k€/an : **l'année 1 ne couvre pas les fondateurs**. C'est attendu pour un amorçage ; il faut soit des subventions (Avalanche, Bpifrance, mentionnés par les mentors), soit l'ouverture EVM (× 6 à 8 sur le SAM) pour atteindre le point mort en année 2.
- **À 17 clients Standard**, la marge brute est > 95 % (coût marginal < 20 €).

## 4. Ce que le jury demandera
- **« Pourquoi 449 € ? »** Parce que le client paie déjà 669 € à Safe pour le palier qui inclut les politiques, qu'un complément doit coûter moins, et que 449 €/mois représente 5 % de la perte annuelle qu'il évite, borne basse.
- **« Pourquoi pas moins cher, vu votre coût marginal ? »** Parce que le prix vend la valeur, pas le coût ; et qu'en dessous de 100 €, Safe Shield gratuit suffit au client.
- **« Qui paie quoi dans l'équipe ? »** Le client paie l'abonnement ; nous payons le gas des alertes (0,002 $) et l'IA (0,01 $) : ça tient dans le prix sans ligne de frais cachée.
- **« Et si personne ne convertit ? »** Alors le mode observation nous aura quand même donné les données réelles, et on révise la cible ou le prix en B8. L'hypothèse H4 (50 % acceptent l'observation) est celle à tester en premier en B5.

## Sources
D8-D10 : voir `shared/business-marche.md` · Bedrock Opus 4.8 : https://pricepertoken.com/pricing-page/model/anthropic-claude-opus-4.6 (même grille 5 $/25 $) · https://www.spheron.network/blog/aws-bedrock-pricing-2026-managed-api-cost/ · gas : `shared/frais-gas.md` · efficacité : `shared/mesures.md`
