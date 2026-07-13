"""
render_arc.py — turn Claude's per-scene emotion reading into a fingerprint SVG.

In the skill, Claude does the reading (not the keyword engine), so this takes a
JSON list of per-scene emotion score dicts and renders the strip. This is the
"scores in -> image out" path: the accuracy comes from Claude, the visual from
the bundled Narrative Resonance renderer.

Usage:
  python render_arc.py scores.json out.svg
where scores.json is: [{"joy":0.1,"fear":0.8,...}, {...}, ...]  (one per scene)
"""

import json
import sys
from math import ceil

from emotion_engine import (
    valence_of, arousal_of, EMOTION_DISPLAY_COLORS, EMOTIONS,
    NEUTRAL, NEUTRAL_COLOR, emotions_to_palette,
)
from fingerprint import fingerprint_svg, _aggregate

MAX_COLUMNS = 120


def _rows_from_scores(scores):
    rows = []
    for em in scores:
        em = {k: float(em.get(k, 0.0)) for k in EMOTIONS}
        intensity = max(em.values()) if em else 0.0
        rows.append({
            "emotions": em,
            "intensity": intensity,
            "valence": valence_of(em),
            "arousal": arousal_of(em),
        })
    return rows


def _columns(rows, max_columns=MAX_COLUMNS):
    n = len(rows)
    if n == 0:
        return []
    if n <= max_columns:
        bins = [[r] for r in rows]
    else:
        size = ceil(n / max_columns)
        bins = [rows[i:i + size] for i in range(0, n, size)]

    columns, cursor = [], 0
    for b in bins:
        agg = _aggregate([r["emotions"] for r in b])
        mean_i = sum(r["intensity"] for r in b) / len(b)
        peak_i = max(r["intensity"] for r in b)
        intensity = 0.45 * mean_i + 0.55 * peak_i
        dominant = max(agg.items(), key=lambda x: x[1])[0]
        if intensity < 0.05:
            dominant, color = NEUTRAL, NEUTRAL_COLOR
        else:
            color = EMOTION_DISPLAY_COLORS.get(dominant, emotions_to_palette(agg, 1)[0])
        columns.append({
            "color": color, "intensity": round(intensity, 4),
            "valence": round(sum(r["valence"] for r in b) / len(b), 4),
            "arousal": round(sum(r["arousal"] for r in b) / len(b), 4),
            "dominant": dominant, "span": (cursor, cursor + len(b) - 1),
        })
        cursor += len(b)
    return columns


def render(scores, width=900, height=90):
    return fingerprint_svg(_columns(_rows_from_scores(scores)), width=width, height=height)


if __name__ == "__main__":
    scores = json.load(open(sys.argv[1], encoding="utf-8"))
    svg = render(scores)
    out = sys.argv[2] if len(sys.argv) > 2 else "arc.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out} ({len(_columns(_rows_from_scores(scores)))} columns)")
