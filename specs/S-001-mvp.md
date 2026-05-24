# S-001 — AI Pair Engineer MVP

## Goal

A developer pastes a Python file or function into a single-page web app,
clicks Review, and receives three structured outputs — design flaws, proposed
tests, and one focused refactor — plus an honest confidence footer, in under
ten seconds.

## In scope

- Single-page Streamlit app with a text-area input and a Review button.
- One Anthropic Claude API call per submission (`claude-sonnet-4-6`),
  configured for structured JSON output.
- Output section 1: 2–4 design flaws, each with a category label and a quoted
  line from the source.
- Output section 2: 2–3 pytest test cases targeting risk areas the model
  identifies.
- Output section 3: one focused before/after refactor diff — not a rewrite.
- Confidence and caveats footer on every response.
- API key sourced from `.env` via `python-dotenv`, never from source.

## Out of scope

- Multi-step or tool-using agent loop (see `../GAPS-REGISTER.md`
  → GAP-P1-001-EVAL).
- Languages other than Python (GAP-P1-002).
- Eval harness or held-out benchmark (GAP-P1-004).
- Streaming output (GAP-P2-001).
- IDE or CLI surface (GAP-P2-002).
- Multi-file or repo-aware review (GAP-P2-004).
- Formal threat model (GAP-P1-003-SEC).

## User flow

1. Developer opens the Streamlit app in a browser.
2. Developer pastes a Python file or function into the text area.
3. Developer clicks Review.
4. App shows a spinner; backend issues a single Claude call with the structured
   response schema.
5. App renders the parsed response as three sections plus the confidence
   footer. On schema-validation failure, app retries once and otherwise shows
   a user-facing error.

## Acceptance criteria

**Scenario: happy path on seeded buggy file**
*Given* the app is running and the user has pasted the contents of
`examples/buggy.py`
*When* the user clicks Review
*Then* the response renders three sections (Design flaws, Proposed tests,
Refactor), the flaws section contains at least two items each with a category
and a quoted line, the tests section contains at least two pytest functions,
and the refactor section contains exactly one before/after pair.

**Scenario: clean code returns honest "no major flaws"**
*Given* the user has pasted a small, well-formed Python function with no
obvious flaws
*When* the user clicks Review
*Then* the design-flaws section may contain zero to two items, the confidence
footer notes the input looked clean, and the app does not invent flaws to fill
space.

**Scenario: non-Python input**
*Given* the user has pasted JavaScript, prose, or random text
*When* the user clicks Review
*Then* the app returns a single clear message that v1 supports Python only,
referencing the polyglot gap (GAP-P1-002), and does not produce hallucinated
Python review of non-Python text.

**Scenario: Anthropic API error**
*Given* the Anthropic API returns a non-2xx response, times out, or returns
malformed JSON twice
*When* the user clicks Review
*Then* the app shows a user-facing error stating "Review service unavailable —
try again" without leaking a stack trace, and the error path is logged
server-side.

**Scenario: missing API key**
*Given* `ANTHROPIC_API_KEY` is not set in `.env` or environment
*When* the app starts or the user clicks Review
*Then* the app shows a clear setup message naming the env var and pointing at
`.env.example`, and does not crash with a KeyError.

**Scenario: response renders safely**
*Given* the model returns content that includes HTML-like or script-like
substrings
*When* the app renders the response
*Then* the content is rendered as text via `st.write`, not via
`st.markdown(unsafe_allow_html=True)`, and no script executes.

## Non-goals

- Applying any suggested change automatically.
- Running the proposed tests.
- Persisting reviews or history across sessions.
- Authentication or per-user state.

## Success signals

A reviewer trying this for the first time can: paste a file, get a useful
review back in seconds, point at the line a flaw refers to without scrolling
ambiguity, and trust the confidence footer enough to either ship or
investigate further. The output reads like a careful colleague's first pass,
not a list of generic lint warnings. The refactor section recommends one
change and explains why — it does not rewrite the file.
