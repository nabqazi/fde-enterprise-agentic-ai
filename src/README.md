# AI Pair Engineer — src

## What this is

A small Streamlit app that reviews a pasted Python snippet using the Anthropic
Claude API. It returns three structured outputs: design flaws, proposed pytest
cases, and one focused refactor.

## Setup

1. Clone the repo and `cd` into it.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r src/requirements.txt`
4. Copy `src/.env.example` to `src/.env` and set `ANTHROPIC_API_KEY`.

## Run

From the repo root:

```
streamlit run src/app.py
```

## Try the demo

Click **Load example** to populate the editor with `examples/buggy.py`, then
click **Review**.

## See also

- [`../WORKFLOW.md`](../WORKFLOW.md)
- [`../specs/S-001-mvp.md`](../specs/S-001-mvp.md)
