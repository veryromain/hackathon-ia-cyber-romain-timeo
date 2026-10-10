# Améliorations après le bilan de Romain

Date : 2026-10-10 21:16. Demande de Timéo : corriger les faiblesses de `bilan-demo.md` à partir des documentations concurrentes. État : code et ABI actualisés, **30 tests locaux réussis ; aucun redéploiement Fuji effectué**.

## Faiblesses corrigées

| Faiblesse | Correction dans TreasuryGuard | Preuve locale |
|---|---|---|
| Deux clés compromises installent une troisième clé puis complètent le quorum renforcé (§2 du bilan) | Clé remplacée en probation pendant **2 jours**. Tous les votes d'un paiement risqué, d'un dépassement de plafond ou de la gouvernance doivent provenir de clés établies. Le dégel refuse une clé en probation. | Tests StepUp, Hold, plafond, baisse de seuil, dégel et frontière exacte des deux jours. Deux anciennes clés + une nouvelle ne suffisent pas ; une troisième ancienne clé permet toujours le paiement après le délai. |
| Le recours unanime aux paiements pouvait aussi raccourcir le délai de gouvernance (§7) | L'unanimité ne raccourcit que le délai d'un **paiement**. Changement de seuil et remplacement de clé gardent toujours `holdDelay`. | Même cinq approbations ne permettent pas de changer le seuil avant ce délai. |
| Retirer puis réajouter une adresse pouvait faire réapparaître un ancien vote | Numéro d'incarnation de clé, enregistré à chaque approbation de proposition ou de dégel. Le vote d'une incarnation retirée ne compte plus. | Tests retrait/réajout pour paiement et dégel ; une nouvelle approbation reste possible. |

Les clés initiales sont considérées établies au déploiement. Une nouvelle clé peut toujours proposer, approuver et exécuter un paiement ordinaire selon le quorum de base, ainsi que geler ou annuler : la probation cible les quorums renforcés. Une approbation de paiement donnée pendant la probation devient comptable à sa fin si la clé est encore active ; le dégel exige un nouveau vote après maturation.

## Ce que les concurrents nous apprennent

- **[Squads — Time Locks](https://docs.squads.so/main/navigating-your-squad/settings/time-locks)** : les transactions approuvées peuvent attendre un délai global. Application à Breaker : préserver notre délai de gouvernance au lieu de laisser une exception de paiement le contourner. Nous ne reproduisons pas le délai global de Squads.
- **[Fireblocks — Set Policies](https://fireblocks.readme.io/docs/set-transaction-authorization-policy)** : distinction politique active/brouillon et possibilité de revue avant publication ; ordre des règles restrictives. Application : traiter une baisse du seuil comme une décision sensible sous quorum et délai. Fireblocks permet aussi une publication directe : la revue n'est pas présentée comme obligatoire chez eux.
- **[Safe — Guards](https://docs.safe.global/advanced/smart-account-guards)** : contrôles avant/après exécution, avec risque de déni de service et nécessité d'audit/récupération. Application : garder l'exécution possible avec les anciennes clés établies et expliciter la disponibilité pendant la rotation. Nous n'avons pas implémenté un module Safe ni une récupération indépendante.
- **[Blockaid — Cosigner](https://blockaid.io/blog/cosigner-the-onchain-security-layer-your-multisig-is-missing-blind-signing)** : contrôle indépendant avant cosignature et recours humain. Application : conserver notre recours humain pour les paiements, sans l'étendre à la gouvernance ni donner de pouvoir de paiement au moniteur. La simulation de transactions est une prochaine brique, pas une fonction déjà livrée.

La probation de deux jours et le numéro d'incarnation sont **nos choix de mise en œuvre**, issus du bilan et de la revue du code. Ces sources ne démontrent pas que les concurrents appliquent exactement ces mécanismes.

## Validation et coût

Depuis `ia-2/` : `npm test` → 30 réussites (20 existants + 10 régressions sécurité), `npm run export-abi` → ABI actualisée, `npm run gas` → mesure Hardhat locale.

| Transaction | Gas local après correction |
|---|---:|
| Déploiement TreasuryGuard | 2 785 215 |
| Proposer un paiement | 243 681 |
| Approuver | 124 453 |
| Exécuter | 148 122 |
| Signaler StepUp / Hold | 42 394 / 45 890 |

Ces valeurs ne constituent pas une facture en dollars ni une nouvelle mesure Fuji. Les datasets train/test/holdout/final et les résultats de détection n'ont pas été modifiés ou réévalués pour améliorer artificiellement les chiffres.

## Limites restantes et suite

1. **Fuji utilise encore l'ancien contrat.** Pour tester la probation sur la chaîne : redéployer, actualiser carnet/adresses/liens de preuve, puis relancer un seul relais en coordination avec Romain. Les preuves de la démo actuelle restent celles de l'ancien contrat.
2. **Disponibilité :** étaler les rotations. Si trop de clés sont simultanément en probation ou expirées, le quorum renforcé peut être indisponible. Prévoir une durée de validité supérieure à deux jours ; aucune récupération indépendante n'est livrée. Ne pas baisser automatiquement le quorum pour contourner cette protection.
3. **Menace résiduelle :** trois anciennes clés compromises peuvent toujours satisfaire un quorum de trois. La probation n'arrête pas une compromission totale, ni un paiement ordinaire frauduleux que le moteur ne signale pas. Les signataires peuvent toujours annuler/geler les paiements.
4. **Faux positifs :** les gros premiers paiements restent mis en attente ; valider l'acceptabilité auprès des clients (B5) avant de changer les seuils. Le mode observation (P7) et le rapport mensuel restent à construire ; le bouton vraie/fausse alerte est déjà livré par Romain.
5. **Intégration produit :** module Safe, signature navigateur, simulation du résultat avant signature et récupération auditée restent dans la feuille de route du bilan. Les seuils de montant sont encore fixés au déploiement ; leur gouvernance dynamique n'est pas livrée.
6. **Pitch :** ne pas présenter Avalanche seul comme exclusivité. Blockaid propose déjà une intégration Avalanche/Core (voir la comparaison des concurrents). Le positionnement à défendre reste la friction graduée, l'oracle sourcé et l'offre pour les petites équipes de protocoles, DAO, startups crypto, fonds et fondations.
