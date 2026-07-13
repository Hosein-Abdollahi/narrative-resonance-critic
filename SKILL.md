---
name: narrative-resonance-critic
description: Critique fiction and creative prose — novels, short stories, chapters, or individual scenes. Use when the user asks for a critical read, developmental feedback, or line edit of narrative writing: pacing, tension, emotional arc, show-vs-tell, and prose-level issues. Combines Claude's close reading with deterministic measurements (emotional arc, told-emotion density, filter-word and adverb load, pacing variance) so feedback is specific and evidence-backed rather than generic.
---

# Narrative Resonance Critic

A developmental critic for fiction. It pairs **Claude's close reading** (the judgment) with **deterministic measurements** from the bundled scripts (the evidence), so every critique cites something concrete instead of offering vibes.

## Core principle

Claude does the *reading and judgment*. The scripts do the *counting*. A critique is only credible when judgment is anchored to evidence, so **every finding must cite either a measurement or a specific quoted line** — never a bare verdict, never a grade.

Do not simply run the scripts and paraphrase their numbers. The numbers are raw material. The value is in Claude reading the prose, deciding what actually matters, and using the measurements as supporting evidence.

## Workflow

1. **Read the whole passage closely, first.** Form your own critical read before looking at any numbers — pacing, tension, whether scenes earn their length, voice, what's working and what isn't.

2. **Run the analyzer** for objective measurements:
   ```
   python scripts/analyze.py path/to/text.txt
   ```
   Returns JSON with `prose_metrics` (pacing variance, dialogue ratio, filter-word / to-be / adverb / said-bookism rates, repetition) and `show_vs_tell` (told-emotion findings tiered STRONG / NAMED / PATTERN).

3. **Read the emotional arc.** Divide the passage into scenes or beats and score each one across the 12 emotions (`joy, calm, nostalgia, anxiety, melancholy, anger, wonder, tenderness, fear, disgust, hope, awe`), 0–1. Save as a JSON list (one dict per scene) and render the strip:
   ```
   python scripts/render_arc.py scores.json arc.svg
   ```
   *You* read the emotion — do not rely on keyword matching for this. The strip is a visualization of your reading, and evidence for arc critique (flat stretches, monotone repetition, a climax that peaks lower than an earlier scene).

4. **Write the critique** across the four dimensions below.

## The four dimensions (v1)

**1. Emotional arc & tension.** Where does tension flatline? Does the same emotion dominate scene after scene (monotone)? Does the climax actually peak, or does an earlier scene overshadow it? Judge whether a lull is earned or dead. *Cite the arc.*

**2. Show vs. tell.** Use `show_vs_tell`. STRONG/NAMED hits are stated feelings ("she was terrified"); PATTERN hits are stated feelings the lexicon didn't know ("she felt hollow"). High `told_density` means the prose names emotion instead of dramatizing it — but judge each: some telling is correct (transitions, summary). Flag the ones that should be enacted, and quote them.

**3. Pacing.** Use `pacing` (sentence-length variance — low stdev = monotone rhythm), `dialogue_ratio`, and scene length. Judge whether slow stretches earn their slowness.

**4. Line-level prose.** Use the per-1000-word rates. High `filter_words` ("she felt/saw/realized") holds the reader at arm's length; high `adverbs_ly` and `to_be_verbs` signal weak, static prose; `said_bookisms` ("exclaimed", "retorted") are usually overwriting; check `overused_words` and `repeated_sentence_openers`. Quote offenders.

## Output format

For each dimension, structure the critique as:

- **Finding** — what's happening, in one clear sentence.
- **Evidence** — the measurement and/or the specific quoted line(s).
- **Why it matters** — the effect on the reader.
- **Suggestion** — one concrete, actionable fix.

Lead with the 2–3 highest-impact issues; don't bury them under minor line notes. Note what's *working* too — a critique that only lists faults is neither accurate nor useful.

## Guidelines

- **Never hand down a grade or score.** Literary judgment is contested; show your reasoning so the writer can disagree.
- **Always quote or cite.** No finding without evidence.
- **Be specific, not generic.** "Chapter opens on four straight 'She'-sentences" beats "vary your sentences."
- **A measurement is a prompt to look, not a verdict.** A high adverb rate might be a stylistic choice; read before you flag.
- **Scope to what was given.** Critique a scene as a scene, a chapter as a chapter. Don't infer whole-novel problems from one excerpt.
- If a told-emotion word was caught only by the PATTERN tier, consider noting the word — it's a candidate to add to `scripts/told_emotion.py`'s lexicon.

## Examples

- "Can you critique this chapter of my novel?" → full four-dimension critique.
- "Is my pacing off in this scene?" → focus on dimension 3, cite variance and scene length.
- "Am I telling instead of showing here?" → focus on dimension 2, quote the flagged lines.
- "Show me the emotional arc of this story." → score scenes, render the strip, comment on shape.
