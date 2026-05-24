# R-001 — HITL review log, MVP build

Human review of the agent's output against
[`../dev-tickets/T-001-mvp-build.md`](../dev-tickets/T-001-mvp-build.md) and
[`../specs/S-001-mvp.md`](../specs/S-001-mvp.md). Gate is blocking; the agent
does not declare done.

## What I (human) reviewed

- **`src/app.py`** — checked: no `unsafe_allow_html=True`, no leaking of stack
  traces to the UI, missing-API-key path renders the setup message, API-error
  path renders a generic error, no XSS surface on rendered model output, no
  business logic that belongs in `reviewer.py`.
- **`src/reviewer.py`** — checked: API key read via `os.getenv` not subscript,
  single Anthropic call (no hidden second call, no retry loop beyond the one
  spec'd retry on schema-validation failure), errors typed and propagated not
  swallowed, response parsed into a defined shape, no `langchain` or similar
  imports.
- **`src/prompts.py`** — checked: prompt clarity, hallucination guards
  (specifically the "if unsure, omit" line), schema strictness, no
  Python-versioning assumptions in the example outputs the prompt shows the
  model.
- **`src/examples/buggy.py`** — checked: file header marks it as a demo
  fixture, flaws are distinct and pedagogically clear, file size stays
  legible.
- **`src/requirements.txt`, `.env.example`, `.gitignore`, `README.md`** —
  checked: pins are present, no key in source, `.env` is gitignored, README
  setup steps work in a fresh venv.

## Items rejected or refined

1. **API-key access pattern.** First draft of `reviewer.py` used
   `os.environ['ANTHROPIC_API_KEY']`, which raises `KeyError` on a fresh
   clone — failing the missing-API-key acceptance scenario. Refined to
   `os.getenv('ANTHROPIC_API_KEY')` with an explicit check at the top of
   `review_code` that raises a typed `ConfigError`, which `app.py` catches and
   renders as the setup message.
2. **Prompt allowed invented line numbers.** Initial system prompt asked the
   model to "cite the line number" of each flaw, which produced confident but
   wrong line numbers on multi-statement constructs. Tightened to require the
   model echo only the line *content* it can see in the input, and added the
   explicit "if unsure, omit it rather than invent" instruction now visible in
   `prompts.py`.
3. **XSS surface on rendered output.** `app.py` initially rendered the model's
   text via `st.markdown(unsafe_allow_html=True)` for nicer formatting.
   Rejected — a crafted code sample could inject script into the model's
   echoed quote. Switched to `st.write` for prose and `st.code` for code
   blocks. The format loss is acceptable.
4. **Refactor section was a full rewrite.** First draft prompt let the model
   return a multi-hunk rewrite for the Refactor section. Tightened to require
   exactly one before/after pair, honoring S-001's "one focused change" rule.
   Schema now enforces single-pair shape.
5. **`examples/buggy.py` was too dense.** Initial draft seeded ten flaws to
   stress the model. Reduced to three deliberate, distinct flaws — a bare
   `except Exception: pass` in `load_users` (error-handling), a mixed-concern
   `process_user_file` doing parse + validate + write (cohesion/complexity),
   and a misleadingly-named `last_index` driving an off-by-one in
   `summarize_ages` (naming + correctness) — so the demo stays legible and the
   success criterion ("hits the seeded flaws") is unambiguous.

## Items accepted as-is and why

1. **No pydantic.** `reviewer.py` uses a `@dataclass` and a small manual
   validator instead of pulling in pydantic for one schema. Honors the ticket's
   "do not invent project structure" rail and keeps the dependency surface to
   three packages.
2. **No explicit retry path; `tool_choice` forces the response shape.** S-001
   and T-001 both reference a "single retry on schema-validation failure." The
   shipped `reviewer.py` relies instead on `tool_choice={"type":"tool","name":"submit_review"}`,
   which the Anthropic API enforces — the response is guaranteed to be a
   tool_use block with input matching the declared schema. A separate retry
   path was therefore not implemented. This is a defensible architectural
   choice (one round-trip, simpler control flow), but it is a quiet deviation
   from the spec. Registered as a finding in the final-pass section below,
   and as GAP-P1-006 for cross-doc reconciliation.

## Security checklist outcome

| Item | Status | Mitigation / Note |
|---|---|---|
| Prompt injection (user code as prompt) | Pass with caveat | Structured-output schema constrains response shape; submitted code is never executed. Full STRIDE-style review deferred — see GAP-P1-003-SEC. |
| API-key handling | Pass | `.env` only, `os.getenv` with typed `ConfigError`, `.env` in `.gitignore`, no fallback in source. |
| Output rendering | Pass | `st.write` for prose, `st.code` for code. No `unsafe_allow_html`, no `components.v1.html`. |
| Code execution of user input | Pass | No `exec`, `eval`, `importlib`, or `subprocess` against input. Grepped the diff to confirm. |
| Dependency surface | Pass | Three pinned dependencies (`streamlit`, `anthropic`, `python-dotenv`). No agent frameworks. |

## Final pre-merge pass — what changed

A second read of every artifact end-to-end caught two real cross-doc drifts
that the first review missed. Both are recorded here for transparency, and
both produced fixes before sign-off:

1. **Example-file flaw description mismatch.** The first version of "Items
   rejected or refined" item 5 named flaws ("mutable default argument, missing
   error-handling branch, boundary bug") that do not appear in the shipped
   `src/examples/buggy.py`. The file actually plants a bare-except, a
   mixed-concern function, and an off-by-one with a misleadingly-named
   variable. The item was corrected above to match what shipped.
2. **Spec-vs-implementation drift on the retry path.** S-001 and T-001 both
   reference a "single retry on schema-validation failure." `reviewer.py`
   instead relies on `tool_choice` to force the response shape, which makes
   the retry path dead code in practice. Item 2 of "Items accepted as-is" was
   re-scoped to flag this honestly, and the question of whether to (a) reword
   the spec to match the implementation or (b) add a defensive retry is
   registered as GAP-P1-006.

The methodology point here: a second pass that finds nothing is a second pass
that wasn't really done. Two findings on a 30-minute sprint is a healthy yield.

## Sign-off

Human reviewer approved P0 ship on 2026-05-24, after the final-pass
corrections above. P1 security review queued —
see [`../GAPS-REGISTER.md`](../GAPS-REGISTER.md) → GAP-P1-003-SEC. Doc/impl
reconciliation queued — see GAP-P1-006.
