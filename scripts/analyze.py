"""
analyze.py — run the deterministic critic detectors over a manuscript and print
a JSON report. Claude reads the prose itself for the interpretive judgment; this
supplies the objective measurements the critique must cite.

Usage:
  python analyze.py path/to/chapter.txt
  cat chapter.txt | python analyze.py
"""

import json
import sys

import told_emotion
import prose_metrics


def analyze(text: str) -> dict:
    return {
        "prose_metrics": prose_metrics.compute(text),
        "show_vs_tell": told_emotion.summary(text),
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = open(sys.argv[1], encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    print(json.dumps(analyze(text), indent=2))
