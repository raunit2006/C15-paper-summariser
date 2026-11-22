# Changelog

## 2026-11-22 — Milestone 2 build
- Designed and implemented the 4-prompt chain (P1 chunk-tagger, P2 evidence
  extractor, P3 synthesizer, P4 hallucination check) in `code/pipeline.py`.
- Built the Streamlit prototype (`code/app.py`): upload PDF or paste text,
  run the full chain, see the checked summary plus the hallucination-check
  detail and raw trace.
- Iterated P4 from v1 (free text, unparseable) to v2 (JSON, but no
  chunk-level traceability) to v3 (numbered chunks + required
  `supporting_chunk_ids`, 5/5 injected-hallucination catch rate) —
  full log in `docs/prompt_iteration_log.md`.
- Wrote 10 test inputs (3 normal, 5 edge, 2 invalid) covering: a full
  structured paper, a paper missing a limitations section, an abstract-only
  "paper", a long multi-section paper that forces 3-way chunking, a
  non-paper input, a non-English paper, a paper with an internal
  abstract-vs-results numeric contradiction, a results-only table fragment,
  a second normal paper, and a garbled OCR scan. Ran the full chain against
  all 10 and recorded pass/fail honestly (7 pass / 3 fail) in
  `test-data/test_results.md`, including 3 fails that map directly to the
  "known limitations" in the Milestone 2 PDF.
- Generated the 4 required diagrams (`docs/*.png`) directly from the actual
  pipeline shape via `docs/make_diagrams.py`, not copied from the internet.

## Since Milestone 1
- Milestone 1 selected topic C15 ("Research paper summariser for students",
  input: research paper, output: structured summary of problem/method/
  results/limitations, with chaining for long documents and hallucination
  checks against the paper) and scoped the target user as a student doing a
  literature review.
- Milestone 2 is the first working implementation: no code existed before
  this build. Prior to this, the chaining/hallucination-check requirement
  from the topic brief was only a stated design goal, not yet implemented.
