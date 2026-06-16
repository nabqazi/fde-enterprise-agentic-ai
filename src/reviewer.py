"""Anthropic-backed code reviewer.

Single entry point: `review_code(source, language)` returns a dict matching
the `submit_review` tool schema, augmented with `_timing_ms` and `_language`
metadata keys. The function makes exactly one Messages API call and forces
the model to respond via the tool, so the result is already structured JSON.
"""
from __future__ import annotations

import os
import time
from typing import Any

import anthropic

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment]

from languages import SUPPORTED_LANGUAGES, detect_language
from prompts import build_system_prompt

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
                        "description": "Self-contained test function body.",
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
    """Backwards-compatible heuristic for Python detection."""
    lang = detect_language(source)
    return lang == "python"


def review_code(source: str, language: str = "python") -> dict[str, Any]:
    """Run a single Claude review pass and return the structured result.

    Args:
        source:   Source code to review.
        language: Language id from SUPPORTED_LANGUAGES (default: python).

    Returns:
        Dict matching the `submit_review` schema plus `_timing_ms` and
        `_language` metadata keys.

    Raises:
        RuntimeError: if the API key is missing or the API call fails.
    """
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:
            pass

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    lang_info = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["python"])
    lang_name = lang_info["name"]
    test_framework = lang_info["test_framework"]
    system_prompt = build_system_prompt(language=lang_name, test_framework=test_framework)

    user_message = (
        f"Review the following {lang_name} code. "
        "Respond only via the `submit_review` tool.\n\n"
        f"```{language}\n"
        f"{source}\n"
        "```"
    )

    client = anthropic.Anthropic(api_key=api_key)

    t0 = time.perf_counter()
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=[_TOOL_DEFINITION],
            tool_choice={"type": "tool", "name": "submit_review"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        print(f"[reviewer] Anthropic API call failed: {exc!r}", flush=True)
        raise RuntimeError(
            "The review service is unavailable. "
            "Check your network and API key, then try again."
        ) from None
    timing_ms = int((time.perf_counter() - t0) * 1000)

    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "submit_review":
            payload = block.input
            if isinstance(payload, dict):
                payload["_language"] = language
                payload["_timing_ms"] = timing_ms
                payload["_input_chars"] = len(source)
                return payload
            break

    print(
        "[reviewer] Model did not return a submit_review tool_use block.",
        flush=True,
    )
    raise RuntimeError("The reviewer returned an unexpected response. Try again.")
