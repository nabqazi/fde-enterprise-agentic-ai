"""Anthropic-backed code reviewer.

Single entry point: `review_code(source)` returns a dict matching the
`submit_review` tool schema. The function makes exactly one Messages API
call and forces the model to respond via the tool, so the result is
already structured JSON — no prose parsing.
"""

from __future__ import annotations

import os
from typing import Any

import anthropic

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is optional at runtime
    load_dotenv = None  # type: ignore[assignment]

from prompts import SYSTEM_PROMPT

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048

REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "design_flaws": {
            "type": "array",
            "minItems": 0,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "coupling",
                            "cohesion",
                            "error-handling",
                            "naming",
                            "complexity",
                            "correctness",
                        ],
                    },
                    "quoted_lines": {
                        "type": "string",
                        "description": (
                            "The offending lines copied verbatim from the "
                            "input. Preserve whitespace."
                        ),
                    },
                    "issue": {
                        "type": "string",
                        "description": "1-2 sentences naming the concrete problem.",
                    },
                    "suggestion": {
                        "type": "string",
                        "description": "1-2 sentences on how to resolve it.",
                    },
                },
                "required": ["category", "quoted_lines", "issue", "suggestion"],
            },
        },
        "proposed_tests": {
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "targets": {
                        "type": "string",
                        "description": "Which flaw or behavior this test exercises.",
                    },
                    "code": {
                        "type": "string",
                        "description": "Self-contained pytest function body.",
                    },
                },
                "required": ["name", "targets", "code"],
            },
        },
        "refactor": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "One sentence: what changes and why.",
                },
                "before": {
                    "type": "string",
                    "description": "Small verbatim excerpt from the input.",
                },
                "after": {
                    "type": "string",
                    "description": "The refactored snippet. Small and focused.",
                },
            },
            "required": ["summary", "before", "after"],
        },
        "confidence": {
            "type": "string",
            "enum": ["low", "medium", "high"],
        },
        "caveats": {
            "type": "string",
            "description": "What the reviewer might be wrong about.",
        },
    },
    "required": [
        "design_flaws",
        "proposed_tests",
        "refactor",
        "confidence",
        "caveats",
    ],
}

_TOOL_DEFINITION: dict[str, Any] = {
    "name": "submit_review",
    "description": (
        "Submit the structured code review. Call this exactly once with all "
        "fields populated. This is the only acceptable response channel."
    ),
    "input_schema": REVIEW_SCHEMA,
}


def looks_like_python(source: str) -> bool:
    """Loose heuristic: does this look like Python source?

    The check is intentionally permissive — false positives are cheaper
    than false negatives, since the model itself will push back on
    obviously-not-Python input. We only reject if there are no Python-ish
    markers at all.
    """
    if not source or not source.strip():
        return False
    text = source
    python_markers = (
        "def ",
        "class ",
        "import ",
        "from ",
        "print(",
        "if __name__",
        "lambda ",
        "async def",
    )
    return any(marker in text for marker in python_markers)


def review_code(source: str) -> dict[str, Any]:
    """Run a single Claude review pass and return the structured result.

    Args:
        source: Python source code to review.

    Returns:
        Dict matching the `submit_review` tool schema (design_flaws,
        proposed_tests, refactor, confidence, caveats).

    Raises:
        RuntimeError: if the API key is missing or the API call fails.
            The error message is sanitized — no SDK internals leak.
    """
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:  # pragma: no cover - defensive
            pass

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)

    user_message = (
        "Review the following Python code. Respond only via the "
        "`submit_review` tool.\n\n"
        "```python\n"
        f"{source}\n"
        "```"
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=[_TOOL_DEFINITION],
            tool_choice={"type": "tool", "name": "submit_review"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        print(f"[reviewer] Anthropic API call failed: {exc!r}", flush=True)
        raise RuntimeError(
            "The review service is unavailable right now. "
            "Check your network and API key, then try again."
        ) from None

    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "submit_review":
            payload = block.input
            if isinstance(payload, dict):
                return payload
            break

    print(
        "[reviewer] Model did not return a submit_review tool_use block.",
        flush=True,
    )
    raise RuntimeError(
        "The reviewer returned an unexpected response shape. Try again."
    )
