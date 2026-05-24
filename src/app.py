"""Streamlit UI for AI Pair Engineer.

Single-page app: paste Python, click Review, see structured feedback.
No code from the user is ever executed.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from reviewer import looks_like_python, review_code

EXAMPLE_PATH = Path(__file__).parent / "examples" / "buggy.py"

CATEGORY_LABEL = {
    "coupling": "Coupling",
    "cohesion": "Cohesion",
    "error-handling": "Error handling",
    "naming": "Naming",
    "complexity": "Complexity",
    "correctness": "Correctness",
}


def _load_example() -> str:
    try:
        return EXAMPLE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[app] Could not read example file: {exc!r}", flush=True)
        return ""


def _render_design_flaws(flaws: list[dict]) -> None:
    if not flaws:
        st.write("No design flaws surfaced. See caveats below.")
        return
    for idx, flaw in enumerate(flaws, start=1):
        category = flaw.get("category", "")
        label = CATEGORY_LABEL.get(category, category or "Issue")
        st.markdown(f"**{idx}. {label}**")
        quoted = flaw.get("quoted_lines", "")
        if quoted:
            st.code(quoted, language="python")
        issue = flaw.get("issue", "")
        suggestion = flaw.get("suggestion", "")
        if issue:
            st.write(f"**Issue.** {issue}")
        if suggestion:
            st.write(f"**Suggestion.** {suggestion}")


def _render_tests(tests: list[dict]) -> None:
    if not tests:
        st.write("No tests proposed.")
        return
    for idx, test in enumerate(tests, start=1):
        name = test.get("name", f"test_{idx}")
        targets = test.get("targets", "")
        st.markdown(f"**{idx}. `{name}`** — targets: {targets}")
        code = test.get("code", "")
        if code:
            st.code(code, language="python")


def _render_refactor(refactor: dict) -> None:
    summary = refactor.get("summary", "")
    if summary:
        st.write(summary)
    before = refactor.get("before", "")
    after = refactor.get("after", "")
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**Before**")
        st.code(before or "", language="python")
    with col_after:
        st.markdown("**After**")
        st.code(after or "", language="python")


def main() -> None:
    st.set_page_config(page_title="AI Pair Engineer", layout="wide")

    st.title("AI Pair Engineer")
    st.write(
        "Paste a Python function or file and get a senior-engineer-style code "
        "review back: design flaws, proposed pytest cases, and one focused "
        "refactor."
    )
    st.write("Python-only in v1. Other languages are skipped client-side.")

    if "code_input" not in st.session_state:
        st.session_state["code_input"] = ""

    if st.button("Load example"):
        st.session_state["code_input"] = _load_example()

    source = st.text_area(
        "Paste a Python function or file",
        value=st.session_state["code_input"],
        height=360,
        key="code_input",
    )

    review_clicked = st.button("Review", type="primary")

    if not review_clicked:
        return

    if not source or not source.strip():
        st.warning("Paste some Python code first, or click Load example.")
        return

    if not looks_like_python(source):
        st.warning(
            "This does not look like Python. The AI Pair Engineer reviews "
            "Python only in v1, so the review was skipped."
        )
        return

    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error(
            "Set ANTHROPIC_API_KEY in a .env file (see .env.example) and "
            "restart."
        )
        return

    with st.spinner("Reviewing..."):
        try:
            result = review_code(source)
        except RuntimeError as exc:
            message = str(exc)
            if "ANTHROPIC_API_KEY" in message:
                st.error(
                    "Set ANTHROPIC_API_KEY in a .env file (see .env.example) "
                    "and restart."
                )
            else:
                st.error(message)
            return
        except Exception as exc:  # pragma: no cover - defensive catch-all
            print(f"[app] Unexpected error during review: {exc!r}", flush=True)
            st.error(
                "Something went wrong while running the review. Please try "
                "again."
            )
            return

    with st.expander("Design flaws", expanded=True):
        _render_design_flaws(result.get("design_flaws", []) or [])

    with st.expander("Proposed tests", expanded=True):
        _render_tests(result.get("proposed_tests", []) or [])

    with st.expander("Refactor suggestion", expanded=True):
        _render_refactor(result.get("refactor", {}) or {})

    confidence = result.get("confidence", "unknown")
    caveats = result.get("caveats", "")
    st.info(f"Confidence: {confidence}. Caveats: {caveats}")


if __name__ == "__main__":
    main()
