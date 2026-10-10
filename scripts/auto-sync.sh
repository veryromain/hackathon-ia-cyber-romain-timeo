#!/bin/bash
# Synchronise le repo avec GitHub : récupère le travail des autres, commite et pousse le nôtre.
# Appelé automatiquement par Claude Code (hook Stop) à la fin de chaque réponse.
# Usage manuel : ./scripts/auto-sync.sh "message de commit"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO" || exit 0
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# Sécurité : ne jamais pousser de secrets
if git status --porcelain | awk '{print $2}' | grep -v '\.example$' | grep -E '(^|/)\.env($|\.)|\.pem$|\.key$' >/dev/null; then
  echo '{"systemMessage": "auto-sync : fichier sensible détecté (.env/.pem/.key), synchro annulée"}'
  exit 0
fi

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "${1:-[auto] Mise à jour $(date '+%d/%m %H:%M')}"
fi

if ! git pull -q --rebase --autostash origin main 2>/dev/null; then
  # Conflits sur JOURNAL.md / SUIVI.md (écrits par les deux en même temps) : résolution automatique.
  while [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; do
    conflits=$(git diff --name-only --diff-filter=U)
    autres=$(echo "$conflits" | grep -vE '^(JOURNAL|SUIVI)\.md$' | grep -v '^$')
    if [ -n "$autres" ] || ! python3 scripts/resoudre-conflits.py $conflits; then
      git rebase --abort 2>/dev/null
      echo '{"systemMessage": "auto-sync : conflit avec GitHub, à résoudre à la main"}'; exit 0
    fi
    git add $conflits && GIT_EDITOR=true git rebase --continue >/dev/null 2>&1 || true
  done
fi
git push -q origin main 2>/dev/null || echo '{"systemMessage": "auto-sync : push vers GitHub échoué (connexion gh ?)"}'
exit 0
