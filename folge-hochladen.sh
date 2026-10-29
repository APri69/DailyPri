#!/usr/bin/env bash
# Legt eine MP3 als Folge in den Podcast DailyPri und veröffentlicht ihn.
#
# Aufruf (aus dem Repo heraus):  bash folge-hochladen.sh <datei.mp3> [JJJJ-MM-TT]
# Ohne MP3 (leeres erstes Argument "") wird nur Feed/Seite neu gebaut.
#
# Der Zweig gh-pages wird bei jedem Lauf OHNE Geschichte neu geschrieben
# (ein einziger Commit: Feed, Seite, Cover, Folgen der letzten 7 Tage).
# So wächst das Repo nicht mit jeder gelöschten Folge weiter.
set -euo pipefail
trap 'echo "FEHLER in Zeile $LINENO" >&2' ERR
cd "$(dirname "${BASH_SOURCE[0]}")"
echo "Ordner: $(pwd)"

MP3="${1:-}"
DATUM="${2:-$(TZ=Europe/Berlin date +%F)}"
echo "Start: Folge $DATUM"

ARBEIT="$(mktemp -d)"
SEITE="$ARBEIT/seite"
mkdir "$SEITE"

# Bisherigen Stand holen (beim allerersten Lauf gibt es gh-pages noch nicht)
if git fetch --quiet --depth 1 origin gh-pages 2>/dev/null; then
  git archive FETCH_HEAD | tar -x -C "$SEITE"
  echo "Bisheriger Stand geholt: $(ls "$SEITE" | wc -l | tr -d ' ') Dateien"
else
  echo "gh-pages gibt es noch nicht – fange leer an"
fi

if [ -n "$MP3" ]; then
  [ -s "$MP3" ] || { echo "MP3 fehlt oder ist leer: $MP3" >&2; exit 1; }
  cp "$MP3" "$SEITE/$DATUM.mp3"
fi
cp cover.png "$SEITE/cover.png"
touch "$SEITE/.nojekyll"

python3 feed_bauen.py "$SEITE" --heute "$DATUM"

# Einen Commit ohne Vorgänger bauen, ohne den Arbeitsordner anzufassen
GITDIR="$(git rev-parse --absolute-git-dir)"
export GIT_INDEX_FILE="$ARBEIT/index"
GIT_DIR="$GITDIR" GIT_WORK_TREE="$SEITE" git -C "$SEITE" add -A .
BAUM="$(GIT_DIR="$GITDIR" git write-tree)"
unset GIT_INDEX_FILE
COMMIT="$(git -c user.name="DailyPri" -c user.email="dailypri@users.noreply.github.com" \
  commit-tree "$BAUM" -m "Folge $DATUM")"

git push --quiet --force origin "${COMMIT}:refs/heads/gh-pages"

# Nachmessen: steht auf GitHub wirklich unser Commit?
AUF_GITHUB="$(git ls-remote origin refs/heads/gh-pages | cut -f1)"
if [ "$AUF_GITHUB" != "$COMMIT" ]; then
  echo "FEHLER: GitHub zeigt $AUF_GITHUB statt $COMMIT" >&2
  exit 1
fi
echo "Veröffentlicht: $COMMIT"
[ -n "$MP3" ] && echo "Folge: https://apri69.github.io/DailyPri/$DATUM.mp3"
echo "Podcast: https://apri69.github.io/DailyPri/"
rm -rf "$ARBEIT"
