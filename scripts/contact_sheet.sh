#!/bin/zsh
# Contact sheet for a rendered video: one grid image plus a map of timecodes.
#
# Why: a language model reviewing your video sees individual frames, never the
# motion. Repeated shots, dead gaps between scenes and a weak ending are invisible
# frame by frame, and obvious on a grid. This is the input for the visual review
# pass after a render.
#
#   contact_sheet.sh <video.mp4> [cols] [rows]
#
# Defaults to 4x3 = 12 frames spread evenly across the file.
# Timecodes are printed rather than drawn on the frames: many ffmpeg builds ship
# without drawtext (no libfreetype), and failing the whole sheet over a caption
# is a bad trade.
set -e

VIDEO="${1:?usage: contact_sheet.sh <video.mp4> [cols] [rows]}"
COLS="${2:-4}"
ROWS="${3:-3}"
N=$((COLS * ROWS))

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")
OUT="${VIDEO%.*}_contact.png"

FPS=$(python3 -c "print($N / max($DUR, 0.001))")
OFFSET=$(python3 -c "print(round($DUR / $N / 2, 3))")

ffmpeg -v error -ss "$OFFSET" -i "$VIDEO" \
  -vf "fps=${FPS},scale=480:-1,tile=${COLS}x${ROWS}:margin=8:padding=8:color=#111111" \
  -frames:v 1 "$OUT" -y

echo "$OUT"
python3 - "$DUR" "$N" "$COLS" <<'PY'
import sys
dur, n, cols = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
step = dur / n
print(f"frames: {n} | duration: {dur:.1f}s | step {step:.2f}s")
print("timecode per cell (left to right, top to bottom):")
row = []
for i in range(n):
    row.append(f"{i+1:2}) {step*i + step/2:5.2f}s")
    if len(row) == cols:
        print("   " + "   ".join(row)); row = []
if row:
    print("   " + "   ".join(row))
PY
