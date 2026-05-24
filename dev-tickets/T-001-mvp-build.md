# T-001 — Build the MVP

Handoff ticket for the coding agent. Read the linked artifacts first. Build
exactly the file list below. Honor the Do-NOT list. Stop at the success
criteria and hand back to the human reviewer for the HITL gate.

## Linked artifacts

- Spec: [`../specs/S-001-mvp.md`](../specs/S-001-mvp.md)
- Charter and ADRs: [`../foundation/00-charter-and-adrs.md`](../foundation/00-charter-and-adrs.md)
- Protocol: [`../PROTOCOL.md`](../PROTOCOL.md)
- Gaps register: [`../GAPS-REGISTER.md`](../GAPS-REGISTER.md)

Read all four before writing a line. The ADRs explain why the architecture is
what it is — do not relitigate them in code.

## Files to create

All paths under `/Users/nmq-ai/Repos/workdesk-ai/sdlc/ai-pair-engineer/src/`:

- `app.py`
- `reviewer.py`
- `prompts.py`
- `examples/buggy.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md`

No other files. Creating files outside this list is a rejection condition at
the review gate.

## Per-file scope

**`app.py`** — Single-page Streamlit app. One text-area for source input, one
Review button, three result sections plus the confidence footer. Imports
`review_code` from `reviewer.py` and renders the returned object. Handles the
missing-API-key, non-Python-input, and API-error paths from S-001's
acceptance criteria. No business logic beyond rendering and error display.

**`reviewer.py`** — Exposes exactly one public function:
`review_code(source: str) -> ReviewResult`. Loads `ANTHROPIC_API_KEY` via
`os.getenv` (not subscript). Issues one Anthropic `claude-sonnet-4-6` call
using the structured-output / tool-use response schema (see ADR-004). Parses
and validates the response against a `ReviewResult` shape (a small
`@dataclass` or `TypedDict` is fine; do not pull in pydantic for this).
Retries once on schema-validation failure. Raises a typed error on terminal
failure; does not catch and swallow.

**`prompts.py`** — Contains the `SYSTEM_PROMPT` string and the response-schema
definition only. No logic, no imports beyond what the schema definition
requires. The system prompt instructs the model to: identify 2–4 design flaws
with category and quoted line, propose 2–3 pytest tests, propose exactly one
focused before/after refactor, and emit a confidence/caveats footer. Includes
an explicit instruction: if unsure about a line's content, omit it rather than
invent it.

**`examples/buggy.py`** — A small Python file (roughly 40–80 lines) with three
deliberate, distinct flaws — e.g. a mutable default argument, a missing
error-handling branch, and a non-obvious off-by-one or boundary bug. Comment
header names the file as a demo fixture, not production code. Used by the
happy-path acceptance scenario.

**`requirements.txt`** — Pinned versions of `streamlit`, `anthropic`,
`python-dotenv`. Nothing else.

**`.env.example`** — One line: `ANTHROPIC_API_KEY=`. Comment above explaining
where to get a key.

**`.gitignore`** — Ignores `.env`, `__pycache__/`, `.venv/`, `*.pyc`.

**`README.md`** — Setup (clone, venv, `pip install -r requirements.txt`, copy
`.env.example` to `.env`), run (`streamlit run src/app.py`), and a one-line
pointer to the spec for anything beyond setup.

## Do NOT

- Do **not** invent a multi-file project structure (no `core/`, `services/`,
  `models/`, `utils/` directories). The file list above is the whole project.
- Do **not** import `langchain`, `llamaindex`, `crewai`, `autogen`, or any
  agent framework. Single direct Anthropic SDK call.
- Do **not** execute user-submitted code anywhere. No `exec`, no `eval`, no
  `importlib`, no `subprocess` against the input. The input is text the model
  reads, nothing more.
- Do **not** store the API key in source. `.env` only. Do not hardcode a
  fallback key, even for "dev convenience."
- Do **not** add features outside S-001. No auth, no history, no streaming,
  no language detection, no eval harness. These are registered gaps; expanding
  scope to touch them silently is a rejection condition.
- Do **not** render model output via `st.markdown(unsafe_allow_html=True)` or
  via `st.components.v1.html`. Use `st.write` for text, `st.code` for code
  blocks.
- Do **not** swallow exceptions with a bare `except`. Catch the specific
  Anthropic error types and the JSON validation error; let everything else
  surface.

## Success criteria

- `pip install -r requirements.txt` completes cleanly in a fresh venv.
- `streamlit run src/app.py` starts the app without error.
- Pasting the full contents of `src/examples/buggy.py` and clicking Review
  returns all three sections plus the confidence footer, end-to-end, in under
  ten seconds.
- Pasting non-Python text (e.g. a paragraph of English or a snippet of JS)
  returns the Python-only message from S-001, with no traceback and no
  hallucinated review.
- Removing or blanking `ANTHROPIC_API_KEY` shows the setup message, with no
  KeyError.
- No file exists outside the listed paths.

## HITL gates before "done"

1. **Code review gate** — human reads the diff against this ticket. File list,
   Do-NOT list, and success criteria are checked literally. Findings logged
   in [`../reviews/R-001-hitl-log.md`](../reviews/R-001-hitl-log.md).
2. **Security gate** — human runs the security checklist (prompt injection,
   API-key handling, output rendering, code execution, dependency surface) and
   records the outcome in the same review log. Items not Pass must carry a
   GAP id.

Both gates are blocking. The agent does not declare done; the human does.
