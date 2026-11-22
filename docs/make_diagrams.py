"""Generate the 4 Milestone 2 Section 2(b) diagrams as PNGs, matching the
actual pipeline in code/pipeline.py (not generic/copied diagrams)."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MplPath

plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, xy, w, h, text, fc="#eef3fb", ec="#2b4c7e", fontsize=10.5):
    x, y = xy
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                            fc=fc, ec=ec, lw=1.6)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, wrap=True)
    return (x, y, w, h)


def arrow(ax, b1, b2, label=None, rad=0.0, side1="right", side2="left"):
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    pts = {
        "right": (x1 + w1, y1 + h1 / 2), "left": (x1, y1 + h1 / 2),
        "top": (x1 + w1 / 2, y1 + h1), "bottom": (x1 + w1 / 2, y1),
    }
    pts2 = {
        "right": (x2 + w2, y2 + h2 / 2), "left": (x2, y2 + h2 / 2),
        "top": (x2 + w2 / 2, y2 + h2), "bottom": (x2 + w2 / 2, y2),
    }
    a = FancyArrowPatch(pts[side1], pts2[side2], connectionstyle=f"arc3,rad={rad}",
                         arrowstyle="-|>", mutation_scale=16, lw=1.5, color="#333")
    ax.add_patch(a)
    if label:
        mx, my = (pts[side1][0] + pts2[side2][0]) / 2, (pts[side1][1] + pts2[side2][1]) / 2
        ax.text(mx, my + 0.18, label, ha="center", fontsize=9, color="#444")


def new_fig(w=11, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


# 1. Prompt workflow (P1 -> P2 -> P3 -> P4), per paper
fig, ax = new_fig(12.5, 4.5)
b_in = box(ax, (0.3, 1.8), 1.8, 1.2, "Paper\ntext/PDF")
b_p1 = box(ax, (2.6, 1.8), 2.1, 1.2, "P1\nChunk Tagger\n(per chunk)", fc="#fde9d9")
b_p2 = box(ax, (5.2, 1.8), 2.1, 1.2, "P2\nEvidence\nExtractor\n(per chunk)", fc="#fde9d9")
b_p3 = box(ax, (7.8, 1.8), 2.1, 1.2, "P3\nSynthesizer\n(whole paper)", fc="#dff0d8")
b_p4 = box(ax, (10.1, 1.8), 2.1, 1.2, "P4\nHallucination\nCheck", fc="#f8d7da")
arrow(ax, b_in, b_p1)
arrow(ax, b_p1, b_p2)
arrow(ax, b_p2, b_p3)
arrow(ax, b_p3, b_p4)
ax.annotate("", xy=(3.65, 1.8), xytext=(3.65, 1.1),
            arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.3))
ax.text(3.65, 0.75, "loops once per chunk\n(1 chunk for short papers,\n3+ for long ones)",
        ha="center", fontsize=8.5, color="#555")
ax.set_title("Prompt workflow: P1 → P2 (looped per chunk) → P3 → P4", fontsize=13)
fig.tight_layout()
fig.savefig("prompt_workflow.png", dpi=170)
plt.close(fig)

# 2. Task decomposition
fig, ax = new_fig(11, 6.5)
root = box(ax, (4.1, 5.3), 3, 0.9, "Summarise a research paper\nfor a student", fc="#dbe7f7")
c1 = box(ax, (0.3, 3.6), 2.3, 1.0, "Chunk the paper\n(respect paragraphs,\n~700 words/chunk)")
c2 = box(ax, (2.9, 3.6), 2.3, 1.0, "Tag relevance\nper chunk (P1)")
c3 = box(ax, (5.5, 3.6), 2.3, 1.0, "Extract quoted\nevidence (P2)")
c4 = box(ax, (8.1, 3.6), 2.3, 1.0, "Synthesize 4\nsections (P3)")
c5 = box(ax, (4.1, 1.6), 2.9, 1.0, "Verify every sentence\nagainst source chunks (P4)", fc="#f8d7da")
for c in (c1, c2, c3, c4):
    arrow(ax, root, c, side1="bottom", side2="top", rad=0.0)
arrow(ax, c4, c5, side1="bottom", side2="top")
ax.set_title("Task decomposition", fontsize=13)
fig.tight_layout()
fig.savefig("task_decomposition.png", dpi=170)
plt.close(fig)

# 3. Input-output flow
fig, ax = new_fig(12.6, 4)
i1 = box(ax, (0.3, 1.6), 2.0, 1.0, "Raw paper\n(PDF or pasted text)")
i2 = box(ax, (2.8, 1.6), 2.0, 1.0, "List of text\nchunks")
i3 = box(ax, (5.3, 1.6), 2.3, 1.0, "Evidence records\n{field, quote,\nparaphrase}", fc="#fde9d9")
i4 = box(ax, (8.1, 1.6), 2.0, 1.0, "Draft 4-section\nJSON summary", fc="#dff0d8")
i5 = box(ax, (10.5, 1.6), 1.6, 1.0, "Checked\nsummary +\nflags", fc="#f8d7da")
for a, b in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
    arrow(ax, a, b)
ax.set_title("Input → output flow (data shape at each stage)", fontsize=13)
fig.tight_layout()
fig.savefig("input_output_flow.png", dpi=170)
plt.close(fig)

# 4. System architecture
fig, ax = new_fig(11, 6.5)
ui = box(ax, (0.4, 4.8), 3.0, 1.1, "Streamlit UI\ncode/app.py", fc="#dbe7f7")
pipe = box(ax, (4.2, 4.8), 3.2, 1.1, "pipeline.py\n(chunk_paper, run_p1..p4)", fc="#eef3fb")
api = box(ax, (8.1, 4.8), 2.4, 1.1, "Anthropic API\nclaude-sonnet-5", fc="#fde9d9")
prompts = box(ax, (4.2, 2.8), 3.2, 1.0, "prompts/final/\n*.txt (P1-P4 sheets)")
testdata = box(ax, (0.4, 2.8), 3.0, 1.0, "test-data/\n10 sample papers")
docs = box(ax, (8.1, 2.8), 2.4, 1.0, "docs/\ndiagrams + PDF")
arrow(ax, ui, pipe, "paper text")
arrow(ax, pipe, api, rad=0.25)
arrow(ax, api, pipe, side1="left", side2="right", rad=0.25)
ax.text(7.3, 6.25, "prompt calls", ha="center", fontsize=9, color="#444")
ax.text(7.3, 5.65, "JSON responses", ha="center", fontsize=9, color="#444")
arrow(ax, prompts, pipe, side1="top", side2="bottom")
arrow(ax, testdata, ui, side1="top", side2="bottom")
ax.set_title("System architecture (deployed app)", fontsize=13)
fig.tight_layout()
fig.savefig("system_architecture.png", dpi=170)
plt.close(fig)

print("Wrote 4 diagrams to docs/")
