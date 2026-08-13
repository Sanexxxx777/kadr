# What is ours and what is not

## Ours (MIT)

- `bin/hf` - CLI wrapper with the environment guard and the post-run check
- `scripts/vendor.sh` - vendoring helper
- `scripts/declaw.py` - removes self-acting instructions from a vendored copy
- `scripts/contact_sheet.sh` - frame grid for reviewing a render
- `templates/starter/` - minimal composition
- `README.md`

## Not ours

- Anything `scripts/vendor.sh` downloads into `references/` is a derivative of
  **HyperFrames** by HeyGen, licensed Apache-2.0.
  Source: https://github.com/heygen-com/hyperframes
  The vendoring script writes their licence to `UPSTREAM-LICENSE` next to the copy.

- The renderer itself is the npm package `hyperframes` (Apache-2.0). It is **not
  forked here**; the wrapper calls it as an external dependency at a pinned version.
  Frame-by-frame seeking in headless Chrome, encoding and audio mixing are upstream's work.

## Modifications to the derivative part (Apache-2.0 section 4(b))

`scripts/declaw.py` rewrites, in the vendored markdown only:

1. commands that install further skills into the user's agent config
2. instructions to bump the pinned CLI version unattended
3. "act on the signal rather than relaying it to the user"
4. the claim to be the mandatory entry point and default output framework
5. the skill-lifecycle page, replaced with a note explaining why it does not apply
   to a vendored copy

Code files are left untouched: dependency installation there already runs through
`npm install --ignore-scripts` into a temporary directory behind an interactive prompt.
