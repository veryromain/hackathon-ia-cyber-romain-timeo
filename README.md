# Hackathon IA & Cybersécurité

Repo partagé pour suivre l'avancée de nos deux IA en parallèle.

## Ce qu'est Breaker
**Breaker ne garde pas vos fonds.** C'est une garde antifraude qui **se greffe sur le coffre multi-signatures que vous avez déjà** (votre Safe) et agit à partir de vos réglages : elle regarde chaque paiement et, quand quelque chose ne colle pas, demande une signature de plus ou impose une attente, jamais plus. Le pire bug possible est un faux ralentissement, pas une perte. Dans ce prototype, le multisig (`ia-2/contracts/TreasuryGuard.sol`) est inclus pour la démonstration et **tient lieu du Safe du client** ; le portage en greffon Safe (Guard + Module) est en feuille de route. Détail : `shared/ce-que-breaker-est.md`.

## Structure

| Dossier | Contenu |
|---|---|
| `ia-1/` | Code, prompts et résultats de l'IA n°1 |
| `ia-2/` | Code, prompts et résultats de l'IA n°2 |
| `shared/` | Données, outils et ressources communs aux deux IA |
| `JOURNAL.md` | Journal d'avancement commun (mis à jour par les deux) |
| `CONTEXTE.md` | Brief du hackathon : tracks, livrables, notation, format du pitch |
| `SUIVI.md` | **Tableau de suivi : qui fait quoi, quand, comment — tâches cochées au fil de l'eau** |
| `PLAN.md` | Plan d'action : scénario, architecture, planning, répartition, limites |
| `conversations/` | Comptes-rendus des conversations avec Claude (décisions, idées) |
| `scripts/auto-sync.sh` | Synchro auto avec GitHub (pull + commit + push) |
| `CLAUDE.md` | Instructions pour Claude (suivi des conversations, règles) |

## Règles de travail

- Chacun travaille dans son dossier (`ia-1/` ou `ia-2/`) pour éviter les conflits.
- `git pull` avant de commencer, commit + push souvent.
- Préfixer les commits : `[ia-1]`, `[ia-2]` ou `[shared]`.
- Ne jamais committer de clés API ou secrets (utiliser un fichier `.env`, ignoré par git).
