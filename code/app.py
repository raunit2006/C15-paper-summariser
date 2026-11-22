"""
C15 - Research Paper Summariser for Students
Streamlit prototype. Paste or upload a paper; get a structured summary
(Problem / Method / Results / Limitations) with a hallucination-check pass
run against the source text.

Run: streamlit run code/app.py
Needs: ANTHROPIC_API_KEY set in the environment, or entered in the sidebar.
"""
import streamlit as st
from pipeline import summarise

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

st.set_page_config(page_title="Paper Summariser", page_icon="📄")
st.title("📄 Research Paper Summariser")
st.caption(
    "Paste a paper (or upload a PDF). The app chunks it, extracts evidence, "
    "synthesizes a 4-section summary, then checks every sentence against the "
    "source paper before showing you anything."
)

with st.sidebar:
    api_key = st.text_input("Anthropic API key", type="password",
                             help="Only needed if ANTHROPIC_API_KEY is not already set in the environment.")
    st.markdown("---")
    st.markdown("**Pipeline**\n1. Chunk + tag relevance (P1)\n2. Extract quoted evidence (P2)\n3. Synthesize summary (P3)\n4. Hallucination check (P4)")

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
pasted = st.text_area("...or paste paper text here", height=200)

paper_text = None
if uploaded is not None:
    if PdfReader is None:
        st.error("pypdf is not installed. Run: pip install pypdf")
    else:
        reader = PdfReader(uploaded)
        paper_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
elif pasted.strip():
    paper_text = pasted

if st.button("Summarise", type="primary", disabled=not paper_text):
    with st.spinner("Running the 4-step prompt chain..."):
        try:
            result = summarise(paper_text, api_key=api_key or None)
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

    st.success(f"Done — {result['n_chunks']} chunk(s), {result['n_evidence_records']} evidence record(s).")

    st.subheader(result["checked_summary"]["title"])
    for field in ["problem", "method", "results", "limitations"]:
        st.markdown(f"**{field.capitalize()}**")
        st.write(result["checked_summary"].get(field, "Not stated in the retrieved sections."))

    with st.expander("Hallucination check detail (what was flagged/corrected)"):
        for check in result["hallucination_checks"]:
            st.markdown(f"**{check['field']}**")
            if check["unsupported_sentences"]:
                st.warning("Unsupported in original draft:\n- " + "\n- ".join(check["unsupported_sentences"]))
            else:
                st.caption("No unsupported sentences found.")
            st.caption(f"Supported by chunks: {check['supporting_chunk_ids']}")

    with st.expander("Raw pre-check summary (P3 output, before P4 correction)"):
        st.json(result["raw_summary"])

    with st.expander("Full trace (per-chunk tagging + extraction)"):
        st.json(result["trace"])
