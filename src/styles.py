"""Visual constants and CSS for the FDE AI Pair Engineer platform."""

CATEGORY_COLORS: dict[str, dict[str, str]] = {
    "coupling":       {"color": "#F97316", "bg": "rgba(249,115,22,0.12)",  "label": "Coupling"},
    "cohesion":       {"color": "#3B82F6", "bg": "rgba(59,130,246,0.12)",  "label": "Cohesion"},
    "error-handling": {"color": "#EF4444", "bg": "rgba(239,68,68,0.12)",   "label": "Error Handling"},
    "naming":         {"color": "#EAB308", "bg": "rgba(234,179,8,0.12)",   "label": "Naming"},
    "complexity":     {"color": "#A855F7", "bg": "rgba(168,85,247,0.12)",  "label": "Complexity"},
    "correctness":    {"color": "#22C55E", "bg": "rgba(34,197,94,0.12)",   "label": "Correctness"},
}

CONFIDENCE_STYLES: dict[str, dict[str, str]] = {
    "high":   {"color": "#4ADE80", "bg": "rgba(34,197,94,0.15)",   "border": "rgba(34,197,94,0.35)"},
    "medium": {"color": "#FBBF24", "bg": "rgba(234,179,8,0.15)",   "border": "rgba(234,179,8,0.35)"},
    "low":    {"color": "#F87171", "bg": "rgba(239,68,68,0.15)",   "border": "rgba(239,68,68,0.35)"},
    "unknown":{"color": "#8B949E", "bg": "rgba(139,148,158,0.15)", "border": "rgba(139,148,158,0.35)"},
}

CUSTOM_CSS = """
<style>
/* ═══════════════════════════════════════════
   FDE Enterprise — AI Pair Engineer
   Design System v1.0
   ═══════════════════════════════════════════ */

/* ── Layout ── */
.stApp { background-color: #0D1117; }

.main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 5rem;
    max-width: 1340px;
}

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #010409 !important;
    border-right: 1px solid #21262D !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
[data-testid="stSidebar"] .stButton button {
    background: #161B22 !important;
    border: 1px solid #21262D !important;
    color: #8B949E !important;
    font-size: 12px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: background 0.15s, color 0.15s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1C2128 !important;
    color: #C9D1D9 !important;
    border-color: #30363D !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: 1px solid #21262D;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border-radius: 0 !important;
    color: #8B949E;
    padding: 0.7rem 1.25rem;
    font-size: 13.5px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    color: #E6EDF3 !important;
    border-bottom: 2px solid #7C3AED !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ── Buttons ── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.5rem !important;
    border-radius: 6px !important;
    transition: opacity 0.15s, transform 0.1s !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.35) !important;
}
.stButton button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton button[kind="secondary"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #C9D1D9 !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    transition: background 0.15s, border-color 0.15s !important;
}
.stButton button[kind="secondary"]:hover {
    background-color: #1C2128 !important;
    border-color: #444C57 !important;
}

/* ── Text area (code input) ── */
.stTextArea textarea {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace !important;
    font-size: 13px !important;
    line-height: 1.65 !important;
    caret-color: #7C3AED;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextArea textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #444C57 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #161B22 !important;
    border-color: #30363D !important;
    color: #E6EDF3 !important;
}

/* ── Slider ── */
.stSlider { color: #7C3AED; }

/* ── Code blocks ── */
.stCode { border-radius: 8px !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #161B22 !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-weight: 600 !important;
}

/* ── Download button ── */
.stDownloadButton button {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #C9D1D9 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ═══════════════════════════════════════════
   Custom Components
   ═══════════════════════════════════════════ */

/* ── Header ── */
.fde-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.5rem;
    border-bottom: 1px solid #21262D;
    margin-bottom: 1.5rem;
}
.fde-brand {
    display: flex;
    align-items: center;
    gap: 0.875rem;
}
.fde-icon {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #7C3AED 0%, #06B6D4 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
    box-shadow: 0 0 24px rgba(124,58,237,0.45);
}
.fde-brand-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #E6EDF3;
    line-height: 1;
    letter-spacing: -0.4px;
    margin: 0;
}
.fde-brand-tagline {
    font-size: 0.68rem;
    color: #6E7681;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}
.fde-header-right { display: flex; gap: 0.5rem; align-items: center; }

.fde-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.fde-pill-version {
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.3);
    color: #A78BFA;
}
.fde-pill-live {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    color: #4ADE80;
}
.fde-dot {
    width: 6px;
    height: 6px;
    background: #4ADE80;
    border-radius: 50%;
    animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.35; }
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 1.25rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    animation: statsIn 0.4s cubic-bezier(0.16,1,0.3,1);
}
@keyframes statsIn {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1;
}
.stat-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #E6EDF3;
    line-height: 1;
    letter-spacing: -1.5px;
}
.stat-label {
    font-size: 0.62rem;
    color: #6E7681;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    white-space: nowrap;
}
.stat-sep {
    width: 1px;
    height: 52px;
    background: #21262D;
    flex-shrink: 0;
}
.conf-chip {
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 1px solid;
}
.lang-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.25);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    color: #22D3EE;
}

/* ── Section title ── */
.section-title {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #21262D;
}
.section-icon {
    width: 30px;
    height: 30px;
    border-radius: 7px;
    background: #1C2128;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}
.section-title-text {
    font-size: 15px;
    font-weight: 600;
    color: #E6EDF3;
}
.count-badge {
    background: #21262D;
    border-radius: 20px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 700;
    color: #8B949E;
    margin-left: 6px;
}

/* ── Flaw card ── */
.flaw-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.875rem;
    transition: border-color 0.15s, box-shadow 0.15s;
    animation: cardIn 0.35s cubic-bezier(0.16,1,0.3,1) both;
}
.flaw-card:hover {
    border-color: #30363D;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.flaw-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.875rem;
}
.flaw-num {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: #21262D;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
    color: #8B949E;
    flex-shrink: 0;
}
.cat-badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    white-space: nowrap;
}
.flaw-code {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 6px;
    padding: 0.875rem 1rem;
    font-size: 12.5px;
    font-family: 'JetBrains Mono','Fira Code','Cascadia Code',monospace;
    color: #E6EDF3;
    margin: 0.75rem 0;
    overflow-x: auto;
    line-height: 1.55;
    white-space: pre;
}
.flaw-field { margin-top: 0.625rem; font-size: 13.5px; color: #C9D1D9; line-height: 1.6; }
.flaw-field-label {
    font-size: 9.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    color: #6E7681;
    margin-bottom: 3px;
}

/* ── Test card ── */
.test-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-left: 4px solid #7C3AED;
    border-radius: 10px;
    padding: 1rem 1.25rem 0.75rem;
    margin-bottom: 0.875rem;
    animation: cardIn 0.35s cubic-bezier(0.16,1,0.3,1) both;
}
.test-name {
    font-family: 'JetBrains Mono',monospace;
    font-size: 13px;
    color: #A78BFA;
    font-weight: 600;
    margin-bottom: 4px;
}
.test-targets { font-size: 12px; color: #6E7681; margin-bottom: 0.75rem; }

/* ── Refactor ── */
.refactor-summary {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.22);
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    font-size: 14px;
    color: #C9D1D9;
    margin-bottom: 1.125rem;
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    animation: cardIn 0.35s cubic-bezier(0.16,1,0.3,1) both;
}
.refactor-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }
.diff-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 6px;
}

/* ── Caveats ── */
.caveats-box {
    background: rgba(139,148,158,0.05);
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    font-size: 13px;
    color: #8B949E;
    margin-top: 1.75rem;
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    line-height: 1.6;
    animation: cardIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.caveats-label {
    font-size: 9.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    color: #6E7681;
    margin-bottom: 4px;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem 4rem;
    color: #6E7681;
}
.empty-icon { font-size: 3.5rem; opacity: 0.5; margin-bottom: 1.25rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: #8B949E; margin-bottom: 0.5rem; }
.empty-desc {
    font-size: 0.875rem;
    color: #6E7681;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.7;
}
.empty-langs {
    margin-top: 1.5rem;
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
}
.empty-lang-chip {
    padding: 4px 12px;
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 20px;
    font-size: 12px;
    color: #6E7681;
}

/* ── Methodology ── */
.method-step {
    display: flex;
    gap: 1rem;
    padding: 1.25rem;
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s;
}
.method-step:hover { border-color: #30363D; }
.method-num {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C3AED, #06B6D4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 0 14px rgba(124,58,237,0.35);
}
.method-title { font-size: 14px; font-weight: 600; color: #E6EDF3; margin: 0 0 4px; }
.method-desc  { font-size: 13px; color: #8B949E; margin: 0; line-height: 1.55; }

/* ── Security checklist ── */
.sec-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 8px;
    margin-bottom: 0.5rem;
}
.sec-check { color: #4ADE80; font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.sec-title { font-size: 13px; font-weight: 600; color: #C9D1D9; }
.sec-desc  { font-size: 12px; color: #6E7681; margin-top: 2px; line-height: 1.4; }

/* ── GAP register ── */
.gap-row {
    display: flex;
    align-items: baseline;
    gap: 0.875rem;
    padding: 0.75rem 1rem;
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    font-size: 13px;
}
.gap-id {
    font-family: monospace;
    font-size: 11px;
    font-weight: 700;
    color: #FBBF24;
    background: rgba(234,179,8,0.1);
    border: 1px solid rgba(234,179,8,0.2);
    border-radius: 4px;
    padding: 2px 7px;
    white-space: nowrap;
    flex-shrink: 0;
}
.gap-title { color: #C9D1D9; font-weight: 500; }
.gap-trigger { color: #6E7681; font-size: 12px; flex: 1; text-align: right; }

/* ── Sidebar model card ── */
.model-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 0.875rem 1rem;
    margin-top: 0.375rem;
}
.model-name     { font-size: 12px; font-weight: 600; color: #E6EDF3; font-family: monospace; }
.model-provider { font-size: 11px; color: #6E7681; margin-top: 2px; }
.model-status   {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    color: #4ADE80;
    margin-top: 6px;
}
.model-dot {
    width: 5px;
    height: 5px;
    background: #4ADE80;
    border-radius: 50%;
    animation: livePulse 2s ease-in-out infinite;
}

/* ── Divider ── */
hr.fde-hr {
    border: none;
    border-top: 1px solid #21262D;
    margin: 1.75rem 0;
}

/* ── Results wrapper ── */
.results-wrap {
    animation: resultsIn 0.5s cubic-bezier(0.16,1,0.3,1);
}
@keyframes resultsIn {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
"""
