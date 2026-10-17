"""TokenLab - LLM Prompt Optimization & Evaluation (Streamlit UI).   Run:  streamlit run app.py

Light theme note: colours below are applied with CSS. For a fully consistent light theme on every
native widget, also set `[theme] base = "light"` in .streamlit/config.toml (optional).
"""
from __future__ import annotations

import difflib
import html
import os
import re

import altair as alt
import pandas as pd
import streamlit as st

import cost_calculator as cc
import pipeline as pl
from llm_provider import PROVIDER_NAMES, ProviderError, get_provider
from sample_prompts import SAMPLES
from token_counter import word_count

st.set_page_config(page_title="TokenLab | Prompt Optimization", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg: #F8FAFC;
  --surface: #FFFFFF;
  --surface-soft: #F1F5F9;
  --text: #0F172A;
  --muted: #64748B;
  --accent: #2563EB;
  --accent-hover: #1D4ED8;
  --border: #E2E8F0;
  --ok: #15803D;
  --warn: #B45309;
}
html, body, .stApp {
  background: var(--bg);
  color: var(--text);
  color-scheme: light;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  color: var(--text);
}
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p { color: var(--muted); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div { padding-top: 1.4rem; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1380px; }

textarea {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  font-size: .84rem !important;
  line-height: 1.65 !important;
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
}
textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent) !important;
}
textarea:disabled {
  -webkit-text-fill-color: var(--text) !important;
  opacity: 1 !important;
  background: var(--surface-soft) !important;
}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div {
  background: var(--surface) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
  border-color: var(--border) !important;
}
input { color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; }

/* Keep every editable form control white, including controls rendered by
   BaseWeb/Streamlit in the sidebar, expanders, and conditional settings. */
.stApp [data-testid="stTextInput"] [data-baseweb],
.stApp [data-testid="stNumberInput"] [data-baseweb],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stDateInput"] [data-baseweb],
.stApp [data-testid="stTimeInput"] [data-baseweb],
.stApp [data-testid="stTextArea"] textarea,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
.stApp [data-testid="stNumberInput"] button,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stNumberInput"] input {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
  border-color: #CBD5E1 !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] div,
.stApp [data-testid="stTextInput"] input::placeholder,
.stApp [data-testid="stNumberInput"] input::placeholder,
.stApp textarea::placeholder {
  color: #64748B !important;
  -webkit-text-fill-color: #64748B !important;
}
.stApp [data-testid="stCheckbox"] label,
.stApp [data-testid="stRadio"] label {
  color: #0F172A !important;
}
.stApp [data-testid="stCheckbox"] input,
.stApp [data-testid="stRadio"] input {
  accent-color: #2563EB;
}
.stApp [data-testid="stExpander"] details,
.stApp [data-testid="stExpander"] summary {
  background-color: #FFFFFF !important;
}

/* Explicitly normalize Streamlit/BaseWeb controls: some browser/Streamlit
   themes otherwise keep dark select and number-input surfaces. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
.stApp [data-testid="stNumberInput"] [data-baseweb="input"],
.stApp [data-testid="stNumberInput"] [data-baseweb="base-input"],
.stApp [data-testid="stNumberInput"] button,
.stApp [data-testid="stTextInput"] [data-baseweb="input"],
.stApp [data-testid="stTextInput"] [data-baseweb="base-input"] {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  border-color: #CBD5E1 !important;
  box-shadow: none !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] *,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] *,
.stApp [data-testid="stNumberInput"] input,
.stApp [data-testid="stTextInput"] input {
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] svg,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
  fill: #475569 !important;
  color: #475569 !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
  background: #FFFFFF !important;
  color: #0F172A !important;
  border: 1px solid #E2E8F0 !important;
}
[role="option"] {
  background: #FFFFFF !important;
  color: #0F172A !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background: #EFF6FF !important;
  color: #1D4ED8 !important;
}
.stApp [data-testid="stNumberInput"] button:hover {
  background: #F1F5F9 !important;
}
.stApp [data-testid="stSlider"] [data-baseweb="slider"] {
  color: #2563EB !important;
}
.stButton > button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
  min-height: 2.55rem;
  border-radius: 8px;
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  transition: border-color .15s ease, background .15s ease;
}
.stButton > button:hover, [data-testid="stBaseButton-secondary"]:hover {
  border-color: #94A3B8;
  background: #F8FAFC;
}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: var(--accent);
  border-color: var(--accent);
  color: #FFFFFF;
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}
.stButton > button:disabled { opacity: .45; }
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .8rem .95rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .025);
}
[data-testid="stMetricLabel"] * { color: var(--muted) !important; font-size: .78rem; }
[data-testid="stMetricValue"] * { color: var(--text) !important; font-weight: 650; }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 9px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 9px; }
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 9px; background: var(--surface); }
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] { min-width: 0; }
.stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] { overflow-wrap: anywhere; }
[data-testid="stSidebarContent"] { padding-bottom: 1.5rem; }
.stApp [data-testid="stWidgetLabel"] p { color: #334155 !important; font-weight: 500; }
.stApp [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
.stApp [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
.stApp [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
  border-color: #93C5FD !important;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, .10) !important;
}
.stApp [data-testid="stSidebar"] hr { border-color: #E2E8F0; }
.stApp [data-testid="stSidebar"] [data-testid="stExpander"] {
  box-shadow: 0 1px 2px rgba(15, 23, 42, .025);
}
button[kind="primary"] { box-shadow: 0 1px 2px rgba(37, 99, 235, .14); }
@media (max-width: 900px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  [data-testid="stMetric"] { padding: .65rem .7rem; }
  [data-testid="stMetricValue"] { font-size: 1.25rem; }
}

.tl-header {
  display: flex; justify-content: space-between; align-items: center;
  gap: 1.25rem; flex-wrap: wrap;
  padding: .25rem 0 1.15rem; margin-bottom: 1.1rem;
  border-bottom: 1px solid var(--border);
}
.tl-brand { font-size: 1.65rem; font-weight: 700; letter-spacing: -.045em; color: var(--text); }
.tl-brand span { color: var(--accent); }
.tl-sub { font-size: .92rem; font-weight: 600; color: var(--text); margin-top: .15rem; }
.tl-desc { font-size: .84rem; color: var(--muted); margin-top: .25rem; }
.tl-chips { display: flex; gap: .4rem; flex-wrap: wrap; }
.tl-chip {
  font-size: .73rem; color: var(--muted); background: var(--surface);
  border: 1px solid var(--border); border-radius: 7px; padding: .3rem .55rem;
}
.tl-chip b { color: var(--text); font-weight: 600; }
.tl-section {
  font-size: 1rem; font-weight: 650; color: var(--text);
  margin: 1.55rem 0 .7rem; padding-bottom: .45rem;
  border-bottom: 1px solid var(--border);
}
.tl-label {
  font-size: .74rem; font-weight: 650; letter-spacing: .055em;
  text-transform: uppercase; color: var(--muted); margin-bottom: .4rem;
}
.tl-badge {
  display: inline-block; font-size: .73rem; font-weight: 600;
  border-radius: 6px; padding: .2rem .5rem;
  border: 1px solid var(--border); color: var(--muted); background: var(--surface);
}
.tl-ok { color: var(--ok); border-color: #BBF7D0; background: #F0FDF4; }
.tl-warn { color: var(--warn); border-color: #FDE68A; background: #FFFBEB; }
.tl-ok::before { content: "\2713  "; }
.tl-warn::before { content: "! "; }
.tl-panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 9px;
  padding: .85rem 1rem; font-family: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
  font-size: .83rem; line-height: 1.7; color: var(--text);
  white-space: pre-wrap; overflow-wrap: anywhere; user-select: text;
  min-height: 4rem;
}
.tl-panel mark.tl-del { background: #FEF3C7; color: var(--text); text-decoration: line-through; border-radius: 3px; }
.tl-panel mark.tl-add { background: #DBEAFE; color: var(--text); text-decoration: underline; border-radius: 3px; }
@media (max-width: 760px) {
  .block-container { padding: 1rem .8rem 2rem; }
  .tl-header { align-items: flex-start; }
  .tl-brand { font-size: 1.45rem; }
  .tl-chips { gap: .3rem; }
  .tl-chip { font-size: .7rem; }
  .tl-panel { padding: .7rem; font-size: .78rem; }
}
/* Force white surfaces on all BaseWeb select controls, including the
   actual control shell and its inner value container (sidebar + main area). */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div > div {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
  border-color: #CBD5E1 !important;
  box-shadow: none !important;
  opacity: 1 !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] *,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] * {
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] svg,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
  color: #475569 !important;
  fill: #475569 !important;
}
/* Force all Streamlit select controls to use a light surface. The visible
   dark area is often a nested BaseWeb element, so styling only the wrapper
   does not override it. Keep this block last to win against earlier rules. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
.stApp [data-testid="stSelectbox"] [role="combobox"],
.stApp [data-testid="stSelectbox"] [role="combobox"] > div,
.stApp [data-testid="stSelectbox"] [role="combobox"] div,
.stApp [data-testid="stSelectbox"] input,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] span,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
  border-color: #CBD5E1 !important;
  box-shadow: none !important;
}
.stApp [data-testid="stSelectbox"] svg,
.stApp [data-testid="stMultiSelect"] svg {
  color: #475569 !important;
  fill: #475569 !important;
}
.stApp [data-testid="stSelectbox"] [aria-expanded="true"],
.stApp [data-testid="stSelectbox"] [aria-expanded="false"] {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- state
ss = st.session_state
for _k, _v in {"prompt": SAMPLES[0]["prompt"], "run": None, "cmp": None, "error": None, "sample": "(keep current)"}.items():
    ss.setdefault(_k, _v)


def _load_sample():
    name = ss["sample"]
    if name != "(keep current)":
        ss["prompt"] = next(s["prompt"] for s in SAMPLES if s["name"] == name)


@st.cache_data(ttl=10, show_spinner=False)
def _models(provider_name: str) -> list:
    """Return model names; provider discovery failures are handled by the UI."""
    result = get_provider(provider_name).list_models()
    return list(result or [])


@st.cache_data(ttl=10, show_spinner=False)
def _check(provider_name: str, model: str):
    if not model or not model.strip():
        return False, "Enter or select a model name."
    return get_provider(provider_name).check(model)


def _status(provider_name: str, model: str) -> tuple[str, str]:
    """Never report a provider as verified unless its check actually succeeds."""
    try:
        ok, msg = _check(provider_name, model)
    except Exception as exc:
        return "Unavailable", f"Provider check failed ({type(exc).__name__}). Check endpoint and credentials."
    if not ok:
        return "Unavailable", str(msg or "Provider check failed.")
    if provider_name == "ollama":
        return "Verified", "Ollama is reachable and the selected model is installed."
    return "Credentials found, not verified", "Credentials are available; model availability will be confirmed on the first request."


def _price(label, key):
    v = st.number_input(label, min_value=0.0, value=0.0, step=0.01, format="%.4f", key=key)
    return v if v > 0 else None


def _badge(text: str, kind: str = "") -> str:
    return f'<span class="tl-badge {kind}">{html.escape(text)}</span>'


def _section(title: str):
    st.markdown(f'<div class="tl-section">{html.escape(title)}</div>', unsafe_allow_html=True)


def _label(title: str):
    st.markdown(f'<div class="tl-label">{html.escape(title)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- sidebar (existing settings only)
with st.sidebar:
    st.markdown("### Configuration")
    method = st.selectbox("Optimization method", ["rule-based", "llm", "hybrid"],
                          help="rule-based works offline and costs nothing. llm/hybrid call an LLM (which costs tokens).")
    st.markdown("**Target model**")
    provider_name = st.selectbox("Provider", PROVIDER_NAMES, key="prov")
    provider = get_provider(provider_name)
    model_discovery_error = None
    try:
        models = _models(provider_name)
    except Exception as exc:
        models = []
        model_discovery_error = f"Model discovery unavailable ({type(exc).__name__}). You can enter a model name manually."

    # Keep each provider's selection separate so switching providers cannot reuse a stale model.
    model_key = f"model_sel_{provider_name}"
    model_text_key = f"model_txt_{provider_name}"
    if models:
        default_model = "llama3.1" if provider_name == "ollama" else models[0]
        default_index = models.index(default_model) if default_model in models else 0
        model = st.selectbox("Model", models, index=default_index, key=model_key)
    else:
        model = st.text_input(
            "Model", value="llama3.1" if provider_name == "ollama" else "",
            key=model_text_key, placeholder="Enter model name"
        )
        if model_discovery_error:
            st.caption(model_discovery_error)
    state_label, state_msg = _status(provider_name, model)
    st.caption(f"Status: {state_label}. {state_msg}")
    endpoint = getattr(provider, "host", None) or getattr(provider, "base_url", None) or "not set"
    st.caption(f"Endpoint: `{endpoint}`")
    key_env = getattr(provider, "key_env", None)
    if key_env:
        st.caption(f"Credentials are read from `{key_env}` ({'found' if os.getenv(key_env) else 'not set'}) and never displayed.")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.0, step=0.1,
                            help="Lower values are more deterministic; higher values allow more variation.")
    max_tokens = st.number_input("Max output tokens", min_value=16, max_value=4096, value=300, step=16)

    if method != "rule-based":
        st.markdown("**Optimizer model**")
        same = st.checkbox("Use target provider/model", value=True)
        if same:
            opt_provider, opt_model = provider, model
        else:
            opt_provider = get_provider(st.selectbox("Optimizer provider", PROVIDER_NAMES, key="optprov"))
            opt_model = st.text_input("Optimizer model", key="optmodel")
    else:
        opt_provider, opt_model = None, ""

    st.markdown("**Evaluation**")
    use_emb = st.checkbox("Use sentence-transformers embeddings", value=False,
                          help="Needs `pip install sentence-transformers` (downloads a model on first use). Falls back to lexical similarity.")
    use_judge = st.checkbox("Use LLM judge (separate evaluation model)", value=False)
    judge_provider, judge_model = None, ""
    if use_judge:
        judge_provider_name = st.selectbox("Judge provider", PROVIDER_NAMES, key="jprov")
        judge_provider = get_provider(judge_provider_name)
        judge_model = st.text_input("Judge model", key="jmodel", placeholder="Enter evaluation model name")
        if not judge_model.strip():
            st.warning("Set a judge model, otherwise the judge is skipped.")

    with st.expander("Pricing (USD per 1M tokens, optional)"):
        st.caption("Enter prices from your provider's pricing page. Leave 0 for unknown. Nothing is hardcoded.")
        t_price = cc.Pricing(_price("Target input", "ti"), _price("Target output", "to"))
        o_price = cc.Pricing(_price("Optimizer input", "oi"), _price("Optimizer output", "oo"))
        j_price = cc.Pricing(_price("Judge input", "ji"), _price("Judge output", "jo"))
        for _name, _p in (("Target", t_price), ("Optimizer", o_price), ("Judge", j_price)):
            if _p.output_per_m and not _p.input_per_m:
                st.warning(f"{_name}: output price set without an input price; input cost will be unavailable.")

# ---------------------------------------------------------------- header
chip_status = {"Verified": "Verified", "Credentials found, not verified": "Not verified", "Unavailable": "Unavailable"}[state_label]
st.markdown(
    f"""<div class="tl-header"><div>
    <div class="tl-brand">Token<span>Lab</span></div>
    <div class="tl-sub">LLM Prompt Optimization &amp; Evaluation</div>
    <div class="tl-desc">Reduce prompt token usage while preserving meaning and response quality.</div></div>
    <div class="tl-chips"><span class="tl-chip">Provider <b>{html.escape(provider_name)}</b></span>
    <span class="tl-chip">Model <b>{html.escape(model or "not set")}</b></span>
    <span class="tl-chip">Method <b>{html.escape(method)}</b></span>
    <span class="tl-chip">Status <b>{chip_status}</b></span></div></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------- prompt workspace
st.selectbox("Load a sample prompt", ["(keep current)"] + [s["name"] for s in SAMPLES],
             key="sample", on_change=_load_sample,
             help="Loading a sample replaces the current original prompt.")

run = ss["run"]
prompt_now = ss["prompt"]
stale = bool(run and run.result.original != prompt_now)

left, right = st.columns(2, gap="large")
with left:
    _label("Original prompt")
    prompt = st.text_area("Original prompt", key="prompt", height=240, label_visibility="collapsed",
                          placeholder="Paste or type the prompt to optimize...")
    stale = bool(run and run.result.original != prompt)
    meta = f"Words: {word_count(prompt)}"
    if run and not stale:
        meta += f"  |  Tokens: {run.orig_tokens.label}"
    st.caption(meta + ("  |  Edited since last analysis: run Optimize Prompt to refresh counts." if stale else ""))
with right:
    _label("Optimized prompt")
    st.text_area("Optimized prompt", value=run.result.optimized if run else "", height=240, disabled=True,
                 label_visibility="collapsed", placeholder="The optimized prompt appears here after you run Optimize Prompt.")
    if run:
        st.caption(f"Words: {word_count(run.result.optimized)}  |  Tokens: {run.opt_tokens.label}"
                   + ("  |  Shown output belongs to the previous version of the prompt." if stale else ""))
    else:
        st.caption("Not optimized yet.")


# ---------------------------------------------------------------- actions
def _fail(msg: str, clear: bool = False):
    ss["error"] = msg
    if clear:
        ss["run"], ss["cmp"] = None, None


def _do_optimize() -> bool:
    ss["error"] = None
    if not prompt.strip():
        _fail("Enter a prompt before running optimization.")
        return False
    if method != "rule-based":
        if not opt_model or not str(opt_model).strip():
            _fail("Choose or enter an optimizer model before continuing.", clear=True)
            return False
        try:
            ok, msg = opt_provider.check(opt_model)
        except Exception as exc:
            _fail(f"Optimizer check failed ({type(exc).__name__}). Check provider settings.", clear=True)
            return False
        if not ok:
            _fail(f"Optimizer unavailable: {msg}", clear=True)
            return False
    with st.status("Optimizing prompt...", expanded=False) as status:
        try:
            ss["run"] = pl.run_optimization(prompt, method, provider, model, opt_provider, opt_model)
            ss["cmp"] = None
            status.update(label="Optimization complete", state="complete")
            return True
        except (ProviderError, ValueError) as e:
            _fail(str(e), clear=True)
        except Exception as e:  # keep internals and credentials out of the UI
            _fail(f"Unexpected error ({type(e).__name__}). Check provider and model settings.", clear=True)
        status.update(label="Optimization failed", state="error")
    return False


def _do_compare():
    ss["error"] = None
    if not run or stale:
        _fail("Optimize the current prompt before comparing responses.")
        return
    if not model or not str(model).strip():
        _fail("Choose or enter a target model before comparing responses.")
        return
    try:
        ok, msg = provider.check(model)
    except Exception as exc:
        _fail(f"Target model check failed ({type(exc).__name__}). Check provider settings.")
        return
    if not ok:
        _fail(f"Target model unavailable: {msg}")
        return
    with st.status("Generating responses and evaluating...", expanded=False) as status:
        try:
            ss["cmp"] = pl.run_comparison(ss["run"], provider, model, temperature, int(max_tokens), t_price,
                                          use_emb, judge_provider, judge_model, o_price, j_price)
            status.update(label="Comparison complete", state="complete")
            return
        except ProviderError as e:
            _fail(str(e))
        except Exception as e:
            _fail(f"Unexpected error ({type(e).__name__}) during comparison.")
        status.update(label="Comparison failed", state="error")


has_prompt = bool(prompt.strip())
b1, b2, _ = st.columns([1, 1, 2])
do_opt = b1.button("Optimize Prompt", type="primary", width="stretch", disabled=not has_prompt)
can_compare = bool(run) and not stale
do_cmp = b2.button("Compare Responses", width="stretch", disabled=not can_compare,
                   help="Sends the original and optimized prompts to the target model with identical settings.")
if not has_prompt:
    st.info("Enter a prompt to begin.")
elif not run:
    st.caption("Run **Optimize Prompt** first; **Compare Responses** becomes available afterwards.")

if do_opt and has_prompt:
    if _do_optimize():
        st.rerun()  # refresh the editors and enable Compare Responses with the new result
elif do_cmp and can_compare:
    _do_compare()
if ss["error"]:
    st.error(ss["error"])

run, cmp_ = ss["run"], ss["cmp"]
stale = bool(run and run.result.original != ss["prompt"])

# ---------------------------------------------------------------- token efficiency
_section("Token efficiency")
m = st.columns(4)
if run:
    zero = run.orig_tokens.count == 0
    m[0].metric("Original tokens", run.orig_tokens.label)
    m[1].metric("Optimized tokens", run.opt_tokens.label)
    m[2].metric("Tokens saved", str(run.saved))
    m[3].metric("Reduction", "n/a" if zero else f"{run.pct:.1f}%")
    kind = "tl-ok" if run.saved > 0 and not run.result.missing else "tl-warn"
    st.markdown(_badge(run.status, kind) + (" " + _badge("Result is stale", "tl-warn") if stale else ""), unsafe_allow_html=True)
    st.caption(f"Tokenizer: {run.orig_tokens.method}" + ("" if run.orig_tokens.exact else ". Counts are estimates."))
    if run.saved <= 0:
        st.caption("No reduction was achieved: the optimizer kept the prompt (or its change added tokens). "
                   "Token reduction alone does not mean quality is preserved.")
else:
    for col, lab in zip(m, ["Original tokens", "Optimized tokens", "Tokens saved", "Reduction"]):
        col.metric(lab, "—")
    st.caption("Run Optimize Prompt to measure token usage.")

# ---------------------------------------------------------------- before / after
_section("Before and after")
if not run:
    st.info("No optimization results yet.")
else:
    r = run.result
    ta, tb = re.findall(r"\s+|\S+", r.original), re.findall(r"\s+|\S+", r.optimized)
    ha, hb = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        sa, sb = html.escape("".join(ta[i1:i2])), html.escape("".join(tb[j1:j2]))
        if tag == "equal":
            ha.append(sa); hb.append(sb)
        else:
            if sa:
                ha.append(f'<mark class="tl-del">{sa}</mark>')
            if sb:
                hb.append(f'<mark class="tl-add">{sb}</mark>')
    p1, p2 = st.columns(2, gap="large")
    with p1:
        _label("Original")
        st.markdown(f'<div class="tl-panel">{"".join(ha)}</div>', unsafe_allow_html=True)
    with p2:
        _label("Optimized")
        st.markdown(f'<div class="tl-panel">{"".join(hb)}</div>', unsafe_allow_html=True)
    st.caption("Removed words are struck through; added or rewritten words are underlined. Highlighting is display-only.")
    with st.expander("Copy plain text"):
        st.code(r.optimized, language=None, wrap_lines=True)

    in_o = cmp_.api_in_original if cmp_ and cmp_.api_in_original is not None else run.orig_tokens.count
    in_p = cmp_.api_in_optimized if cmp_ and cmp_.api_in_optimized is not None else run.opt_tokens.count
    rows = [("Word count", word_count(r.original), word_count(r.optimized)),
            ("Token count", run.orig_tokens.label, run.opt_tokens.label),
            ("Tokens saved", "—", str(run.saved)),
            ("Reduction", "—", "n/a" if run.orig_tokens.count == 0 else f"{run.pct:.1f}%"),
            ("Estimated input cost", cc.fmt_money(cc.input_cost(in_o, t_price)), cc.fmt_money(cc.input_cost(in_p, t_price))),
            ("Essential information preserved", "100% (reference)", f"{r.preservation * 100:.0f}% of critical tokens"
             + (f" (missing: {', '.join(r.missing)})" if r.missing else ""))]
    t1, t2 = st.columns([3, 2], gap="large")
    with t1:
        st.dataframe(pd.DataFrame(rows, columns=["Metric", "Original", "Optimized"]).astype(str), width="stretch", hide_index=True)
        st.markdown("**Techniques applied:** " + (", ".join(r.techniques) or "none"))
        if r.optimizer_usage:
            st.caption(f"Optimizer LLM usage: input {r.optimizer_usage[0]}, output {r.optimizer_usage[1]} tokens (not free).")
        for n in r.notes:
            (st.warning if "WARNING" in n or "Refused" in n else st.info)(n)
        if r.protected:
            with st.expander("Constraints deliberately kept (not rewritten)"):
                for p in r.protected:
                    st.write("- " + p)
    with t2:
        _label("Token comparison")
        df = pd.DataFrame({"Prompt": ["Original", "Optimized"], "Tokens": [run.orig_tokens.count, run.opt_tokens.count]})
        base = alt.Chart(df).encode(
            x=alt.X("Prompt:N", sort=None, title="Prompt version", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Tokens:Q", title="Token count", scale=alt.Scale(domainMin=0)),
            color=alt.Color("Prompt:N", legend=None, scale=alt.Scale(domain=["Original", "Optimized"], range=["#94A3B8", "#2563EB"])),
            tooltip=[alt.Tooltip("Prompt:N", title="Prompt"), alt.Tooltip("Tokens:Q", title="Tokens", format=",d")])
        chart = base.mark_bar(size=56) + base.mark_text(dy=-8, color="#0F172A").encode(text="Tokens:Q")
        st.altair_chart(chart.properties(height=240), theme=None, width="stretch")
        if not run.orig_tokens.exact:
            st.caption("Token counts are estimates.")

# ---------------------------------------------------------------- response evaluation
_section("Response evaluation")
if not cmp_:
    st.info("No responses yet. Click Compare Responses to run both prompts on the target model and evaluate the outputs.")
else:
    e, rep = cmp_.evaluation, cmp_.evaluation.requirements
    if e.verdict.startswith("Preserved"):
        st.markdown(_badge("Automated checks passed", "tl-ok") + " " + html.escape(e.verdict), unsafe_allow_html=True)
    elif e.verdict.startswith(("Degraded", "Possibly")):
        st.markdown(_badge("Needs review", "tl-warn") + " " + html.escape(e.verdict), unsafe_allow_html=True)
    else:
        st.markdown(_badge("Inconclusive") + " " + html.escape(e.verdict), unsafe_allow_html=True)

    j = e.judge or {}
    judged = lambda k: f"{j[k]}/5" if isinstance(j.get(k), (int, float)) else "Unavailable"
    jhelp = None if e.judge else "Enable the LLM judge in the sidebar to score this."
    so, sp = rep.score("original"), rep.score("optimized")
    cov = "No checkable requirements" if so is None else f"{so * 100:.0f}% / {sp * 100:.0f}%"
    ev = st.columns(5)
    ev[0].metric("Semantic similarity", f"{e.similarity:.2f}", help=e.similarity_method)
    ev[1].metric("Requirement coverage (orig / opt)", cov, help="Rule-checked constraints extracted from the original prompt.")
    ev[2].metric("Instruction compliance", judged("instruction_compliance"), help=jhelp)
    ev[3].metric("Factual consistency", judged("factual_consistency"), help=jhelp)
    ev[4].metric("Output format compliance", judged("format_compliance"), help=jhelp)

    r1, r2 = st.columns(2, gap="large")
    for col, title, text, words, out_tok in ((r1, "Original response", cmp_.resp_original, e.length_original, cmp_.api_out_original),
                                             (r2, "Optimized response", cmp_.resp_optimized, e.length_optimized, cmp_.api_out_optimized)):
        with col:
            _label(title)
            with st.container(border=True):
                st.markdown(text or "*(empty response)*")
            st.caption(f"Words: {words}" + (f"  |  Output tokens: {out_tok}" if out_tok is not None else ""))

    for line in e.reasons:
        st.write("- " + line)
    if rep.requirements:
        with st.expander("Requirement checks"):
            st.dataframe(pd.DataFrame({"Requirement": [q.description for q in rep.requirements],
                                       "Original response": ["Pass" if x else "Fail" for x in rep.original_pass],
                                       "Optimized response": ["Pass" if x else "Fail" for x in rep.optimized_pass]}),
                         width="stretch", hide_index=True)
    if e.judge:
        with st.expander("Judge output"):
            st.json(e.judge)
    st.caption(e.disclaimer)

# ---------------------------------------------------------------- cost analysis
_section("Cost analysis")
if not (t_price.configured or t_price.output_per_m):
    st.info("Cost estimation requires pricing configuration. Enter prices in the sidebar under Pricing.")
elif not run:
    st.info("Run Optimize Prompt to estimate input costs.")
elif not cmp_:
    c_o, c_p = cc.input_cost(run.orig_tokens.count, t_price), cc.input_cost(run.opt_tokens.count, t_price)
    sv = None if c_o is None or c_p is None else c_o - c_p
    st.dataframe(pd.DataFrame([("Original input cost", cc.fmt_money(c_o)), ("Optimized input cost", cc.fmt_money(c_p)),
                               ("Estimated input cost savings", cc.fmt_money(sv))], columns=["Item", "USD (estimate)"]),
                 width="stretch", hide_index=True)
    st.caption("Optimization and evaluation overhead and net savings are calculated after Compare Responses.")
else:
    c = cmp_.costs
    items = [("Original input cost", c["original_input_cost"]), ("Optimized input cost", c["optimized_input_cost"]),
             ("Estimated input cost savings", c["input_cost_savings"]),
             ("Output cost difference (+ means optimized is cheaper)", c["output_cost_difference"]),
             ("Optimization overhead", c["optimization_api_cost"]), ("Evaluation overhead", c["evaluation_api_cost"]),
             ("Estimated net savings", c["net_savings"])]
    st.dataframe(pd.DataFrame([(k, cc.fmt_money(v)) for k, v in items], columns=["Item", "USD (estimate)"]),
                 width="stretch", hide_index=True)
    if c["net_savings"] is None:
        st.caption("Net savings are unavailable until the pricing needed for every line is configured.")
    elif c["net_savings"] <= 0:
        st.warning("The measured result does not show a net saving after overhead.")
    st.caption(c["caveat"])