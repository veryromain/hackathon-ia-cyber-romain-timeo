# Frais de gas du portefeuille et du garde (tâche T7)

Gas mesuré sur la chaîne locale par `cd ia-2 && npm run gas`, le 10 octobre à 16h52. Conversion au prix relevé au même moment : gas de la C-Chain d'Avalanche à 5,08 nAVAX (`eth_gasPrice` sur le RPC public), AVAX à 10,47 $ (CoinGecko, relevé à 16h17).

| Transaction | Qui paie | Gas | Coût en dollars |
|---|---|---|---|
| Signaler un paiement, niveau `StepUp` | Nous (le moniteur) | 42 394 | 0,002 $ |
| Signaler un paiement, niveau `Hold` | Nous (le moniteur) | 45 890 | 0,002 $ |
| Inscrire une adresse au registre | Nous (l'oracle) | 73 968 | 0,004 $ |
| Proposer un paiement | Le client | 217 168 | 0,012 $ |
| Approuver | Le client | 93 457 | 0,005 $ |
| Exécuter | Le client | 137 376 | 0,007 $ |
| Geler le portefeuille | Le client | 48 838 | 0,003 $ |
| Annuler un paiement | Le client | 35 336 | 0,002 $ |
| Déployer le portefeuille (une fois) | Le client | 2 359 819 | 0,13 $ |
| Déployer le registre (une fois) | Nous | 578 341 | 0,03 $ |

## Ce qu'il faut en retenir pour le modèle économique

- **Notre coût par alerte est d'environ 0,002 $.** Un client dont on signalerait 100 paiements par mois nous coûterait 0,24 $ de gas.
- **Lire la chaîne ne coûte rien** : le moniteur ne paie que lorsqu'il signale.
- Un paiement complet (proposer, approuver, exécuter) coûte environ 0,024 $ au client, garde compris.
- Le gas est donc négligeable dans le prix d'un abonnement, comme le disait le mentor Team1. Hypothèse de prix et cible : `shared/cible-et-modele-economique.md`. Le prix du gas varie avec la charge du réseau : même multiplié par cent, une alerte resterait sous 0,25 $.

## Limites de ces chiffres

- Mesures sur la chaîne locale de Hardhat ; le gas consommé sera le même sur Fuji et sur la C-Chain, seul son prix change.
- Le contrat n'est pas optimisé. Proposer un paiement coûte cher parce que le libellé est inscrit dans l'événement et que le portefeuille recompte les approbations valides.
- Les prix du gas et de l'AVAX sont des relevés ponctuels du 10 octobre, pas des moyennes.
