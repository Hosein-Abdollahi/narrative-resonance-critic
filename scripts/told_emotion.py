"""
told_emotion.py — detect "told" emotion in prose (the show-vs-tell instrument).

Two layers, tiered by confidence:

  STRONG  an emotion-naming word inside a telling construction
          ("she was terrified", "a wave of grief", "filled with dread")
  NAMED   a bare emotion-naming word on the page ("the terror rose in him")
  PATTERN a telling construction around an UNKNOWN adjective
          ("she felt despondent") — catches feeling-words not in the lexicon

This is a DETECTOR, not a scorer: it reports candidates and lets the reader
(Claude) decide which are genuine problems. So the lexicon is intentionally
big and blunt — false positives are cheap because a human/Claude filters them,
and the PATTERN tier means coverage does not depend on the lexicon being complete.
"""

import re
from typing import List, Dict

# ── Emotion-naming lexicon (lemmas; inflections handled at match time) ─────────
# Sized to the language: common emotions have many naming words, subtle ones few.
# This is the show-vs-tell detector's dictionary, SEPARATE from the arc engine's
# weighted _LEXICON, so expanding it here never disturbs arc calibration.

TOLD_WORDS: Dict[str, set] = {
    "joy": {
        "happy", "happiness", "joy", "joyful", "joyous", "glad", "gladness",
        "delight", "delighted", "delightful", "cheer", "cheerful", "cheery",
        "elated", "elation", "ecstatic", "ecstasy", "thrilled", "jubilant",
        "jubilation", "gleeful", "glee", "merry", "merriment", "blissful",
        "bliss", "content", "contented", "pleased", "overjoyed", "euphoric",
        "euphoria", "exuberant", "buoyant", "upbeat", "giddy", "exhilarated",
        "exhilaration", "rapturous", "rapture", "gratified", "jovial",
        "lighthearted", "festive", "beaming", "chipper", "tickled", "gleefully",
        "rejoicing", "rejoiced", "elatedly",
    },
    "melancholy": {
        "sad", "sadness", "sorrow", "sorrowful", "grief", "grieved", "grieving",
        "grieve", "mournful", "mourning", "mourn", "melancholy", "melancholic",
        "gloom", "gloomy", "glum", "despair", "despairing", "despondent",
        "dejected", "dejection", "forlorn", "heartbroken", "heartache",
        "woeful", "woe", "dismal", "downcast", "disconsolate", "desolate",
        "desolation", "bleak", "morose", "downhearted", "crestfallen",
        "doleful", "tearful", "weeping", "wept", "somber", "sombre",
        "heavyhearted", "unhappy", "misery", "miserable", "wretched",
        "anguish", "anguished", "grief-stricken", "brokenhearted", "lonely",
        "loneliness", "lonesome", "sorrowing",
    },
    "anger": {
        "angry", "anger", "angered", "furious", "fury", "mad", "rage", "raging",
        "enraged", "irate", "irritated", "irritation", "annoyed", "annoyance",
        "indignant", "indignation", "incensed", "livid", "seething", "wrathful",
        "wrath", "resentful", "resentment", "exasperated", "exasperation",
        "aggravated", "outraged", "outrage", "hostile", "hostility", "bitter",
        "bitterness", "fuming", "galled", "irked", "riled", "vexed", "vexation",
        "infuriated", "peeved", "miffed", "spiteful", "affronted", "choleric",
        "apoplectic", "wrothful", "cross",
    },
    "fear": {
        "afraid", "fear", "fearful", "scared", "frightened", "frighten",
        "terrified", "terror", "dread", "dreadful", "panic", "panicked",
        "panicky", "horror", "horrified", "horrifying", "petrified", "alarmed",
        "alarm", "spooked", "aghast", "fright", "trembling", "quaking",
        "cowering", "shaken", "phobic", "fearsome", "dreading", "terror-struck",
        "scary", "scaring", "frightful",
    },
    "anxiety": {
        "anxious", "anxiety", "worried", "worry", "nervous", "nervousness",
        "uneasy", "unease", "tense", "tension", "apprehensive", "apprehension",
        "stressed", "stress", "fretful", "fret", "restless", "jittery", "edgy",
        "distressed", "distress", "agitated", "agitation", "unsettled",
        "disquiet", "disquieted", "trepidation", "misgiving", "foreboding",
        "overwhelmed", "frazzled", "antsy", "wary", "flustered", "perturbed",
        "rattled", "on-edge",
    },
    "tenderness": {
        "tender", "tenderness", "love", "loving", "loved", "affection",
        "affectionate", "fond", "fondness", "warmth", "caring", "compassion",
        "compassionate", "gentle", "gentleness", "adore", "adoring", "adored",
        "cherish", "cherished", "devoted", "devotion", "doting", "endearment",
        "softhearted", "warmhearted", "loved", "beloved", "dear", "cherishing",
        "tenderly",
    },
    "calm": {
        "calm", "calmness", "serene", "serenity", "tranquil", "tranquility",
        "tranquillity", "peaceful", "peace", "placid", "composed", "composure",
        "relaxed", "relaxation", "soothed", "untroubled", "unruffled", "mellow",
        "restful", "sedate", "collected", "settled", "at-ease", "unperturbed",
        "quietude", "equanimity", "serenely",
    },
    "nostalgia": {
        "nostalgia", "nostalgic", "wistful", "wistfulness", "homesick",
        "homesickness", "longing", "yearning", "yearn", "reminiscent",
        "reminisce", "sentimental", "bittersweet", "pining", "pine",
        "hankering", "nostalgically",
    },
    "wonder": {
        "wonder", "wondrous", "wonderstruck", "amazed", "amazement",
        "astonished", "astonishment", "astounded", "marvel", "marveling",
        "marvelling", "fascinated", "fascination", "spellbound", "entranced",
        "enchanted", "enthralled", "agog", "dumbfounded", "flabbergasted",
        "wide-eyed", "mystified", "awestruck",
    },
    "hope": {
        "hope", "hopeful", "optimistic", "optimism", "expectant", "anticipation",
        "eager", "encouraged", "heartened", "buoyed", "sanguine", "aspiring",
        "aspiration", "hopefully", "reassured", "uplifted",
    },
    "awe": {
        "awe", "awed", "awestruck", "awestricken", "reverent", "reverence",
        "reverential", "sublime", "humbled", "overawed", "reverently",
    },
    "disgust": {
        "disgust", "disgusted", "disgusting", "revolted", "revulsion",
        "repulsed", "repulsion", "repugnance", "repugnant", "revolting",
        "sickened", "nauseated", "nausea", "nauseating", "queasy", "appalled",
        "loathing", "loathe", "abhorrence", "abhor", "aversion", "distaste",
        "distasteful", "repelled", "sickening", "repellent", "odious",
    },
}

# Flat lemma -> emotion lookup.
_WORD_TO_EMOTION: Dict[str, str] = {}
for _emo, _words in TOLD_WORDS.items():
    for _w in _words:
        _WORD_TO_EMOTION.setdefault(_w, _emo)

# ── Telling constructions ─────────────────────────────────────────────────────
# Linking / perception verbs: "was/felt/seemed + EMOTION".
_LINK_VERBS = {
    "was", "were", "is", "are", "am", "be", "been", "being", "felt", "feels",
    "feel", "feeling", "seemed", "seems", "seem", "looked", "looks", "appeared",
    "appears", "grew", "grows", "became", "becomes", "become", "turned", "turns",
    "sounded", "remained", "got",
}
# Nominal telling: "a wave/surge/pang of EMOTION".
_NOMINAL_HEADS = {
    "wave", "surge", "rush", "flood", "pang", "stab", "flash", "flicker",
    "sense", "feeling", "sensation", "twinge", "wash", "swell", "pang",
    "jolt", "shiver", "ripple", "burst", "fit",
}
# "filled/overcome with EMOTION".
_WITH_VERBS = {
    "filled", "overcome", "overwhelmed", "consumed", "gripped", "seized",
    "wracked", "racked", "flooded", "brimming", "trembling", "shaking",
    "sick", "weak", "numb", "giddy",
}
_INTENSIFIERS = {
    "very", "so", "quite", "utterly", "completely", "deeply", "terribly",
    "extremely", "incredibly", "absolutely", "thoroughly", "rather", "too",
    "somewhat",
}
# Feeling adjectives with no telltale suffix — the pattern tier needs these
# spelled out, since "hollow" / "numb" don't look adjectival by morphology.
_BARE_FEELING_ADJ = {
    "hollow", "numb", "empty", "cold", "lost", "blank", "heavy", "raw", "small",
    "alone", "adrift", "grim", "faint", "dull", "tired", "proud", "hurt",
    "broken", "shaken", "low", "blue", "sick", "weak", "tense", "restless",
    "bitter", "sour", "flat", "grey", "gray", "dark", "distant", "detached",
    "drained", "spent", "fragile", "brittle", "cross",
}
# Words that end a "<link> …" scan without being a feeling (determiners,
# prepositions, pronouns, common non-emotion complements).
_FUNCTION_STOP = {
    "the", "a", "an", "his", "her", "its", "their", "my", "your", "our", "this",
    "that", "these", "those", "there", "here", "in", "on", "at", "to", "into",
    "onto", "of", "for", "from", "by", "with", "about", "over", "under", "up",
    "down", "out", "off", "back", "away", "around", "not", "no", "it", "he",
    "she", "they", "we", "you", "him", "them", "us", "ready", "able", "sure",
    "right", "wrong", "done", "gone", "home", "late", "early", "quiet",
    "silent", "still", "one", "two", "some", "any", "all", "just", "only",
    "now", "then", "again",
}
_ADJ_SUFFIX = ("ed", "ful", "ous", "less", "ent", "ant", "ive", "ish", "some",
               "id", "ate", "ile", "ory")

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _normalize(word: str) -> str:
    """Strip common inflections so stored lemmas catch surface forms."""
    w = word.lower()
    if w in _WORD_TO_EMOTION:
        return w
    for suf in ("iness", "ness", "ically", "ially", "ing", "edly", "ed", "ly", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            base = w[: -len(suf)]
            if base in _WORD_TO_EMOTION:
                return base
            if base + "e" in _WORD_TO_EMOTION:
                return base + "e"
    return w


def _emotion_of(word: str):
    return _WORD_TO_EMOTION.get(_normalize(word))


def _looks_adjectival(word: str) -> bool:
    if word in _BARE_FEELING_ADJ:
        return True
    return len(word) >= 5 and word.endswith(_ADJ_SUFFIX)


def detect(text: str) -> List[Dict]:
    """
    Return told-emotion findings, one per hit, each with:
      sentence_index, sentence, tier (STRONG|NAMED|PATTERN), emotion, trigger
    """
    findings: List[Dict] = []
    sentences = [s for s in _SENT_SPLIT.split(text.strip()) if s.strip()]

    for si, sent in enumerate(sentences):
        tokens = _WORD_RE.findall(sent)
        lowered = [t.lower() for t in tokens]
        flagged = set()

        # STRONG / NAMED: a known emotion word, with or without a construction.
        for i, tok in enumerate(lowered):
            emo = _emotion_of(tok)
            if not emo:
                continue
            window = lowered[max(0, i - 4):i]
            in_construction = (
                any(w in _LINK_VERBS for w in window)
                or any(w in _NOMINAL_HEADS for w in window)
                or any(w in _WITH_VERBS for w in window)
            )
            findings.append({
                "sentence_index": si, "sentence": sent.strip(),
                "tier": "STRONG" if in_construction else "NAMED",
                "emotion": emo, "trigger": tok,
            })
            flagged.add(i)

        # PATTERN: "<link> [intensifier]* <ADJ> [and/or <ADJ>]" around words the
        # lexicon does NOT know — catches "felt hollow and adrift", "was despondent".
        for i, tok in enumerate(lowered):
            if tok not in _LINK_VERBS:
                continue
            j = i + 1
            while j < len(lowered) and lowered[j] in _INTENSIFIERS:
                j += 1
            chain = 0
            while j < len(lowered):
                w = lowered[j]
                if j in flagged or _emotion_of(w) or w in _FUNCTION_STOP:
                    break
                if _looks_adjectival(w):
                    findings.append({
                        "sentence_index": si, "sentence": sent.strip(),
                        "tier": "PATTERN", "emotion": None, "trigger": w,
                    })
                    flagged.add(j)
                    chain += 1
                    if j + 1 < len(lowered) and lowered[j + 1] in ("and", "or", "yet"):
                        j += 2
                        continue
                break

    findings.sort(key=lambda f: (f["sentence_index"], {"STRONG": 0, "NAMED": 1, "PATTERN": 2}[f["tier"]]))
    return findings


def summary(text: str) -> Dict:
    """Aggregate counts for a quick told-emotion density read."""
    hits = detect(text)
    n_sent = max(1, len([s for s in _SENT_SPLIT.split(text.strip()) if s.strip()]))
    by_tier = {"STRONG": 0, "NAMED": 0, "PATTERN": 0}
    for h in hits:
        by_tier[h["tier"]] += 1
    return {
        "sentences": n_sent,
        "told_hits": len(hits),
        "by_tier": by_tier,
        "told_density": round(len(hits) / n_sent, 3),
        "findings": hits,
    }


if __name__ == "__main__":
    import json, sys
    src = sys.stdin.read() if not sys.stdin.isatty() else "She was terrified."
    print(json.dumps(summary(src), indent=2))
