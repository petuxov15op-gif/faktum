#!/usr/bin/env bash
# Safely save the current project state to GitHub.

set -euo pipefail

cd "$(dirname "$0")"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: this folder is not a Git repository."
  exit 1
fi

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "ERROR: no current Git branch."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "ERROR: GitHub remote 'origin' is not configured."
  exit 1
fi

git add -A

if git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi

message="${1:-chore: sync changes $(date '+%Y-%m-%d %H:%M')}"
git commit -m "$message"

git pull --rebase origin "$branch"
git push -u origin "$branch"

echo "Published to GitHub."
