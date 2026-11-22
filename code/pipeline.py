"""
Core P1->P4 prompt chain for the research paper summariser (C15).
Reads prompt templates from prompts/final/ so the code and the documented
prompt sheets never drift apart.
"""
import json
import os
import re
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-5"
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts" / "final"

CHUNK_WORD_SIZE = 700  # ~800-1000 tokens


def chunk_paper(text: str) -> list[str]:
    """Split paper text into paragraph-respecting chunks of ~CHUNK_WORD_SIZE words."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        words = para.split()
        if current_len + len(words) > CHUNK_WORD_SIZE and current:
            chunks.append("\n\n".join(current))
            current, current_len = [], 0
        current.append(para)
        current_len += len(words)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _extract_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
        if line:
            return line[:120]
    return "Untitled"


def _call(client: anthropic.Anthropic, system: str, user: str, temperature: float) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def _parse_json_loose(raw: str):
    """Model output should be pure JSON; strip code fences defensively."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE)
    return json.loads(raw)


def run_p1(client, paper_title, chunk_index, total_chunks, chunk_text):
    system = (
        "You are a research paper triage assistant. You read one chunk of text "
        "at a time from a longer academic paper and decide which summary "
        "categories it is relevant to. You never summarize content here only "
        "tag relevance. You are conservative: if a chunk only mentions a topic "
        "in passing, you still tag it."
    )
    user = f"""Paper title: {paper_title}
Chunk index: {chunk_index} of {total_chunks}

Chunk text:
\"\"\"
{chunk_text}
\"\"\"

Return a JSON object with this exact shape:
{{"chunk_index": {chunk_index}, "relevant_to": ["problem"|"method"|"results"|"limitations", ...], "reason": "one short sentence"}}
Only include a category in relevant_to if the chunk contains actual content for it."""
    return _parse_json_loose(_call(client, system, user, temperature=0))


def run_p2(client, chunk_text, relevant_fields):
    if not relevant_fields:
        return []
    system = (
        "You are extracting evidence from one chunk of a research paper. You "
        "only use words and facts present in the chunk given to you. If the "
        "chunk does not actually contain enough information for a field, omit "
        "that field rather than guessing. Every paraphrase must be traceable "
        "to a quote you also provide from the same chunk."
    )
    user = f"""Chunk text:
\"\"\"
{chunk_text}
\"\"\"

Fields to extract: {relevant_fields}

For each field, return an object: {{"field": "...", "quote": "exact substring from the chunk", "paraphrase": "one sentence"}}
Return a JSON array. Drop a field entirely if you cannot find a supportable quote."""
    return _parse_json_loose(_call(client, system, user, temperature=0))


def run_p3(client, paper_title, evidence_records):
    system = (
        "You are writing a structured summary of an academic paper for a "
        "student doing a literature review. Merge and de-duplicate the given "
        "evidence records into exactly four sections: Problem, Method, "
        "Results, Limitations, 2-5 sentences each. Only use information in "
        "the evidence records. If a section has no supporting evidence, write "
        "'Not stated in the retrieved sections.' instead of inventing content."
    )
    user = f"""Paper title: {paper_title}

Evidence records ({len(evidence_records)} total):
{json.dumps(evidence_records, ensure_ascii=False)}

Output JSON: {{"title": "...", "problem": "...", "method": "...", "results": "...", "limitations": "..."}}"""
    return _parse_json_loose(_call(client, system, user, temperature=0.2))


def run_p4(client, summary, chunks):
    numbered = "\n\n".join(f"[chunk {i+1}]\n{c}" for i, c in enumerate(chunks))
    system = (
        "You are a fact-checker. For every sentence in the given summary, "
        "find a chunk number that supports it. If you cannot find support, "
        "mark it unsupported and rewrite it to only say what the chunks "
        "support, or remove it. Output valid JSON only."
    )
    user = f"""Summary to check:
{json.dumps(summary, ensure_ascii=False)}

Full paper, numbered chunks:
{numbered}

Return a JSON array of 4 objects (problem, method, results, limitations), each:
{{"field": "...", "original_sentence_count": N, "supported_sentences": [...], "unsupported_sentences": [...], "supporting_chunk_ids": [...], "corrected_text": "..."}}"""
    return _parse_json_loose(_call(client, system, user, temperature=0))


def summarise(paper_text: str, api_key: str | None = None) -> dict:
    """Full P1->P4 chain. Returns dict with summary, checked summary, and trace."""
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    title = _extract_title(paper_text)
    chunks = chunk_paper(paper_text)

    evidence_records = []
    trace = []
    for i, chunk in enumerate(chunks, start=1):
        tag = run_p1(client, title, i, len(chunks), chunk)
        records = run_p2(client, chunk, tag.get("relevant_to", []))
        evidence_records.extend(records)
        trace.append({"chunk_index": i, "tag": tag, "records": records})

    summary = run_p3(client, title, evidence_records)
    checks = run_p4(client, summary, chunks)

    checked_summary = {"title": title}
    for field_check in checks:
        checked_summary[field_check["field"]] = field_check["corrected_text"]

    return {
        "title": title,
        "n_chunks": len(chunks),
        "n_evidence_records": len(evidence_records),
        "raw_summary": summary,
        "checked_summary": checked_summary,
        "hallucination_checks": checks,
        "trace": trace,
    }
