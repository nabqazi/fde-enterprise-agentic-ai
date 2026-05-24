# How I built this — the workflow, not the artifact

This repository is my submission for the Careem AI-augmented coding challenge, written against the Founding Forward Deployed Engineer (WorkOS — Enterprise Agentic AI) job posting. The brief offered three challenges and roughly 30–60 minutes. I picked challenge #2 — the **AI Pair Engineer** — and gave myself a hard 30-minute sprint.

The deliverable is intentionally two things:

1. A working Streamlit app under [`src/`](./src/) that reviews a Python file and returns design flaws, proposed pytest cases, and one focused refactor.
2. **The full trail of artifacts that produced it** — charter, ADRs, gaps register, spec, dev-ticket handed to a coding agent, and the HITL review log that gated the merge.

The artifact is the easy part. The trail is the point. For a Forward Deployed Engineer role at an agentic-AI division, the question is not "can you ship a small app with Claude" — it is "do you have a methodology for putting agents into other people's workflows that does not produce slop and does not ship security holes." This repo is my answer to that question, applied to a tiny problem so it fits in 30 minutes.

## How to read this repo

In order, top to bottom:

1. [`PROTOCOL.md`](./PROTOCOL.md) — the working principles I apply when collaborating with AI coding agents. One page. Lock-or-register, MCQ-before-silent-pick, blocking HITL gates, anti-hallucination rails. This is the "how I work" reference; everything else in the repo is an instance of it.
2. [`foundation/00-charter-and-adrs.md`](./foundation/00-charter-and-adrs.md) — what the product is, what it explicitly is **not**, and the four architecture decisions I locked before any code was written. Each ADR has a tradeoff and lists the alternatives I considered. Decisions I did not want to lock yet became gap rows instead, never silent picks.
3. [`GAPS-REGISTER.md`](./GAPS-REGISTER.md) — ten open decisions, each with a revisit trigger and a priority (P1 or P2). The P1/P2 split is the explicit backlog for what would happen in session two.
4. [`specs/S-001-mvp.md`](./specs/S-001-mvp.md) — the MVP spec in Given/When/Then form. Six scenarios cover happy path, clean-code, non-Python input, API error, missing key, and safe output rendering.
5. [`dev-tickets/T-001-mvp-build.md`](./dev-tickets/T-001-mvp-build.md) — the handoff to the autonomous coding agent. Exact file list, per-file scope, an explicit Do-NOT list of seven anti-hallucination rails, runnable success criteria, and the two blocking HITL gates required before "done."
6. [`src/`](./src/) — what the agent produced. Eight files. No more.
7. [`reviews/R-001-hitl-log.md`](./reviews/R-001-hitl-log.md) — the human gate. What I checked per file, the five items I rejected or refined before approval, two items I accepted as-is with rationale, and the security checklist outcome.

Reading in that order takes ten minutes and walks through the methodology end-to-end.

## The 30-minute constraint as a feature

Thirty minutes is not enough to build everything someone could reasonably want from an "AI Pair Engineer." Pretending otherwise produces a sprawling toy. The discipline move is to make the priority ladder explicit and to make the cuts visible.

- **P0 — shipped this session.** Single-call architecture, Python-only, structured-output via Claude tool-use, Streamlit demo surface, one focused refactor per review (not a multi-hunk rewrite), HITL log signed off.
- **P1 — registered in the gap register, queued for session two.** Multi-step ReAct agent for long files (GAP-P1-001-EVAL), polyglot support (GAP-P1-002), real STRIDE-style threat model (GAP-P1-003-SEC), eval harness on a held-out buggy-file set (GAP-P1-004), user interviews to validate the flaw taxonomy (GAP-P1-005-Q).
- **P2 — longer-horizon, also registered.** Streaming output (GAP-P2-001), IDE/CLI surface as the real product (GAP-P2-002), telemetry on dev acceptance rate per category (GAP-P2-003), multi-file PR review (GAP-P2-004), fine-tuned grader for the eval harness (GAP-P2-005).

Every cut is named, has a reason, and has a revisit trigger. Nothing was dropped silently.

## Where AI augmented me, and where the human gated

This is the part of the workflow worth narrating, because it is the part the role is hiring for.

**Investigate and charter.** I used Claude as a brainstorming partner to pressure-test the challenge framing — "what does the FDE-WorkOS role actually grade against, and which of the three challenges best showcases that?" I rejected challenge #3 as under-engineered for a founding role and rejected challenge #2's most expansive framing ("design an IDE plugin") as scope-incompatible with 30 minutes. The output of that phase is the charter and the "What it is NOT" section, which is where most of the value lives — a sharp negative scope.

**Lock or register.** Every real architectural choice became either an ADR or a gap row. ADR-001 (single-call vs. multi-step) is the load-bearing one — multi-step is the higher-ceiling shape, but its failure modes (tool-loop divergence, step-budget exhaustion, harder debugging) make it the wrong v1 choice on a tight budget. I locked single-call and registered the multi-step revisit as GAP-P1-001-EVAL with a concrete trigger ("real-user feedback shows missed flaws on files >300 lines"). The discipline is that I do not get to silently re-decide this; the next person to touch the agent shape sees the deferred decision and the trigger.

**Spec.** [`S-001-mvp.md`](./specs/S-001-mvp.md) is short on purpose. Six Given/When/Then scenarios cover the happy path, the no-flaws-found path (which a sloppy spec would forget), the non-Python edge (so the model is not invited to hallucinate a JavaScript review), the API-error edge, the missing-key edge, and the safe-rendering invariant (no `unsafe_allow_html`). These are the same scenarios that show up as the dev-ticket's success criteria, which is the point.

**Handoff to the coding agent.** This is the doc that does the most work to keep the agent honest. [`T-001-mvp-build.md`](./dev-tickets/T-001-mvp-build.md) gives the coding agent (1) the exact file list and forbids any other files, (2) per-file scope in 2–4 sentences each, (3) a Do-NOT list naming the specific failure modes (no `langchain`/`llamaindex`, no `exec`/`eval` on user input, no `unsafe_allow_html`, no hardcoded API key, no silent scope expansion into P1 items), (4) literal success criteria that are checkable, and (5) the requirement that the agent does not declare done — the human does, at the HITL gate. Without that ticket, the agent would have invented a `core/`, `services/`, `utils/` structure and reached for a framework. With it, it shipped exactly eight files.

**Build.** A coding subagent wrote the code under [`src/`](./src/) against T-001. Single Anthropic Claude call (`claude-sonnet-4-6`) with a tool-use-shaped structured output schema, dataclass-validated, no agent framework, no executed user code, no XSS surface. I did not write the code line by line; the ticket was scoped tightly enough that the agent's freedom was bounded to the right shape.

**HITL gate.** [`R-001-hitl-log.md`](./reviews/R-001-hitl-log.md) records the gate. Five items rejected or refined — the `os.environ` subscript that would `KeyError` on a missing key, an early prompt that let the model invent line numbers, an `unsafe_allow_html` XSS surface in the first app draft, a refactor section that returned a full rewrite instead of one focused change, and an over-dense example file. Two accepted as-is with rationale. Security checklist run across five items: prompt injection, API-key handling, output rendering, code execution, dependency surface. Items not Pass carry a GAP id; nothing waved through.

The gate is **blocking**. The dev-ticket says so explicitly: "the agent does not declare done; the human does." This is the discipline that keeps AI slop and security vulnerabilities out of "production" — even when production is a 30-minute demo.

## The artifact, briefly

Streamlit single page. Paste a Python function or file. Click Review. The app runs one Claude call with a forced `submit_review` tool, validates the structured response, and renders three sections plus a confidence-and-caveats footer. Non-Python input is rejected client-side without an API call. Missing key shows setup instructions, not a stack trace. [`examples/buggy.py`](./src/examples/buggy.py) is a ~50-line file with three deliberate flaws of different categories — load it with the "Load example" button and click Review to see the end-to-end flow.

To run: `streamlit run src/app.py` from the repo root, after `pip install -r src/requirements.txt` and an `ANTHROPIC_API_KEY` in `src/.env`.

## Why this generalizes to the FDE mandate

A Forward Deployed Engineer at an enterprise-agentic-AI division does not get to ship slop into a customer's workflow and figure it out later. The customer's data, the customer's compliance posture, and the customer's tolerance for "the AI hallucinated a thing" are all bounded. The agent has to be scoped, locked, and gated before it touches anything that matters.

The loop in this repo — investigate → lock-or-register → spec → handoff with rails → build → HITL gate — is the same loop at any scale. Replace "Streamlit app reviewing a Python file" with "agent that triages incoming partner integration requests," and the methodology is unchanged. The ticket gets longer; the rails get sharper; the HITL gates add a security review with a real STRIDE pass and a compliance sign-off. The shape is identical. That portability is what I am offering — not the Streamlit app.

## What I would do next, if this were a real session two

In order: ship GAP-P1-003-SEC (the real threat model) before anything else, because it is the only blocker against deploying the v1 surface to a public link. Then GAP-P1-004 (the eval harness), because every prompt change after that point without it is vibes-based. Then GAP-P1-001-EVAL (the multi-step ReAct prototype) on a held-out long-file set, A/B-graded against the v1 single-call baseline. Polyglot (GAP-P1-002) waits until the eval harness can grade non-Python. P2 items are queued behind those four, in the order they appear in [`GAPS-REGISTER.md`](./GAPS-REGISTER.md).

That sequencing is itself a small system-design choice, and it is in this document rather than the gap register because the register holds the gaps, not the order they are resolved in. The order belongs in the next session's planning doc, which does not exist yet.

---

Thank you for reading. Happy to walk through any of these artifacts live.
