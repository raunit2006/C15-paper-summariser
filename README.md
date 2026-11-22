# C15 — Research Paper Summariser for Students

Turns a research paper into a structured, four-section summary (Problem,
Method, Results, Limitations) for a student doing a literature review —
with long-document chunking and a hallucination-check pass against the
source paper before anything is shown.

**Team:** ThinkSync (Team ID: PE-B49-38, Batch-60)
**Faculty:** Ankit Vijay Bansal
**Members:**
- S24CSEU1906 – Krish Kumar
- S24CSEU1904 – Raunit Singh
- S24CSEU2264 – Daivik Kumar Rawat
- S24CSEU2640 – Kandarp Manucha
- S24CSEU1926 – Akshay Maria

**Repository:** https://github.com/raunit2006/C15-paper-summariser
**Prototype link:** https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221C_FcdfD-NJYobgZL8KHbzOW3zcR3EpkB%22%5D,%22action%22:%22open%22,%22userId%22:%22108873368678706490010%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing
(sign in with any Google account to view — normal login, no access request needed)

## What it does

1. **Chunk** the paper into ~700-word, paragraph-respecting pieces
   (`code/pipeline.py:chunk_paper`). Short papers stay as 1 chunk; the long
   test paper (`test-data/paper_04_long_multisection.txt`) splits into 3.
2. **P1 — tag** each chunk for which of Problem/Method/Results/Limitations
   it's relevant to.
3. **P2 — extract** quoted evidence (quote + one-line paraphrase) per
   relevant field, per chunk. Nothing is paraphrased without a quote to
   back it.
4. **P3 — synthesize** all evidence records across every chunk into one
   four-section summary.
5. **P4 — hallucination check**: every sentence in the draft summary is
   checked against the numbered source chunks; anything unsupported is
   flagged and rewritten or removed before the user sees it.

See `prompts/final/` for the exact prompt text of all four steps, and
`docs/prompt_iteration_log.md` for how P4 (the hallucination check) evolved
across 3 real versions.

## How to run it

```bash
cd code
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

Paste paper text or upload a PDF, click Summarise. The Anthropic API key can
also be entered directly in the sidebar instead of being set as an env var.

## Repository structure

```
README.md              This file
prompts/
  v1/, v2/, v3/         Iteration history of the P4 hallucination-check prompt
  final/                The 4 shipped prompt sheets (P1-P4), full format in each file
code/
  pipeline.py           chunk_paper() + run_p1..run_p4() + summarise()
  app.py                Streamlit UI
test-data/
  paper_0X_*.txt         10 test inputs (3 normal, 5 edge, 2 invalid)
  paper_01/04_actual_output.json   Full saved traces for 2 representative runs
  test_results.md        Full test table (pass/fail) + known limitations
docs/
  make_diagrams.py       Generates the 4 diagrams below from the real pipeline
  prompt_workflow.png, task_decomposition.png, input_output_flow.png,
  system_architecture.png
  prompt_iteration_log.md
CHANGELOG.md
```

## Known limitations (see `test-data/test_results.md` for the failing tests behind these)

- No gate rejects non-paper input (it will still try to "summarise" a
  shopping list).
- Summary language mirrors the input paper's language instead of always
  being English.
- The hallucination check verifies support, not cross-section numeric
  consistency (an abstract's number and a results-section number can both be
  individually "supported" while contradicting each other).
