# Prompt iteration log — P4 (Hallucination Check)

We iterated on P4 specifically because it is the prompt the whole "no
hallucinations" claim of this project rests on. P1-P3 went through smaller,
single-pass tuning; P4 is documented here in full since it needed 3 real
versions to become reliable. Each version was run against all 10 files in
`test-data/` (10 runs per version).

| Version | What changed | Why it was changed | Result after the change |
|---|---|---|---|
| v1 | First attempt: ask the model to "check for hallucinations" in free text, default temperature (0.7), no schema, no chunk numbering | Starting point | Free-text response in 10/10 runs — not machine-parseable. In 4/10 runs the model just said "this summary looks accurate" with no per-sentence check at all. |
| v2 | Added a system prompt, temperature=0, and a required JSON schema (`field`, `unsupported_sentences`, `corrected_text`) | v1 couldn't be parsed or acted on programmatically | JSON parsed correctly in 10/10 runs. But with no chunk numbering, the model could not point to *where* a sentence was supported — in 3/10 runs it claimed a sentence was "supported" with no way to verify that claim, and it missed an injected hallucination test (a fabricated "evaluated on 10,000 users" sentence we manually inserted into a draft summary) in 2/5 injection tests. |
| v3 (final) | Split the paper into numbered chunks (`[chunk N]`) and required `supporting_chunk_ids` + `original_sentence_count` per field, forcing the model to cite which chunk supports each kept sentence | v2's claims of "supported" were unverifiable | Every kept sentence in 10/10 runs now carries a concrete chunk id we can spot-check by hand. In the same 5 injection tests used for v2, v3 caught the fabricated sentence in 5/5 by correctly finding no supporting chunk id for it. It still does not catch cross-section numeric contradictions that are each individually "supported" by some chunk (see `test-data/test_results.md`, row 7 / known limitation #3) — that is a different failure mode from hallucination and is left as future work, not something v3 claims to solve. |

Two worked examples were embedded in the v3 system prompt during the
development runs above; once the 5/5 injection-catch rate was confirmed
stable without them, they were removed from the production prompt shipped in
`prompts/final/P4_hallucination_check.txt` to cut token cost per call.

---

## v1 — full text

```
SYSTEM PROMPT: (none)

USER PROMPT:
Here is a summary of a paper and the paper text. Check the summary for
hallucinations and tell me if anything is wrong.

Summary: {summary_json}
Paper: {full_paper_text}
```
Settings: temperature = 0.7 (default)

## v2 — full text

```
SYSTEM PROMPT:
You are a fact-checker. You check a paper summary against the paper text and
list any unsupported claims.

USER PROMPT:
Summary: {summary_json}
Paper (numbered chunks): {numbered_chunks_text}

For each field (problem, method, results, limitations), return JSON:
{"field": "...", "unsupported_sentences": ["..."], "corrected_text": "..."}
Return a JSON array of 4 objects.
```
Settings: temperature = 0

Note: this version's user prompt already mentions "numbered chunks" in the
label, but the chunk-numbering code was not actually wired in until v3 — the
variable was populated with plain concatenated text, which is why the model
could not reliably point to a specific chunk (see "Result after the change"
above).

## v3 — full text (final, shipped version)

See `prompts/final/P4_hallucination_check.txt` for the complete prompt sheet
(system prompt, user template, variables, and a real sample run). The only
change from v2 is: numbered chunks are now actually passed in
(`[chunk 1] ... [chunk 2] ...`), and the required JSON schema adds
`original_sentence_count` and `supporting_chunk_ids` per field.
