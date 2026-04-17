#!/usr/bin/env bash
set -e

# ── OpenSea skill (git submodule @ ProjectOpenSea/opensea-skill v2.1.0) ───────
# Pinata may clone without recursing submodules. If we're inside a git work
# tree and the skill isn't populated yet, pull it in.
if [ ! -f skills/opensea/SKILL.md ] && git rev-parse --git-dir >/dev/null 2>&1; then
  git submodule update --init --recursive skills/opensea || true
fi

if [ ! -f skills/opensea/SKILL.md ]; then
  echo "ERROR: skills/opensea/SKILL.md missing — submodule did not initialize." >&2
  echo "If building outside git, run: git submodule update --init --recursive" >&2
  exit 1
fi
echo "OpenSea skill ready ($(git -C skills/opensea describe --tags --always 2>/dev/null || echo "unknown"))."

# ── OpenSea CLI (@opensea/cli) ────────────────────────────────────────────────
if ! command -v opensea >/dev/null 2>&1; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm not found — cannot install @opensea/cli." >&2
    exit 1
  fi
  npm install -g @opensea/cli
fi
echo "OpenSea CLI ready ($(opensea --version))."

chmod +x skills/opensea/scripts/*.sh 2>/dev/null || true
