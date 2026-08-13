#!/usr/bin/env python3
"""Declaw a vendored copy of the HyperFrames agent skills.

The upstream pack (github.com/heygen-com/hyperframes, Apache-2.0) ships 19 agent
skills. They are good material, but a few instructions in them make the agent act
on your machine without asking:

  * commands that install more skills into ~/.claude/skills while the agent works
  * instructions to bump the pinned CLI version on its own
  * "act on the signal rather than relaying it to the user"
  * a claim to be the mandatory entry point and the default output framework
    for anything animation-shaped

This script rewrites those out of the vendored markdown and prints a check at the
end. Code files (.mjs/.py/.sh) are left alone: dependency installs there already
run through `npm install --ignore-scripts` into a temp dir behind an interactive
prompt, which is reasonable.

Usage:
    python3 declaw.py <path-to-vendored-skills-dir>

Run it again after every upstream refresh.
"""
import os
import re
import sys

NOTE_INSTALL = "<!-- vendored locally: nothing to install -->"
NOTE_UPGRADE = "<!-- CLI version is pinned; upgrade deliberately, not mid-task -->"

LIFECYCLE = """# Skill lifecycle - not applicable to a vendored copy

Upstream documents `npx hyperframes skills check/update/add` here: the mechanism the
CLI uses to install its skills into `~/.claude/skills/` while an agent is working.

This copy is vendored, so there is nothing to install and nothing to refresh at
runtime.

Note that `npx hyperframes init` **deletes and replaces** a directory named
`hyperframes` under your skills folder. Two things protect you:

1. Vendor the pack under a different directory name.
2. Always call the CLI through the wrapper, which sets `HYPERFRAMES_SKIP_SKILLS=1`.

The `--skip-skills` flag is deliberately ignored by the CLI; the environment
variable is the only opt-out.
"""

PATTERNS = [
    (r"^.*npx (?:hyperframes )?skills (?:update|add)[^\n]*$", NOTE_INSTALL, "install commands", re.M),
    (r"^.*npx skills add heygen-com/hyperframes[^\n]*$", NOTE_INSTALL, "install commands", re.M),
    (r"^.*npx hyperframes@latest upgrade[^\n]*$", NOTE_UPGRADE, "self-upgrade commands", re.M),
    (r"Act on the signal rather than relaying it to the user[^.]*\.",
     "Report the signal to the user and let them decide.", "silent-action directives", 0),
    (r"Mandatory entry point: read this first for",
     "Reference material, routed by your own dispatcher, for", "entry-point capture", 0),
    (r"HyperFrames is the default output framework\s+unless the user explicitly chooses another framework for the deliverable or asks only to record a\s+browser session\.",
     "Use it when the deliverable is a video file. Anything that stays on a web page belongs to your own animation tooling.",
     "default-framework capture", 0),
    (r"selects and installs\s+the owning workflow", "reads the owning workflow from the vendored copy", "entry-point capture", 0),
]

LEFTOVER_MARKERS = ("skills update", "skills add heygen", "hyperframes@latest upgrade",
                    "Mandatory entry point", "default output framework", "Act on the signal")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = os.path.abspath(os.path.expanduser(sys.argv[1]))
    if not os.path.isdir(root):
        print(f"not a directory: {root}")
        return 2

    counts, touched = {}, set()

    for dirpath, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            try:
                original = open(path, encoding="utf-8").read()
            except OSError:
                continue
            text = original
            for pattern, repl, label, flags in PATTERNS:
                text, n = re.subn(pattern, repl, text, flags=flags)
                if n:
                    counts[label] = counts.get(label, 0) + n
                    touched.add(os.path.relpath(path, root))
            if text != original:
                open(path, "w", encoding="utf-8").write(text)

    lifecycle = os.path.join(root, "hyperframes/references/skill-lifecycle.md")
    if os.path.exists(lifecycle):
        open(lifecycle, "w", encoding="utf-8").write(LIFECYCLE)
        touched.add("hyperframes/references/skill-lifecycle.md")

    print(f"files changed: {len(touched)}")
    for label, n in sorted(counts.items()):
        print(f"  {label}: {n}")

    leftovers = []
    for dirpath, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            body = open(path, encoding="utf-8", errors="ignore").read()
            leftovers += [f"{os.path.relpath(path, root)}: {m}" for m in LEFTOVER_MARKERS if m in body]

    print("\ncheck:", "clean" if not leftovers else "LEFTOVERS")
    for item in leftovers:
        print("  ", item)
    return 1 if leftovers else 0


if __name__ == "__main__":
    raise SystemExit(main())
