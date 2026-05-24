# Gaps register — AI Pair Engineer

Open questions and deferred decisions. Each row has an explicit revisit
trigger. Slug convention: plain `GAP-NNN` for general gaps, `GAP-NNN-Q` for
clarification questions to a stakeholder, `GAP-NNN-EVAL` for technical claims
we will revisit with evidence, `GAP-NNN-SEC` for security items.

| ID | Title | Why deferred | Revisit trigger | Priority |
|---|---|---|---|---|
| GAP-P1-001-EVAL | Single-call vs. multi-step ReAct agent | Single call wins on v1 latency and debuggability (ADR-001). Multi-step is the higher-ceiling shape for long files and tool-using reviews. | Real-user feedback shows missed flaws on files >300 lines, or any request to actually execute the proposed tests. | P1 |
| GAP-P1-002 | Python-only language support | v1 prompt is Python-specific; the example flaws and test scaffolds assume pytest. Polyglot needs per-language examples in the prompt and AST-style hints. | Any non-Python user request, or any internal demo against a JS/TS/Go file. | P1 |
| GAP-P1-003-SEC | User-pasted code as prompt-injection vector | User input is concatenated into the model prompt. Currently mitigated by (a) structured-output schema constraining the model to a fixed JSON shape, (b) not executing the submitted code anywhere, and (c) rendering output via `st.write` not `unsafe_allow_html`. A real STRIDE-style threat model has not been written. | Before any public deployment, or before adding a feature that executes/imports the submitted code. | P1 |
| GAP-P1-004 | No eval harness | Quality is asserted by hand on `examples/buggy.py` only. There is no held-out set, no recall measurement, no regression guard. | Before any non-trivial prompt change, or before claiming a quality improvement. | P1 |
| GAP-P1-005-Q | What does "design flaw" mean to a real user? | The taxonomy (error-handling, naming, complexity, missing-test-surface, etc.) is the author's guess. A short user interview would tighten the categories. | First five external users, or first complaint that a category was confusing. | P1 |
| GAP-P1-006 | Spec-vs-implementation drift on the retry path | S-001 and T-001 reference "single retry on schema-validation failure." `reviewer.py` instead forces shape via `tool_choice`, making a retry path dead code in practice. Surfaced by the final-pass HITL review (R-001). Either reword the spec to match the implementation, or add a defensive retry for the rare API-error case where the tool block is missing. | Next time the spec or `reviewer.py` is touched, whichever comes first. | P1 |
| GAP-P2-001 | Streaming output | Current UX blocks until the full JSON is returned. Streaming is a UX win, not a correctness win, and complicates the JSON-validation path. | When p95 review time exceeds 8s on real files, or on first user feedback about perceived latency. | P2 |
| GAP-P2-002 | IDE/CLI integration | The natural v2 surface for a working developer. Streamlit is the demo surface (ADR-003). | After the prompt and output shape stabilise — moving the surface before then doubles the work. | P2 |
| GAP-P2-003 | Telemetry on dev acceptance rate per suggestion category | Needed to actually improve the prompt over time. Without it, prompt iteration is vibes. | After GAP-P2-002 ships — a real surface gives us real signal on which suggestions get applied. | P2 |
| GAP-P2-004 | Multi-file PR review with cross-file context | One file in, one review out today. Real PRs touch multiple files and call across them. Different agent shape — likely retrieval + multi-step. | When single-file mode is in regular use and users ask for it, not before. | P2 |
| GAP-P2-005 | Fine-tuned grader for the eval harness | A self-graded eval is circular. A small fine-tuned judge or a held-out human-labelled set is the right shape. Premature until GAP-P1-004 exists at all. | After the eval harness has been in use for one prompt-iteration cycle. | P2 |
