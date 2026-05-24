# Charter and ADRs — AI Pair Engineer

Merged for compression. Charter first, then the four ADRs that bound v1.

## Charter

### Problem statement

Pre-PR code review is a bottleneck and uneven across reviewers. The person who
should catch a missing edge-case test, a too-broad refactor opportunity, or a
straightforward design flaw is often the person who has the least time. The
result is a quality floor that drifts with reviewer load, not a quality floor
that holds. The opportunity is a pair-engineer pass — fast, structured, and
honest about its confidence — that runs *before* the human reviewer, so the
human spends their attention on what only humans can do.

### Users

Solo developers and small teams (≤5 engineers) who do not have a dedicated
code-review culture and who already paste snippets into chat LLMs ad-hoc. The
goal is to turn that ad-hoc habit into a structured, repeatable pass with a
predictable output shape.

### What it is

A web app where a developer pastes a single Python file or function, clicks
Review, and gets three structured outputs back:

1. **Design flaws** — 2–4 items, each with a category and a quoted line.
2. **Proposed tests** — 2–3 pytest cases targeting risk areas.
3. **Refactor suggestion** — one focused before/after diff.

Every response carries a confidence and caveats footer.

### What it is NOT

- Not an autonomous fixer. It proposes; the human applies.
- Not an IDE plugin in v1. Streamlit is the demo surface. IDE/CLI is the right
  v2 surface (see `GAPS-REGISTER.md` → GAP-P2-002).
- Not a security scanner. It will surface obvious risk patterns when they are
  inside a design flaw, but it is not a substitute for SAST. A real
  STRIDE-style threat model is queued at GAP-P1-003-SEC.
- Not multi-file or repo-aware. One file in, one review out
  (GAP-P2-004).

### Success criteria

- **Functional** — paste a Python file, get all three sections rendered, in
  under 10 seconds, with no traceback.
- **Quality** — on `examples/buggy.py`, the model surfaces the seeded flaws
  (not necessarily worded identically, but pointing at the right lines).
- **Trust** — every output carries an honest confidence and caveats footer.
  The reviewer never has to guess how sure the model was.

---

## ADR-001 — Single Claude call with structured output vs. multi-step ReAct

| Status | Date | Supersedes |
|---|---|---|
| Accepted | 2026-05-24 | — |

**Context.** A pair-engineer review can be modeled as either (a) one prompt
asking for all three outputs at once, or (b) a multi-step agent that plans,
calls tools, and iterates (e.g. ReAct over an AST tool, a test-runner tool,
etc.). Option (b) is the more powerful long-run shape.

**Decision.** Single Claude call with a structured JSON response schema for
v1.

**Consequences.** Lower latency (one round-trip), trivially debuggable (one
request, one response), and fewer failure modes (no tool-loop divergence, no
step-budget exhaustion). Ceiling on quality for long files where the model
would benefit from re-reading. Loss of tool-use composability — we cannot, for
example, actually run the proposed tests.

**Alternatives considered.** Multi-step ReAct (deferred to GAP-P1-001-EVAL);
two sequential calls (review then refactor) — rejected as the worst of both
worlds, with neither the simplicity of one call nor the power of an agent.

## ADR-002 — Anthropic Claude vs. OpenAI vs. open-source

| Status | Date | Supersedes |
|---|---|---|
| Accepted | 2026-05-24 | — |

**Context.** The reviewer needs reliable structured output and strong code
reasoning on Python. Three live options: Anthropic Claude, OpenAI GPT-class,
and a self-hosted open-source model (Qwen-Coder, DeepSeek-Coder, etc.).

**Decision.** Anthropic Claude, specifically `claude-sonnet-4-6`.

**Consequences.** Tool-use and structured-output reliability is the strongest
of the three for the JSON-shape constraint this app depends on. Strong code
reasoning, particularly on idiomatic Python. Vendor lock-in at the API
surface; mitigated by isolating the call inside `reviewer.py`. Cost per review
is non-zero but bounded by single-call architecture (ADR-001).

**Alternatives considered.** OpenAI — comparable quality, slightly weaker
tool-use adherence in our spot-checks. Open-source — defers hosting, latency,
and quality risk into v1's 30-minute build budget, which is unacceptable.

## ADR-003 — Streamlit vs. CLI vs. IDE plugin

| Status | Date | Supersedes |
|---|---|---|
| Accepted | 2026-05-24 | — |

**Context.** v1 needs a demoable surface in a 30-minute sprint. Three options:
Streamlit web app, CLI tool, IDE plugin (VS Code).

**Decision.** Streamlit, single page.

**Consequences.** Fastest path to a runnable, screen-shareable artifact. Trivial
text-area input and structured output rendering. Not where a working developer
actually lives — the IDE is. v2 surface is IDE/CLI (registered as GAP-P2-002).
Streamlit is treated as a demo surface, not a product surface.

**Alternatives considered.** CLI — narrower demo audience, but a real candidate
for v2 alongside IDE. IDE plugin — correct long-run surface, wrong v1 cost.

## ADR-004 — Structured JSON output vs. free-form markdown

| Status | Date | Supersedes |
|---|---|---|
| Accepted | 2026-05-24 | — |

**Context.** The model's three outputs (flaws, tests, refactor) can be
returned as free-form markdown for the UI to render, or as a structured JSON
object enforced by Anthropic's response-schema / tool-use feature.

**Decision.** Structured JSON via a response schema. The Streamlit UI does the
markdown rendering from the parsed object.

**Consequences.** Enforces a consistent output shape — flaws always have a
category and a quoted line, tests always have a name and a body, refactor
always has a before and after. Makes the output composable with future
consumers (PR-comment formatter, CLI, eval harness). Easier to evaluate
because each field is addressable. Tradeoff: occasional schema-validation
errors if the model emits malformed JSON, handled by a single retry and a
user-facing error.

**Alternatives considered.** Free-form markdown — simpler to prompt, harder
to evaluate, harder to compose, and the UI ends up parsing prose anyway.
