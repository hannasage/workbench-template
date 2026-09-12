#!/usr/bin/env bash
# Creates the Claude Code wiring that the neutral core does not carry: the
# instruction filename this harness reads, and its role and skill discovery
# paths. It installs no settings file, because the template ships no
# permissions: what this harness may run without asking stays your own choice.
# Run it from the workbench root after a clone. Running it again changes nothing
# and prints what it found.
set -euo pipefail

changed=0

# The workbench root is identified by the files the neutral core guarantees,
# not by this script's own path. A wrong working directory is the one mistake
# that would otherwise scatter symlinks across somebody's home directory, so it
# is checked before anything is written.
for marker in AGENTS.md agents skills; do
  if [ ! -e "$marker" ]; then
    echo "error: run this from the workbench root. Not found here: $marker" >&2
    exit 1
  fi
done

# link <path> <target>. Creates one symlink, or reports that it is already
# right. An existing path of any other kind stops the run: it may be a file
# somebody wrote on purpose, and this script never overwrites one.
link() {
  path=$1
  target=$2
  if [ -L "$path" ]; then
    found=$(readlink "$path")
    if [ "$found" = "$target" ]; then
      echo "ok       $path -> $target"
      return
    fi
    echo "error: $path points at $found, not $target. Remove it and run again." >&2
    exit 1
  fi
  if [ -e "$path" ]; then
    echo "error: $path exists and is not a symlink. Move it aside and run again." >&2
    exit 1
  fi
  ln -s "$target" "$path"
  echo "created  $path -> $target"
  changed=1
}

if [ ! -d .claude ]; then
  mkdir .claude
  echo "created  .claude/"
  changed=1
fi

link CLAUDE.md AGENTS.md
link .claude/agents ../agents
link .claude/skills ../skills

# Everything above is installer output, so none of it is ever committed. It
# cannot be ignored from inside this directory, because a nested .gitignore
# cannot ignore a path at the repository root, and the root .gitignore belongs
# to the neutral core and names no harness. The per-clone exclude file is the
# right scope: it is never committed either, so the neutral core stays clean
# whether this adapter is installed or not. The second pattern also covers
# whatever the harness writes under .claude/ by itself, including
# settings.local.json and scheduled_tasks.lock.
#
# --git-common-dir, not --git-dir: inside a linked worktree the latter returns
# .git/worktrees/<name>/, and git reads ignore patterns from the common
# directory instead, so the two lines would land where nothing reads them. In
# an ordinary clone both return .git.
if git_dir=$(git rev-parse --git-common-dir 2>/dev/null); then
  exclude="$git_dir/info/exclude"
  mkdir -p "$(dirname "$exclude")"
  for line in "/CLAUDE.md" "/.claude/"; do
    if grep -qxF "$line" "$exclude" 2>/dev/null; then
      echo "ok       $line already in $exclude"
    else
      printf '%s\n' "$line" >> "$exclude"
      echo "added    $line to $exclude"
      changed=1
    fi
  done
else
  echo "skipped  no git repository here, so nothing was excluded"
fi

if [ "$changed" -eq 0 ]; then
  echo
  echo "Nothing to do. The tree already carries this adapter."
else
  echo
  echo "Done. Start a session at the workbench root and run /context to confirm"
  echo "CLAUDE.md appears under Memory files."
fi
