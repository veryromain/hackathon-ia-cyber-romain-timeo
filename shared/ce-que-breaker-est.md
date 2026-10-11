# Ce que Breaker est, et ce qu'il n'est pas : un greffon sur le coffre du client, pas un coffre

> Romain (avec Claude), 11/10 vers 08:55. Réponse à la question de Romain : « avons-nous bien mis en évidence que nous ne sommes pas un coffre, mais un Guard greffé sur le coffre existant du client ? ». Réponse : **non, pas assez** ; ce document fixe la formulation à reprendre partout (README, tableau de bord, en-tête du contrat, pitch) et dit honnêtement où en est le code.

## 1. La phrase à retenir
**Breaker ne garde pas vos fonds. Il se greffe sur le coffre que vous avez déjà (votre Safe) et agit à partir de vos réglages : il regarde chaque paiement, et quand quelque chose ne colle pas, il demande une signature de plus ou impose une attente, jamais plus.** Le moniteur ne peut pas transférer de fonds ; cela ne garantit pas l’absence de pertes ou de blocage causés par un bug du contrat. Le prototype détient des jetons fictifs ; le greffon Safe reste à développer.

## 2. Ce que la démo montre, honnêtement
Le code d'aujourd'hui (`ia-2/contracts/TreasuryGuard.sol`) est **un coffre de démonstration avec la garde dedans** : un multisig M-sur-N complet, parce qu'en 36 heures il fallait une chaîne réelle (Fuji) pour prouver la logique de bout en bout. **Ce multisig tient lieu du Safe du client.** Le produit, ce n'est pas lui : c'est la garde (délais, signature en plus, attente, gel, probation des clés, clé d'identité, clé de contrainte) et le moteur hors chaîne (règles, modèle, oracle, explications, tableau de bord). Dans le pitch : « démontré sur un coffre de démonstration qui tient lieu de votre Safe ; portage en greffon Safe en feuille de route ».

## 3. L'architecture cible : greffon = Guard + Module de Safe
Safe prévoit deux points de branchement officiels (S : docs.safe.global, « Safe Guards », « Safe Modules ») :
| Brique Safe | Ce qu'elle permet | Ce qu'on y met |
|---|---|---|
| **Guard** : contrat appelé par le Safe **avant chaque transaction**, qui peut la refuser | freiner | délai de revue, signature en plus (StepUp : le Guard compte les signatures reçues et en exige plus que le seuil), mise en attente (Hold), gel, probation des clés neuves, refus pur des adresses sanctionnées si le client l'active |
| **Module** : contrat autorisé par les signataires à exécuter **certaines actions sans quorum** | agir en urgence | révocation de sa propre clé par la clé d'identité (`swapOwner`), levée de gel à l'unanimité |

**Ce qui se porte directement** (même logique, autre enveloppe) : délais, StepUp, Hold, gel, probation, clé d'identité, moteur, oracle, tableau de bord, et le principe « le moniteur ne peut qu'ajouter de la friction ».
**Ce qui demande une conception** : la **clé de contrainte** (une signature d'apparence normale qui gèle en silence) suppose que le Safe reconnaisse une seconde clé par signataire ; à concevoir dans le Module, ou à garder dans le portefeuille du signataire. On le dit tel quel si on nous le demande.
**Ce que ça change pour le client** : il garde son Safe, son adresse, ses signataires, son historique ; il installe Breaker comme il installe un Guard, et il le retire par la même procédure qu'un paiement (jamais en une transaction, décision Timéo). **Estimation du portage (H10) : 6 à 8 semaines, à confirmer par Timéo.**

## 4. Où la formulation doit apparaître (fait / à faire)
| Endroit | Formulation | État |
|---|---|---|
| Tableau de bord, sous le titre | « Breaker n'est pas un coffre : il se greffe sur votre multisig (ici, un coffre de démonstration qui tient lieu de votre Safe) et ne détient aucun fonds… » | fait (Romain, 11/10) |
| `README.md`, en tête | paragraphe « Ce qu'est Breaker » | fait |
| `CONTEXTE.md` | une ligne | fait |
| En-tête du contrat (`@title`, `@notice`) | « TreasuryGuard : garde antifraude greffée sur un multisig de trésorerie. Dans ce prototype, le multisig est inclus pour la démonstration ; en production, la garde se greffe sur le Safe du client (Guard + Module). » | **Timéo** (dans ses corrections cosmétiques) |
| Pitch, slide d'architecture | schéma : Safe du client → Guard Breaker → moteur hors chaîne → signataires | à faire (pitch) |
| Site vitrine (Timéo) | reprendre § 1 mot pour mot | **Timéo** |

## 5. Pourquoi c'est important devant le jury
- **Catégorie de risque** : un bug chez un dépositaire perd l'argent ; un bug chez nous retarde un paiement (`shared/pitch-argumentaire-audit.md`). Si on se présente comme un coffre, on perd cet argument.
- **Réglementation** : ne pas détenir les fonds nous tient hors de la garde d'actifs (MiCA) ; on serait prestataire tiers de services TIC (DORA), à confirmer avec le mentor KPMG (`shared/retour-mentor-team1.md`).
- **Commercial** : c'est ce qui rend l'essai gratuit possible (personne ne déplace sa trésorerie pour un essai) et ce qui nous distingue d'un portefeuille concurrent de Safe : nous ne sommes pas en concurrence avec le coffre, nous le complétons d'une surveillance qu'il n'a pas.
