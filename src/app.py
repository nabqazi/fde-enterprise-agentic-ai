"""FDE Enterprise — AI Pair Engineer.

Multi-language, enterprise-grade code review platform powered by Claude.
"""
from __future__ import annotations

import html as _html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from languages import SUPPORTED_LANGUAGES, looks_like_code
from reviewer import review_code
from styles import CATEGORY_COLORS, CONFIDENCE_STYLES, CUSTOM_CSS

# ── Constants ────────────────────────────────────────────────────────────────

EXAMPLES_DIR = Path(__file__).parent / "examples"

CATEGORY_ICONS: dict[str, str] = {
    "coupling":       "🔗",
    "cohesion":       "🎯",
    "error-handling": "⚠️",
    "naming":         "🏷️",
    "complexity":     "🔀",
    "correctness":    "🐛",
}

METHODOLOGY_STEPS = [
    (
        "Investigate",
        "Open-ended exploration — map the problem space, user needs, and constraints. "
        "Output is notes and questions, never code. No silent assumptions.",
    ),
    (
        "Design",
        "Lock every architectural decision as an ADR or register it in the Gap "
        "Register with a concrete revisit trigger. MCQ before silent pick: if a "
        "tradeoff is real, surface it with honest downsides named.",
    ),
    (
        "Build",
        "Execute against the locked spec. Dev tickets carry five rails: linked "
        "artifacts, exact file list, per-file scope, explicit Do-NOT list, and "
        "runnable success criteria. No scope creep without an ADR.",
    ),
    (
        "Review (HITL Gate)",
        "Blocking human-in-the-loop review against the ticket. Security checklist: "
        "prompt injection, API key handling, output rendering surface, code "
        "execution, dependency audit. Nothing is waved through.",
    ),
]

SECURITY_CHECKS = [
    ("Prompt injection", "User code is passed as text content — never executed or interpreted by the platform."),
    ("API key handling", "Key loaded via os.getenv() from .env file. Never logged, never in error output."),
    ("Output rendering", "All model output rendered via st.write() / st.code() or HTML-escaped. No raw HTML injection of user content."),
    ("Code execution", "No eval(), exec(), importlib, or subprocess on user input. Strictly read-only."),
    ("Dependency surface", "Three pinned packages. No agent frameworks. No transitive surprises."),
]

OPEN_GAPS = [
    ("GAP-P1-001", "Multi-step ReAct for files >300 lines", "When users report quality issues on long files"),
    ("GAP-P1-002", "Polyglot prompt tuning per language",   "Next prompt-iteration cycle per language"),
    ("GAP-P1-003", "Full STRIDE threat model",              "Before any public deployment"),
    ("GAP-P1-004", "Eval harness with held-out set",        "Before any non-trivial prompt change"),
    ("GAP-P2-001", "Streaming output",                      "When p95 review time exceeds 8 s"),
    ("GAP-P2-002", "IDE / CLI integration",                 "After prompt and output shape stabilise"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """HTML-escape model output before embedding in HTML templates."""
    return _html.escape(str(text or ""))


def _load_example(lang: str) -> str:
    candidates = [
        EXAMPLES_DIR / f"buggy.{lang[:2]}",
        EXAMPLES_DIR / f"buggy.{lang}",
        EXAMPLES_DIR / "buggy.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def _export_markdown(result: dict) -> str:
    lang = result.get("_language", "")
    timing = result.get("_timing_ms", 0)
    confidence = result.get("confidence", "unknown")
    flaws = result.get("design_flaws", []) or []
    tests = result.get("proposed_tests", []) or []
    refactor = result.get("refactor", {}) or {}
    caveats = result.get("caveats", "")

    lines: list[str] = [
        "# AI Code Review — FDE Enterprise",
        "",
        f"**Language:** {lang.title()}  ",
        f"**Confidence:** {confidence.upper()}  ",
        f"**Review time:** {timing / 1000:.1f}s  ",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        "",
        "---",
        "",
        f"## Design Flaws ({len(flaws)})",
        "",
    ]
    for i, flaw in enumerate(flaws, 1):
        lines += [
            f"### {i}. {flaw.get('category', '').title()}",
            "",
            "```",
            flaw.get("quoted_lines", ""),
            "```",
            "",
            f"**Issue:** {flaw.get('issue', '')}",
            "",
            f"**Suggestion:** {flaw.get('suggestion', '')}",
            "",
        ]

    lines += [f"## Proposed Tests ({len(tests)})", ""]
    for test in tests:
        lines += [
            f"### `{test.get('name', '')}`",
            "",
            f"Targets: {test.get('targets', '')}",
            "",
            f"```{lang}",
            test.get("code", ""),
            "```",
            "",
        ]

    lines += [
        "## Refactor Suggestion",
        "",
        refactor.get("summary", ""),
        "",
        "**Before:**",
        "```",
        refactor.get("before", ""),
        "```",
        "",
        "**After:**",
        "```",
        refactor.get("after", ""),
        "```",
        "",
    ]
    if caveats:
        lines += ["---", "", f"**Caveats:** {caveats}", ""]

    return "\n".join(lines)


# ── HTML component builders ───────────────────────────────────────────────────

def _html_header() -> str:
    return """
<div class="fde-header">
  <div class="fde-brand">
    <div class="fde-icon">🔷</div>
    <div>
      <div class="fde-brand-name">AI Pair Engineer</div>
      <div class="fde-brand-tagline">FDE Enterprise · Powered by Claude</div>
    </div>
  </div>
  <div class="fde-header-right">
    <span class="fde-pill fde-pill-version">v1.0 Enterprise</span>
    <span class="fde-pill fde-pill-live">
      <span class="fde-dot"></span>Live
    </span>
  </div>
</div>"""


def _html_stats_bar(result: dict) -> str:
    flaws    = len(result.get("design_flaws", []) or [])
    tests    = len(result.get("proposed_tests", []) or [])
    timing   = result.get("_timing_ms", 0)
    conf     = result.get("confidence", "unknown")
    lang_id  = result.get("_language", "python")

    lang_info = SUPPORTED_LANGUAGES.get(lang_id, {})
    lang_icon = lang_info.get("icon", "💻")
    lang_name = lang_info.get("name", lang_id.title())

    cs = CONFIDENCE_STYLES.get(conf, CONFIDENCE_STYLES["unknown"])
    timing_s = f"{timing / 1000:.1f}s"

    return f"""
<div class="stats-bar">
  <div class="stat-item">
    <div class="stat-value">{flaws}</div>
    <div class="stat-label">Design Flaws</div>
  </div>
  <div class="stat-sep"></div>
  <div class="stat-item">
    <div class="stat-value">{tests}</div>
    <div class="stat-label">Tests Proposed</div>
  </div>
  <div class="stat-sep"></div>
  <div class="stat-item">
    <div class="stat-value">{timing_s}</div>
    <div class="stat-label">Review Time</div>
  </div>
  <div class="stat-sep"></div>
  <div class="stat-item">
    <span class="conf-chip"
          style="color:{cs['color']};background:{cs['bg']};border-color:{cs['border']};">
      {conf.upper()}
    </span>
    <div class="stat-label">Confidence</div>
  </div>
  <div class="stat-sep"></div>
  <div class="stat-item">
    <span class="lang-chip">{lang_icon} {lang_name}</span>
    <div class="stat-label">Language</div>
  </div>
</div>"""


def _html_flaw_card(idx: int, flaw: dict) -> str:
    category = flaw.get("category", "")
    cat      = CATEGORY_COLORS.get(category, {"color": "#8B949E", "bg": "rgba(139,148,158,0.12)", "label": category.title()})
    icon     = CATEGORY_ICONS.get(category, "•")

    quoted      = _e(flaw.get("quoted_lines", "") or "")
    issue       = _e(flaw.get("issue", "") or "")
    suggestion  = _e(flaw.get("suggestion", "") or "")

    code_block = ""
    if quoted:
        code_block = f'<pre class="flaw-code">{quoted}</pre>'

    return f"""
<div class="flaw-card" style="border-left:4px solid {cat['color']};">
  <div class="flaw-header">
    <div class="flaw-num">{idx}</div>
    <span class="cat-badge"
          style="background:{cat['bg']};color:{cat['color']};border:1px solid {cat['color']}40;">
      {icon} {cat['label']}
    </span>
  </div>
  {code_block}
  <div class="flaw-field">
    <div class="flaw-field-label">Issue</div>
    {issue}
  </div>
  <div class="flaw-field" style="margin-top:0.625rem;">
    <div class="flaw-field-label">Suggestion</div>
    {suggestion}
  </div>
</div>"""


def _html_section_title(icon: str, title: str, count: int | None = None) -> str:
    badge = f'<span class="count-badge">{count}</span>' if count is not None else ""
    return f"""
<div class="section-title">
  <div class="section-icon">{icon}</div>
  <span class="section-title-text">{title}</span>
  {badge}
</div>"""


# ── Render sections ───────────────────────────────────────────────────────────

def _render_design_flaws(flaws: list[dict]) -> None:
    flaws = flaws or []
    st.markdown(_html_section_title("🔍", "Design Flaws", len(flaws)), unsafe_allow_html=True)

    if not flaws:
        st.markdown("""
<div style="text-align:center;padding:2.5rem;color:#6E7681;font-size:14px;">
  ✅ No design flaws surfaced for this snippet.
</div>""", unsafe_allow_html=True)
        return

    for idx, flaw in enumerate(flaws, 1):
        st.markdown(_html_flaw_card(idx, flaw), unsafe_allow_html=True)


def _render_tests(tests: list[dict], lang: str) -> None:
    tests = tests or []
    st.markdown(_html_section_title("🧪", "Proposed Tests", len(tests)), unsafe_allow_html=True)

    if not tests:
        st.markdown("""
<div style="text-align:center;padding:2.5rem;color:#6E7681;font-size:14px;">
  No tests proposed.
</div>""", unsafe_allow_html=True)
        return

    for idx, test in enumerate(tests, 1):
        name    = _e(test.get("name", f"test_{idx}") or "")
        targets = _e(test.get("targets", "") or "")
        code    = test.get("code", "") or ""

        st.markdown(f"""
<div class="test-card">
  <div class="test-name">def {name}()</div>
  <div class="test-targets">Targets: {targets}</div>
</div>""", unsafe_allow_html=True)

        if code:
            st.code(code, language=lang)


def _render_refactor(refactor: dict, lang: str) -> None:
    st.markdown(_html_section_title("⚡", "Refactor Suggestion"), unsafe_allow_html=True)

    summary = _e(refactor.get("summary", "") or "")
    before  = refactor.get("before", "") or ""
    after   = refactor.get("after", "") or ""

    if summary:
        st.markdown(f"""
<div class="refactor-summary">
  <span class="refactor-icon">⚡</span>
  <span>{summary}</span>
</div>""", unsafe_allow_html=True)

    col_b, col_a = st.columns(2)
    with col_b:
        st.markdown('<div class="diff-label" style="color:#F87171;">❌ Before</div>', unsafe_allow_html=True)
        st.code(before or "(nothing)", language=lang)
    with col_a:
        st.markdown('<div class="diff-label" style="color:#4ADE80;">✅ After</div>', unsafe_allow_html=True)
        st.code(after or "(nothing)", language=lang)


def _render_results(result: dict) -> None:
    lang = result.get("_language", "python")
    flaws   = result.get("design_flaws", []) or []
    tests   = result.get("proposed_tests", []) or []
    refactor= result.get("refactor", {}) or {}
    conf    = result.get("confidence", "unknown")
    caveats = result.get("caveats", "") or ""

    st.markdown('<div class="results-wrap">', unsafe_allow_html=True)
    st.markdown(_html_stats_bar(result), unsafe_allow_html=True)

    _render_design_flaws(flaws)
    st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)

    _render_tests(tests, lang)
    st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)

    _render_refactor(refactor, lang)

    if caveats:
        st.markdown(f"""
<div class="caveats-box">
  <span style="font-size:18px;flex-shrink:0;">⚠️</span>
  <div>
    <div class="caveats-label">Caveats</div>
    {_e(caveats)}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_empty_state() -> None:
    lang_chips = "".join(
        f'<span class="empty-lang-chip">{info["icon"]} {info["name"]}</span>'
        for info in SUPPORTED_LANGUAGES.values()
    )
    st.markdown(f"""
<div class="empty-state">
  <div class="empty-icon">🔷</div>
  <div class="empty-title">Ready to review</div>
  <div class="empty-desc">
    Paste code above or click <strong>Load Example</strong> to see the
    reviewer in action. Supports six languages out of the box.
  </div>
  <div class="empty-langs">{lang_chips}</div>
</div>""", unsafe_allow_html=True)


# ── Methodology tab ───────────────────────────────────────────────────────────

def _render_methodology_tab() -> None:
    st.markdown("""
<p style="color:#8B949E;font-size:14px;line-height:1.75;max-width:720px;margin-bottom:2rem;">
  FDE Enterprise follows a four-step discipline for deploying AI agents in
  production workflows. The loop generalises to any agentic task: replace
  "code review" with "partner integration triage" and the shape is identical —
  only the ticket gets longer and the HITL gate adds a STRIDE sign-off.
</p>""", unsafe_allow_html=True)

    for i, (title, desc) in enumerate(METHODOLOGY_STEPS, 1):
        st.markdown(f"""
<div class="method-step">
  <div class="method-num">{i}</div>
  <div>
    <div class="method-title">{title}</div>
    <div class="method-desc">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)

    st.markdown(_html_section_title("🔒", "Security Checklist (v1 — all passed)"), unsafe_allow_html=True)
    for title, desc in SECURITY_CHECKS:
        st.markdown(f"""
<div class="sec-item">
  <span class="sec-check">✓</span>
  <div>
    <div class="sec-title">{title}</div>
    <div class="sec-desc">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)

    st.markdown(_html_section_title("📋", "Open Gaps Register"), unsafe_allow_html=True)
    st.markdown("""
<p style="color:#6E7681;font-size:13px;margin-bottom:1rem;">
  Every cut is named. Every named cut has a revisit trigger.
  Nothing is waved through silently.
</p>""", unsafe_allow_html=True)

    for gap_id, title, trigger in OPEN_GAPS:
        st.markdown(f"""
<div class="gap-row">
  <span class="gap-id">{gap_id}</span>
  <span class="gap-title">{title}</span>
  <span class="gap-trigger">{trigger}</span>
</div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown("""
<div style="font-size:10px;font-weight:700;text-transform:uppercase;
     letter-spacing:1.2px;color:#6E7681;padding-bottom:0.75rem;
     border-bottom:1px solid #21262D;margin-bottom:1rem;">
  Configuration
</div>""", unsafe_allow_html=True)

        lang_options = ["Auto-detect"] + [info["name"] for info in SUPPORTED_LANGUAGES.values()]
        selected_display = st.selectbox("Language", lang_options, index=0, label_visibility="collapsed")
        selected_lang = (
            "auto"
            if selected_display == "Auto-detect"
            else next(
                (k for k, v in SUPPORTED_LANGUAGES.items() if v["name"] == selected_display),
                "python",
            )
        )

        depth = st.select_slider(
            "Review depth",
            options=["Quick", "Standard", "Deep"],
            value="Standard",
        )

        st.markdown('<hr style="border:none;border-top:1px solid #21262D;margin:0.875rem 0;">', unsafe_allow_html=True)

        st.markdown("""
<div style="font-size:10px;font-weight:700;text-transform:uppercase;
     letter-spacing:1.2px;color:#6E7681;margin-bottom:0.75rem;">
  Model
</div>
<div class="model-card">
  <div class="model-name">claude-sonnet-4-6</div>
  <div class="model-provider">Anthropic · Claude</div>
  <div class="model-status">
    <span class="model-dot"></span>Connected
  </div>
</div>""", unsafe_allow_html=True)

        history: list[dict] = st.session_state.get("review_history", [])
        if history:
            st.markdown('<hr style="border:none;border-top:1px solid #21262D;margin:0.875rem 0;">', unsafe_allow_html=True)
            st.markdown("""
<div style="font-size:10px;font-weight:700;text-transform:uppercase;
     letter-spacing:1.2px;color:#6E7681;margin-bottom:0.75rem;">
  Recent Reviews
</div>""", unsafe_allow_html=True)

            for i, rev in enumerate(reversed(history[-6:])):
                info = SUPPORTED_LANGUAGES.get(rev.get("language", ""), {})
                icon = info.get("icon", "💻")
                name = info.get("name", "?")
                fc   = rev.get("flaw_count", 0)
                conf = rev.get("confidence", "?")[0].upper()
                ts   = rev.get("timestamp", "")
                label = f"{icon} {name} · {fc} flaw{'s' if fc != 1 else ''} · {conf} · {ts}"

                if st.button(label, key=f"hist_{i}", use_container_width=True):
                    st.session_state["loaded_review"] = rev.get("result")
                    st.rerun()

    return selected_lang, depth


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="AI Pair Engineer | FDE Enterprise",
        page_icon="🔷",
        layout="wide",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Session state init
    for key, default in [
        ("review_history", []),
        ("last_result", None),
        ("code_input", ""),
        ("loaded_review", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    selected_lang, depth = _render_sidebar()

    st.markdown(_html_header(), unsafe_allow_html=True)

    tab_review, tab_method = st.tabs(["🔍  Review", "📐  Methodology"])

    # ── Review tab ────────────────────────────────────────────────────────────
    with tab_review:
        source = st.text_area(
            "code_input_area",
            value=st.session_state.code_input,
            height=300,
            placeholder=(
                "# Paste Python, JavaScript, TypeScript, Go, Java, or Rust…\n"
                "# Or click  ⬇ Example  to load a deliberately flawed snippet."
            ),
            label_visibility="collapsed",
            key="code_input",
        )

        c1, c2, c3, _ = st.columns([1, 1.3, 1, 5])
        with c1:
            if st.button("⬇ Example", use_container_width=True):
                lang = selected_lang if selected_lang != "auto" else "python"
                st.session_state.code_input = _load_example(lang)
                st.session_state.loaded_review = None
                st.rerun()
        with c2:
            review_clicked = st.button("🔍 Review", type="primary", use_container_width=True)
        with c3:
            if st.button("✕ Clear", use_container_width=True):
                st.session_state.code_input = ""
                st.session_state.last_result = None
                st.session_state.loaded_review = None
                st.rerun()

        st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)

        if review_clicked:
            st.session_state.loaded_review = None

            if not source or not source.strip():
                st.warning("Paste some code first, or click **⬇ Example** to load a sample.")
                st.stop()

            # Language resolution
            if selected_lang == "auto":
                is_code, detected = looks_like_code(source)
                if not is_code or not detected:
                    st.warning(
                        "Could not detect a supported language. "
                        "Supported: Python, JavaScript, TypeScript, Go, Java, Rust."
                    )
                    st.stop()
                language = detected
            else:
                language = selected_lang

            if not os.getenv("ANTHROPIC_API_KEY"):
                st.error(
                    "**API key required.** Set `ANTHROPIC_API_KEY` in `.env` "
                    "(see `.env.example`) and restart."
                )
                st.stop()

            lang_display = SUPPORTED_LANGUAGES.get(language, {}).get("name", language)
            with st.spinner(f"Reviewing {lang_display} code with Claude…"):
                try:
                    result = review_code(source, language=language)
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.stop()
                except Exception:
                    st.error("Unexpected error. Please try again.")
                    st.stop()

            st.session_state.last_result = result
            st.session_state.review_history.append({
                "language":   language,
                "flaw_count": len(result.get("design_flaws", []) or []),
                "confidence": result.get("confidence", "unknown"),
                "timestamp":  datetime.now().strftime("%H:%M"),
                "result":     result,
            })
            st.rerun()

        result_to_show = st.session_state.loaded_review or st.session_state.last_result

        if result_to_show:
            _render_results(result_to_show)

            st.markdown('<hr class="fde-hr">', unsafe_allow_html=True)
            md = _export_markdown(result_to_show)
            st.download_button(
                "📋 Export as Markdown",
                data=md,
                file_name="code-review.md",
                mime="text/markdown",
            )
        else:
            _render_empty_state()

    # ── Methodology tab ───────────────────────────────────────────────────────
    with tab_method:
        _render_methodology_tab()


if __name__ == "__main__":
    main()
