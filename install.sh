#!/usr/bin/env bash
{
# The whole script is one brace group, so a truncated `curl | bash` download is a syntax error, not half an install.
set -euo pipefail

REPO="codeswithroh/pitch-video"
REF="${PITCH_VIDEO_REF:-main}"
SKILL="pitch-video"
DESTS=("$HOME/.claude/skills/$SKILL" "$HOME/.agents/skills/$SKILL")

say() { printf '\033[1;33m▸\033[0m %s\n' "$1"; }
fail() { printf '\033[1;31mpitch-video install failed:\033[0m %s\n' "$1" >&2; exit 1; }

for bin in curl tar; do command -v "$bin" >/dev/null || fail "$bin is required"; done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
say "Downloading $REPO@$REF"
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" | tar -xz -C "$tmp" || fail "download failed"
src="$(find "$tmp" -maxdepth 4 -type d -path "*/.agents/skills/$SKILL" | head -1)"
[ -n "$src" ] || fail "skill folder not found in the archive"

for d in "${DESTS[@]}"; do
  mkdir -p "$(dirname "$d")"
  rm -rf "$d"
  cp -R "$src" "$d"
  say "Installed skill → $d"
done

if [ "${PITCH_VIDEO_SKIP_TOOLBOX:-0}" != "1" ]; then
  say "Building the toolbox (ffmpeg/whisper check, Python venv, Playwright Chromium, models). This takes a few minutes the first time."
  bash "${DESTS[0]}/scripts/setup.sh" || fail "toolbox setup failed. Fix the message above, then re-run: bash ${DESTS[0]}/scripts/setup.sh"
fi

say "Done. Restart your agent, then ask: \"Make a pitch video from ~/Movies/my_pitch.mov\""
}
