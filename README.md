# AI Pair Engineer

A 30-minute sprint built for the **Founding Forward Deployed Engineer — Enterprise Agentic AI** application. Challenge #2 ("the AI Pair Engineer") implemented as a working Streamlit app, alongside the full discipline trail that produced it.

**The trail is the point.** The artifact is small on purpose. The methodology — investigate → lock-or-register → spec → handoff with anti-hallucination rails → build → blocking HITL gate — generalizes to any agent deployment, which is the FDE muscle this role is hiring for.

## Start here

**[WORKFLOW.md](./WORKFLOW.md)** — the application-facing narrative. Walks the reader through every artifact in order, explains where AI augmented the work and where the human gated. Ten minutes to read.

## How the repo is organized

```
ai-pair-engineer/
├── WORKFLOW.md                          The application narrative. Start here.
├── PROTOCOL.md                          One-page methodology reference.
├── foundation/
│   └── 00-charter-and-adrs.md           Problem, scope, four ADRs with tradeoffs.
├── GAPS-REGISTER.md                     Ten open decisions with revisit triggers (P1/P2).
├── specs/
│   └── S-001-mvp.md                     MVP spec, Given/When/Then.
├── dev-tickets/
│   └── T-001-mvp-build.md               Handoff to the coding agent. The anti-hallucination doc.
├── reviews/
│   └── R-001-hitl-log.md                Human review log. What was rejected, security checklist.
└── src/                                 The Streamlit demo. Eight files, no more.
    ├── app.py
    ├── reviewer.py
    ├── prompts.py
    ├── examples/buggy.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md
```

## Run the demo

From the repo root:

```bash
cd src
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env and paste your ANTHROPIC_API_KEY
streamlit run app.py
```

Click "Load example" to populate the text area with [`src/examples/buggy.py`](./src/examples/buggy.py), then click "Review." You get three sections back — design flaws, proposed pytest cases, and one focused before/after refactor — plus a confidence and caveats footer.

## The P0 / P1 / P2 ladder

What shipped this session, and what is queued.

- **P0 (shipped).** Single-call Anthropic Claude review, structured-output via tool-use, Python-only, Streamlit demo surface, HITL log signed off, security checklist green or registered as a gap.
- **P1 (registered).** Multi-step ReAct agent for long files, polyglot support, real STRIDE-style threat model, eval harness, user-interview validation of the flaw taxonomy. All five in [`GAPS-REGISTER.md`](./GAPS-REGISTER.md) with concrete revisit triggers.
- **P2 (registered).** Streaming output, IDE/CLI as the real surface, telemetry on suggestion-acceptance rate, multi-file PR review, fine-tuned grader for the eval harness.

Nothing was cut silently. Every cut has a reason and a trigger.

## A note on the brief

The brief offered 30–60 minutes. I gave myself a hard 30. The discipline of the constraint is part of what is being shown — ruthless scoping and explicit priority gates are FDE muscle.
