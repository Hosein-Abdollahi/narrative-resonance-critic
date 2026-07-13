"""
prose_metrics.py — deterministic, objective measurements a critic can cite.

These are things better counted than judged: pacing proxies, filter-word density,
adverb load, dialogue balance, and repetition. Claude interprets the numbers;
the numbers themselves are not opinions.
"""

import re
import statistics
from collections import Counter
from typing import Dict, List

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

# "she felt / saw / noticed / realized …" — filter words hold the reader at arm's
# length from the character's direct experience.
_FILTER_WORDS = {
    "felt", "feel", "feels", "saw", "sees", "see", "noticed", "notice",
    "realized", "realised", "realize", "wondered", "wonder", "thought",
    "thinks", "think", "knew", "know", "heard", "hears", "hear", "watched",
    "watch", "seemed", "seem", "seems", "looked", "decided", "considered",
    "remembered", "sensed", "sense", "observed", "noted", "figured",
}
# Weak "to be" verbs — a high rate flags static, telling-heavy prose.
_TO_BE = {"is", "are", "was", "were", "be", "been", "being", "am"}
# Said-substitutes (dialogue tags) that often signal overwriting.
_SAID_BOOKISMS = {
    "exclaimed", "declared", "retorted", "interjected", "opined", "chortled",
    "ejaculated", "expostulated", "proclaimed", "articulated", "voiced",
    "uttered", "queried", "riposted", "vociferated",
}


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]


def _words(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


def compute(text: str) -> Dict:
    sents = _sentences(text)
    words = _words(text)
    n_words = max(1, len(words))
    n_sents = max(1, len(sents))
    lengths = [len(_WORD_RE.findall(s)) for s in sents]

    # Pacing: sentence-length distribution + variance (monotony proxy).
    mean_len = statistics.mean(lengths) if lengths else 0
    stdev_len = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0

    # Dialogue balance: fraction of sentences containing quotation marks.
    dialogue_sents = sum(1 for s in sents if '"' in s or '“' in s or '”' in s or "'" in s and re.search(r"[‘’']", s))
    dialogue_ratio = round(dialogue_sents / n_sents, 3)

    # Filter words, to-be verbs, adverbs, said-bookisms — as per-1000-word rates.
    adverbs = [w for w in words if w.endswith("ly") and len(w) > 3]
    filt = [w for w in words if w in _FILTER_WORDS]
    tobe = [w for w in words if w in _TO_BE]
    bookisms = [w for w in words if w in _SAID_BOOKISMS]

    def per_1000(items):
        return round(1000 * len(items) / n_words, 1)

    # Repetition: most common non-trivial words + repeated sentence openers.
    stop = {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at",
        "for", "with", "was", "were", "is", "are", "he", "she", "it", "they",
        "her", "his", "him", "them", "that", "this", "as", "had", "have", "has",
        "s", "i", "you", "we", "not", "be", "by", "from", "so", "up", "out",
    }
    content = [w for w in words if w not in stop and len(w) > 3]
    overused = [w for w, c in Counter(content).most_common(8) if c >= 4]
    openers = Counter(
        (_WORD_RE.findall(s)[0].lower() if _WORD_RE.findall(s) else "")
        for s in sents
    )
    repeated_openers = [w for w, c in openers.most_common(5) if w and c >= 3]

    return {
        "counts": {"words": len(words), "sentences": len(sents)},
        "pacing": {
            "mean_sentence_length": round(mean_len, 1),
            "sentence_length_stdev": round(stdev_len, 1),
            "longest": max(lengths) if lengths else 0,
            "shortest": min(lengths) if lengths else 0,
            "note": "low stdev = monotone rhythm; healthy prose varies sentence length",
        },
        "dialogue_ratio": dialogue_ratio,
        "rates_per_1000_words": {
            "filter_words": per_1000(filt),
            "to_be_verbs": per_1000(tobe),
            "adverbs_ly": per_1000(adverbs),
            "said_bookisms": per_1000(bookisms),
        },
        "flags": {
            "filter_word_examples": sorted(set(filt))[:10],
            "said_bookism_examples": sorted(set(bookisms))[:10],
            "overused_words": overused,
            "repeated_sentence_openers": repeated_openers,
        },
    }


if __name__ == "__main__":
    import json, sys
    src = sys.stdin.read() if not sys.stdin.isatty() else "She felt sad. She was sad. She looked sad."
    print(json.dumps(compute(src), indent=2))
