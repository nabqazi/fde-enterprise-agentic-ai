"""Language detection and metadata for the FDE AI Pair Engineer platform."""
from __future__ import annotations

SUPPORTED_LANGUAGES: dict[str, dict] = {
    "python": {
        "name": "Python",
        "icon": "🐍",
        "test_framework": "pytest",
        "markers": (
            "def ", "class ", "import ", "from ", "print(",
            "if __name__", "lambda ", "async def", "elif ", "except ", "try:",
            "with ", "yield ", "raise ",
        ),
    },
    "javascript": {
        "name": "JavaScript",
        "icon": "🟨",
        "test_framework": "Jest",
        "markers": (
            "function ", "const ", "let ", "var ", "console.log",
            "require(", "module.exports", "=> {", "async function",
            ".then(", ".catch(", "Promise.",
        ),
    },
    "typescript": {
        "name": "TypeScript",
        "icon": "🔷",
        "test_framework": "Jest",
        "markers": (
            "interface ", ": string", ": number", ": boolean",
            "readonly ", ": void", "as ", "type ", "enum ",
            ": Promise<", ": Array<", "?: ",
        ),
    },
    "go": {
        "name": "Go",
        "icon": "🐹",
        "test_framework": "testing",
        "markers": (
            "func ", "package ", "fmt.", ":=", "go func",
            "struct {", "import (", "chan ", "defer ", "select {",
        ),
    },
    "java": {
        "name": "Java",
        "icon": "☕",
        "test_framework": "JUnit",
        "markers": (
            "public class", "private ", "void ", "System.out.",
            "@Override", "import java", "throws ", "extends ",
            "implements ", "new ArrayList", "new HashMap",
        ),
    },
    "rust": {
        "name": "Rust",
        "icon": "🦀",
        "test_framework": "cargo test",
        "markers": (
            "fn ", "let mut", "impl ", "pub ", "match ",
            "Ok(", "Err(", "unwrap()", "use std::", "-> Result",
        ),
    },
}


def detect_language(source: str) -> str | None:
    """Return the most likely language id, or None if unrecognised."""
    if not source or not source.strip():
        return None

    scores: dict[str, int] = {}
    for lang_id, info in SUPPORTED_LANGUAGES.items():
        score = sum(1 for m in info["markers"] if m in source)
        if score > 0:
            scores[lang_id] = score

    if not scores:
        return None

    # TypeScript is a JS superset — prefer TS when its markers appear
    if "typescript" in scores and "javascript" in scores:
        if scores["typescript"] >= 2:
            del scores["javascript"]

    return max(scores, key=lambda k: scores[k])


def looks_like_code(source: str) -> tuple[bool, str | None]:
    """Return (is_recognised_code, language_id)."""
    lang = detect_language(source)
    return (lang is not None, lang)
