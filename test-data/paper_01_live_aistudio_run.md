# Live run — Google AI Studio (Gemini), test row 1

Reproduced the full P1→P2→P3→P4 chain manually in Google AI Studio chat
(no API key, no code) on `paper_01_normal.txt`. Shareable chat:
https://ai.studio/apps/e7499add-b434-4868-aa8b-2ab4348ef3cf

## P1 output
```json
{
  "chunk_index": 1,
  "relevant_to": ["problem", "method", "results", "limitations"],
  "reason": "The chunk contains the full paper text covering the edge inference batching problem, the ABC scheduling method and experimental setup, empirical latency and throughput results, and explicit hardware and evaluation limitations."
}
```

## P2 output
```json
[
  {"field": "problem", "quote": "Static batch sizes either waste throughput when traffic is low\nor blow latency budgets when traffic spikes.", "paraphrase": "Using a static batch size either leaves throughput underutilized during low traffic or exceeds latency budgets during traffic spikes."},
  {"field": "method", "quote": "ABC maintains a sliding window of the last 200 request arrival and completion\ntimestamps. Every 50ms, it computes the current queueing delay percentile and\ncompares it against a target latency budget set by the operator. If the\nestimated delay is below 70% of budget, ABC increases the next batch size by\none; if above 90% of budget, it decreases the next batch size by one, down to\na minimum of 1.", "paraphrase": "Every 50ms, ABC evaluates a queueing delay percentile over a sliding window of the last 200 request arrival and completion timestamps against an operator-set latency budget, increasing the batch size by one below 70% of the budget and decreasing it by one (to a minimum of 1) above 90%."},
  {"field": "results", "quote": "On the bursty trace, ABC reduced p99 latency by 34% on average across the\nthree models compared to the best-performing fixed batch size, while keeping\nthroughput within 3% of the fixed-batch-8 baseline. On the steady low-traffic\ntrace, ABC matched fixed-batch-1 latency while improving throughput by 18%\nby occasionally batching requests that arrived close together.", "paraphrase": "Across the three evaluated models, ABC lowered average p99 latency by 34% on bursty traffic while keeping throughput within 3% of fixed-batch-8, and achieved 18% higher throughput than fixed-batch-1 at matching latency on steady low traffic."},
  {"field": "limitations", "quote": "Our evaluation used three specific model architectures and two traffic\ntraces from a single retail camera deployment; results may not transfer\ndirectly to other domains such as audio or text workloads. ABC's 50ms control\ninterval was tuned by hand for the Jetson Orin Nano and would likely need\nretuning on substantially faster or slower hardware. We did not test ABC\nunder adversarial traffic patterns designed to induce oscillation, and we\nleave a formal stability analysis of the controller to future work.", "paraphrase": "The evaluation covered only three model architectures and two retail camera traces, used a 50ms control interval hand-tuned for the Jetson Orin Nano, and did not include adversarial oscillation tests or a formal stability analysis."}
]
```

## P3 output
```json
{
  "title": "Adaptive Batching for Low-Latency Inference on Edge GPUs",
  "problem": "Using a static batch size leaves throughput underutilized and wastes capacity when traffic is low. Conversely, when traffic spikes, static batch sizes exceed and blow latency budgets.",
  "method": "ABC tracks a sliding window of the last 200 request arrival and completion timestamps. Every 50ms, it computes the current queueing delay percentile and compares that estimate against a target latency budget set by the operator. If the estimated delay is below 70% of the budget, ABC increases the next batch size by one, and if it is above 90% of the budget, ABC decreases the next batch size by one down to a minimum of 1.",
  "results": "On the bursty trace, ABC reduced p99 latency by an average of 34% across the three evaluated models compared to the best-performing fixed batch size, while keeping throughput within 3% of the fixed-batch-8 baseline. On the steady low-traffic trace, ABC matched fixed-batch-1 latency while improving throughput by 18% by occasionally batching requests that arrived close together.",
  "limitations": "The evaluation used only three specific model architectures and two traffic traces from a single retail camera deployment, meaning the results may not transfer directly to other domains such as audio or text workloads. Furthermore, ABC's 50ms control interval was tuned by hand for the Jetson Orin Nano and would likely need retuning on substantially faster or slower hardware. The controller was also not tested under adversarial traffic patterns designed to induce oscillation, and a formal stability analysis is left to future work."
}
```

## P4 output (hallucination check)
Every sentence in all four fields came back fully supported by chunk 1,
`corrected_text` identical to the P3 draft — no hallucinations found in this
run.

**Outcome: matches the predicted output in `paper_01_actual_output.json` —
Pass, reproduced live on Gemini via Google AI Studio (no API key, no code
deployment).**
