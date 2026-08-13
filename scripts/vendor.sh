#!/bin/zsh
# Vendor the HyperFrames agent skills into a directory you control, then declaw them.
#
#   vendor.sh <target-dir>
#
# Downloads the upstream repo tarball, extracts only `skills/`, copies it into
# <target-dir>/references, and runs declaw.py over the result.
#
# Pick a target directory whose name is NOT "hyperframes": `npx hyperframes init`
# deletes and replaces a directory by that name under ~/.claude/skills. Naming it
# something else is the cheap half of the protection; the wrapper is the other half.
set -e

TARGET="${1:?usage: vendor.sh <target-dir>}"
HERE="${0:A:h}"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "downloading upstream tarball..."
curl -sSL "https://codeload.github.com/heygen-com/hyperframes/tar.gz/refs/heads/main" -o "$TMP/hf.tgz"

echo "extracting skills/ ..."
tar -xzf "$TMP/hf.tgz" -C "$TMP" --include='*/skills/*'
SRC=$(find "$TMP" -maxdepth 2 -type d -name skills | head -1)
[ -d "$SRC" ] || { echo "no skills/ directory in the tarball" >&2; exit 1; }

mkdir -p "$TARGET/references"
cp -R "$SRC"/. "$TARGET/references/"
echo "vendored $(ls -d "$TARGET"/references/*/ | wc -l | tr -d ' ') skills into $TARGET/references"

# upstream ships Apache-2.0; keep the license next to the copy
curl -sSL "https://raw.githubusercontent.com/heygen-com/hyperframes/main/LICENSE" -o "$TARGET/UPSTREAM-LICENSE"

python3 "$HERE/declaw.py" "$TARGET/references"
