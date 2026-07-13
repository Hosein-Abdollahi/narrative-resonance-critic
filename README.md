# Narrative Resonance Critic

A **Claude Skill** that gives developmental critique of fiction — novels, short stories, chapters, or single scenes. It pairs Claude's close reading with deterministic measurements so feedback is specific and evidence-backed, not generic.

[![License](https://img.shields.io/badge/license-Apache%202.0-2ecc71)](LICENSE)
[![Skill](https://img.shields.io/badge/Claude-Skill-E6C079)](https://code.claude.com/docs/en/skills)
[![Python](https://img.shields.io/badge/python-stdlib%20only-4584b6)](https://www.python.org/)

## What it does

Ask it to "critique this chapter" and it returns a structured report across four dimensions — **emotional arc & tension, show vs. tell, pacing, and line-level prose** — where every finding cites a measurement or a quoted line. No grades, no vibes: each point is *finding → evidence → why it matters → suggestion*.

## How it works

The design principle is a split:

- **Claude reads and judges.** All interpretation — is this lull earned, does the climax land, is this telling a problem — comes from Claude reading the prose directly.
- **The scripts count.** Objective, countable things (told-emotion density, filter-word and adverb rates, pacing variance, the emotional arc) are measured by bundled Python and handed to Claude as evidence.

These two layers cover each other. The detectors are deliberately blunt and will over-flag; Claude filters the false positives and grounds its judgment in the numbers that survive. That combination — a fixed rubric plus instrumentation plus a reader — is what a plain "review my story" prompt can't reproduce.

### Deterministic vs. judged

| Dimension | Measured by Python | Judged by Claude |
|---|---|---|
| Emotional arc & tension | per-beat emotion scores → fingerprint strip | is the shape right, does tension ratchet or sawtooth |
| Show vs. tell | told-emotion detection (lexicon + grammar-of-telling) | which told lines should be dramatized |
| Pacing | sentence-length variance, dialogue ratio, scene length | is a slow stretch earned |
| Line-level prose | filter-word / to-be / adverb rates, repetition | voice, freshness, what actually weakens the prose |

### The show-vs-tell detector

"Telling" is prose that *names* a feeling ("she was terrified") instead of dramatizing it. The detector finds these in tiers: a curated emotion-naming lexicon catches the known words, and a **grammar-of-telling** pass catches feeling-words the lexicon doesn't know — "she felt *hollow* and *adrift*" fires on the construction, not the vocabulary. So coverage doesn't depend on the word list being complete.

## Install (Claude Code)

Clone into your personal skills directory:

```bash
git clone https://github.com/Hosein-Abdollahi/narrative-resonance-critic ~/.claude/skills/narrative-resonance-critic
```

Start a new Claude Code session and confirm it loaded:

```
/skills
```

`narrative-resonance-critic` should appear in the list. Then paste or attach a scene and say **"critique this chapter."** To force it explicitly: *"use the narrative-resonance-critic skill."*

Requires the code-execution environment (standard in Claude Code) and Python — the scripts are **standard-library only**, so there is nothing to `pip install`.

## Usage

- `critique this chapter` → full four-dimension critique
- `is my pacing off in this scene?` → focuses dimension 3
- `am I telling instead of showing here?` → focuses dimension 2
- `show me the emotional arc of this story` → scores beats and renders the fingerprint strip

## Files

```
narrative-resonance-critic/
├── SKILL.md                  # the critic's reading spec + workflow
└── scripts/
    ├── analyze.py            # one-command deterministic report (JSON)
    ├── told_emotion.py       # show-vs-tell detector (lexicon + telling patterns)
    ├── prose_metrics.py      # pacing, filter words, adverbs, repetition
    ├── render_arc.py         # per-beat emotion scores → fingerprint SVG
    ├── emotion_engine.py     # bundled: 12-emotion taxonomy + colors
    └── fingerprint.py        # bundled: strip renderer
```

## Roadmap (v2)

Character consistency, dialogue depth, POV/tense consistency, scene purpose, and theme — each following the same measure-then-judge pattern.

## Credits

Built on the [Narrative Resonance](https://github.com/Hosein-Abdollahi/Narrative-Resonance) emotion engine — a 12-emotion taxonomy tuned for literary text.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
