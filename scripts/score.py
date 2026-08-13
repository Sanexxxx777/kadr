#!/usr/bin/env python3
"""Generate a music bed timed to the cuts of one specific clip.

Why generate instead of picking a track: an agent reviewing a render cannot hear
audio, so choosing music by feel is not available to it. The scene timings, on the
other hand, are known exactly, and a bed can be built so the hits land on the cuts.
A finished track cannot do that; normally the edit is cut to the music, and here the
edit already exists.

The synthesis is deliberately plain: a pulse, a bass line on the scale, a noise hat,
a pad and a kick on the accents. This is a bed, not a song. It holds the rhythm and
stays out of the way of a voiceover.

    python3 score.py out.wav --duration 18 --bpm 96 \
        --accents 0.45,3.55,8.85,13.45 --key A --mood tense

    --mood calm    pad and a soft pulse only, for slow pieces
    --mood steady  pulse + bass + hats (default)
    --mood tense   denser, minor harmony, harder attack

Then wire it as a normal audio clip:
    <audio id="bgm" src="audio/score.wav" data-start="0" data-duration="18"
           data-track-index="20" data-volume="0.5"></audio>

Measure the mix after rendering (`ffmpeg -af ebur128`): aim for -16 to -20 LUFS on a
site, true peak no higher than -3 dBFS.
"""
import argparse
import math
import struct
import wave

SR = 44100

# semitones from the root: both pentatonics are neutral enough not to fight the text
SCALE_MINOR = [0, 3, 5, 7, 10]
SCALE_MAJOR = [0, 2, 4, 7, 9]
NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi_hz(semitone_from_a4: float) -> float:
    return 440.0 * (2 ** (semitone_from_a4 / 12.0))


def env(i: int, n: int, attack: float, release: float) -> float:
    """Note envelope: fast attack, exponential decay."""
    if n <= 0:
        return 0.0
    t = i / n
    a = min(1.0, t / attack) if attack > 0 else 1.0
    r = math.exp(-t / max(release, 1e-4))
    return a * r


def add(buf: list, start_s: float, samples: list, gain: float) -> None:
    off = int(start_s * SR)
    for i, v in enumerate(samples):
        j = off + i
        if 0 <= j < len(buf):
            buf[j] += v * gain


def kick(dur=0.36):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        # pitch drops from 110 to 45 Hz, which is what makes it a hit and not a beep
        f = 45 + 65 * math.exp(-t * 22)
        out.append(math.sin(2 * math.pi * f * t) * env(i, n, 0.002, 0.16))
    return out


def hat(dur=0.05, seed=1):
    n = int(dur * SR)
    out, x = [], seed * 12345 + 6789
    for i in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF   # own PRNG: renders must be reproducible
        noise = (x / 0x3FFFFFFF) - 1.0
        out.append(noise * env(i, n, 0.001, 0.05))
    return out


def bass(freq, dur):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        # a summed-harmonics saw is softer than a raw saw
        v = sum(math.sin(2 * math.pi * freq * k * t) / k for k in (1, 2, 3))
        out.append(v * 0.33 * env(i, n, 0.01, dur * 0.55))
    return out


def pad(freqs, dur):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = 0.0
        for k, f in enumerate(freqs):
            detune = 1.0 + 0.0016 * (k - len(freqs) / 2)   # slight detune keeps the chord alive
            v += math.sin(2 * math.pi * f * detune * t)
        a = min(1.0, t / 0.9)                # long fade in
        r = min(1.0, (dur - t) / 0.9)        # and long fade out
        out.append(v / max(len(freqs), 1) * 0.5 * max(0.0, min(a, r)))
    return out


def build(duration, bpm, accents, key, mood):
    total = int(duration * SR)
    buf = [0.0] * total
    beat = 60.0 / bpm
    root = NOTES.get(key.upper(), 9) - 12          # root below the middle register
    scale = SCALE_MINOR if mood in ("tense", "steady") else SCALE_MAJOR

    # pad: two chords, swapping at the midpoint
    for half, deg in enumerate((0, 3 if mood == "tense" else 4)):
        chord = [midi_hz(root + scale[(deg + s) % len(scale)] + (12 if s > 2 else 0)) for s in (0, 2, 4)]
        seg = duration / 2
        add(buf, half * seg, pad(chord, seg), 0.20 if mood != "calm" else 0.30)

    if mood != "calm":
        # pulse: bass on every beat, walking the scale so it does not sit still
        steps = [0, 0, 4, 0, 2, 0, 4, 3]
        i = 0
        t = 0.0
        while t < duration - beat:
            f = midi_hz(root + scale[steps[i % len(steps)] % len(scale)])
            add(buf, t, bass(f, beat * 0.9), 0.5 if mood == "tense" else 0.38)
            i += 1
            t += beat

        # hats on eighths, offbeat quieter, otherwise it reads as a metronome
        t, i = 0.0, 0
        while t < duration:
            add(buf, t, hat(seed=i), 0.11 if i % 2 == 0 else 0.06)
            i += 1
            t += beat / 2

    # accents: the kick lands 60 ms before the cut, which is where it feels on time
    for a in accents:
        if 0 <= a < duration:
            add(buf, max(0.0, a - 0.06), kick(), 0.85)

    # soft limiting instead of hard clipping
    peak = max((abs(v) for v in buf), default=1.0) or 1.0
    norm = 0.72 / peak
    for i in range(total):
        v = buf[i] * norm
        buf[i] = math.tanh(v * 1.25) * 0.8

    # edge fades
    fi, fo = int(0.25 * SR), int(1.4 * SR)
    for i in range(min(fi, total)):
        buf[i] *= i / fi
    for i in range(min(fo, total)):
        buf[total - 1 - i] *= i / fo
    return buf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--duration", type=float, required=True, help="clip duration in seconds")
    ap.add_argument("--bpm", type=float, default=96)
    ap.add_argument("--accents", default="", help="comma-separated scene-cut times in seconds")
    ap.add_argument("--key", default="A")
    ap.add_argument("--mood", default="steady", choices=["calm", "steady", "tense"])
    a = ap.parse_args()

    accents = [float(x) for x in a.accents.split(",") if x.strip()]
    buf = build(a.duration, a.bpm, accents, a.key, a.mood)

    with wave.open(a.out, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in buf))

    print(f"{a.out}: {a.duration}s, {a.bpm} bpm, {a.mood}, {len(accents)} accents")


if __name__ == "__main__":
    main()
