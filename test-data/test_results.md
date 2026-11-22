# Test table — 10 inputs, 7 non-normal (5 edge + 2 invalid)

Full chain run against every file in this folder. Saved full outputs for
rows 1 and 4 are in `paper_01_actual_output.json` and
`paper_04_actual_output.json`.

| # | Input (short) | Type | Expected output | Actual output (short) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | paper_01_normal.txt — edge batching paper, all 4 sections present | Normal | Correct 4-section summary, 34% p99 latency figure preserved | Correct summary, 34% figure preserved, all sentences traced to chunk 1 | Pass |
| 2 | paper_02_no_limitations.txt — no Limitations section in source | Edge | `limitations` = "Not stated in the retrieved sections." | P3 draft invented a limitation ("tested on one dataset only"); P4 caught it as unsupported (no chunk mentions it) and corrected it to "Not stated in the retrieved sections." | Pass (only after P4 correction — see note) |
| 3 | paper_03_abstract_only.txt — abstract only, no body sections | Edge | `method`/`results` filled from abstract sentence, `limitations` = "Not stated..." | Correctly split the one abstract sentence across method/results, limitations correctly empty | Pass |
| 4 | paper_04_long_multisection.txt — ~2000 words, 9 sections | Normal | Chunked into 3+, merged into one coherent summary, all numbers preserved | Chunked into 3, 7 evidence records, summary correct (see saved JSON) | Pass |
| 5 | paper_05_shopping_list.txt — not a paper at all | Invalid | All 4 fields = "Not stated in the retrieved sections." (or a clear rejection) | P1 still forced a tag on 2 items ("call mom", "pick up dry cleaning") as `problem`-relevant; P3 produced a nonsense "problem: managing daily household tasks" summary | **Fail** |
| 6 | paper_06_non_english.txt — Hindi-language paper | Edge | Summary in English (target audience is students using this tool) | Summary correctly structured but written in Hindi, mirroring input language | **Fail** |
| 7 | paper_07_contradictory_numbers.txt — abstract says 40%, results section says 26% | Edge | Summary flags or resolves the discrepancy, or at minimum uses the more precise results-section figure | Summary used the abstract's "40%" figure; P4 did not flag it because it IS supported by a chunk (the abstract), so the contradiction with the results section was never surfaced | **Fail** |
| 8 | paper_08_results_only_fragment.txt — ablation table only, no narrative | Edge | `problem`/`method` = "Not stated...", `results` = ablation findings (attention pooling -6.8pts, pretraining -11.7pts) | Correct — results field accurately summarized the table, problem/method correctly empty | Pass |
| 9 | paper_09_normal_short.txt — duplicate bug report detector | Normal | Correct 4-section summary, 29% triage-time figure preserved | Correct summary, all sentences traced | Pass |
| 10 | paper_10_garbled_ocr.txt — OCR-corrupted scan, missing accuracy numbers | Invalid | `results`/`limitations` = "Not stated..." rather than inventing a number for "X%" | Correctly left results as "Not stated in the retrieved sections." and did not invent a number for the "X%" placeholder | Pass |

**Score: 7 pass / 3 fail.**

## Known limitations surfaced by this test table (carried into Section 4 of the Milestone 2 PDF)

1. **No input-type gate.** Row 5 shows the chain will force a "summary" out of
   clearly non-paper text instead of refusing. *Next:* add a P0 classifier
   step before P1 that rejects input not resembling a research paper.
2. **No output-language pin.** Row 6 shows the summary mirrors the input
   language instead of always producing English for the student reader.
   *Next:* add an explicit "always respond in English" instruction to the P3
   system prompt, regardless of source language.
3. **P4 checks support, not cross-section consistency.** Row 7 shows a
   hallucination-check limitation: P4 only verifies a sentence is *supported
   by some chunk*, so a number that is technically present in the abstract
   but contradicted by the results section is never flagged. *Next:* add a
   numeric-consistency pass that compares all extracted numbers for the same
   quantity across chunks before synthesis.
4. **Implicit limitations in a Conclusion are sometimes missed by P1's
   zero-shot tagging** if they aren't under a heading literally called
   "Limitations" (seen while tuning on earlier drafts of paper_02/paper_09).
   *Next:* add 1-2 worked examples of implicit-limitation phrasing
   ("we leave X to future work") to the P1 system prompt.
