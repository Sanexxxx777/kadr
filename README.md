# Kadr

Small toolkit for making video with [HyperFrames](https://github.com/heygen-com/hyperframes) as a coding agent, without letting the tooling write into your agent config behind your back.

HyperFrames renders plain HTML, CSS and a paused GSAP timeline into a deterministic MP4. It is genuinely good, and it ships a pack of agent skills full of useful craft. Two things bit us while adopting it, and this repo is what came out of fixing them.

## What happened

**`npx hyperframes init` deleted our skill directory. Twice.**

The CLI keeps its own skills fresh under `~/.claude/skills/`. If you vendor the pack into a directory named `hyperframes`, `init` removes that directory and writes its own version, plus seven more skills, without asking. We lost a full vendored copy the first time.

The second time we had the documented opt-out set, and it still happened, because of a shell detail worth knowing:

```zsh
E="A=1 B=1"
env $E npx hyperframes init x     # zsh does not word-split variables
```

zsh passes that as one argument, so neither variable is set and the guard is silently off. The `--skip-skills` flag does not help either, it is deliberately ignored upstream. `HYPERFRAMES_SKIP_SKILLS=1` as a real environment variable is the only opt-out.

**The skills instruct the agent to act on its own.** Commands that install more skills mid-task, instructions to bump the pinned CLI version, a line that says to act on a signal rather than relay it to the user, and a claim to be the mandatory entry point and default output framework for anything animation-shaped. As material the pack is excellent. As standing instructions in an agent's context, those parts are not what you want.

## What is here

```
bin/hf                    wrapper: sets the env guard, pins the version, verifies your dir survived
scripts/vendor.sh         pull upstream skills into a directory you name, then declaw them
scripts/declaw.py         strip the self-acting instructions; prints a check at the end
scripts/contact_sheet.sh  grid of frames from a render, for reviewing a video you cannot watch
templates/starter/        minimal composition with the determinism rules written down
```

Nothing here replaces HyperFrames. The renderer is upstream's and stays upstream's; this is the layer around it.

## Use

```sh
git clone https://github.com/Sanexxxx777/kadr && cd kadr

# vendor the pack somewhere that is NOT named "hyperframes"
./scripts/vendor.sh ~/.claude/skills/my-video-kit

# always call the CLI through the wrapper
export HF_GUARD=~/.claude/skills/my-video-kit
./bin/hf init promo --example blank
cd promo && ../bin/hf check && ../bin/hf render
```

Requires Node 22+, FFmpeg, Python 3. The first render downloads a Chromium build.

## The contact sheet

A model reviewing a render sees single frames, never motion. Repeated shots, dead gaps and a weak ending are invisible frame by frame and obvious on a grid:

```sh
./scripts/contact_sheet.sh promo/renders/promo.mp4 4 3
```

It prints the timecode of each cell. On our first promo it immediately showed three places where the video sat still while we thought it was moving.

## Two things the renderer taught us

**`check` is worth running every time.** It measures text contrast per frame and finds text blocks that overlap in time, which caught two real defects for us. Intentional layering is declared with `data-layout-allow-overlap`.

**Compute layout values at build time.** Render workers initialise tweens independently, so a function-valued tween (`x: () => el.offsetWidth`) can resolve differently per worker and drift across the file. The linter warns about it; take the warning.

## Credits and licence

The vendored `references/` are a derivative of [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen, Apache-2.0. `scripts/vendor.sh` places their licence next to the copy and `scripts/declaw.py` records the modifications, as Apache-2.0 section 4(b) requires. Apache-2.0 grants no trademark rights, so this project is called Kadr and not something HyperFrames-shaped.

This repo's own code is MIT. See `NOTICE.md` for the split between what is ours and what is not.
