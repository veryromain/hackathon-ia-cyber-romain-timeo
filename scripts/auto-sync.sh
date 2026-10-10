#!/bin/bash
# Synchronise le repo avec GitHub : récupère le travail des autres, commite et pousse le nôtre.
# Appelé automatiquement par Claude Code (hook Stop) à la fin de chaque réponse.
# Usage manuel : ./scripts/auto-sync.sh "message de commit"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO" || exit 0
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# Sécurité : ne jamais pousser de secrets
if git status --porcelain | awk '{print $2}' | grep -E '(^|/)\.env($|\.)|\.pem$|\.key$' >/dev/null; then
  echo '{"systemMessage": "auto-sync : fichier sensible détecté (.env/.pem/.key), synchro annulée"}'
  exit 0
fi

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "${1:-[auto] Mise à jour $(date '+%d/%m %H:%M')}"
fi

git pull -q --rebase --autostash origin main 2>/dev/null || { git rebase --abort 2>/dev/null; echo '{"systemMessage": "auto-sync : conflit avec GitHub, à résoudre à la main"}'; exit 0; }
git push -q origin main 2>/dev/null || echo '{"systemMessage": "auto-sync : push vers GitHub échoué (connexion gh ?)"}'
exit 0
