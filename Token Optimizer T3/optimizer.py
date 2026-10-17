"""Prompt optimizer: rule-based (offline) and optional LLM-based rewriting.

Safety design: every aggressive rewrite is verified against a set of "critical tokens"
(numbers, quoted text, negations, formats, languages, proper nouns). If a rewrite would
drop one, the sentence is kept in its safe-cleaned form instead. User-provided data blocks
(text after "the following text:" etc.) are never modified.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# ------------------------------------------------------------------ critical tokens
NEG_GROUP = {"not", "no", "never", "without", "avoid", "cannot", "nor", "none"}
STRICT_WORDS = {"only", "exactly", "must", "always", "at least", "at most"}
TECH_WORDS = {
    "json", "xml", "yaml", "csv", "html", "css", "markdown", "table", "bullet", "bullets", "numbered",
    "python", "java", "javascript", "typescript", "sql", "rust", "golang", "c++", "c#", "bash", "regex",
    "pandas", "numpy", "words", "word", "sentences", "sentence", "paragraphs", "lines", "characters",
    "steps", "examples", "example", "descending", "ascending", "tone", "format",
}
CONTRACTIONS = {"don't": "do not", "dont": "do not", "can't": "cannot", "won't": "will not",
                "shouldn't": "should not", "mustn't": "must not", "isn't": "is not", "doesn't": "does not"}
_TOKEN_RE = re.compile(r"[A-Za-z0-9_+#]+(?:['’.\-][A-Za-z0-9_+#]+)*")


def _norm(text: str) -> str:
    t = text.lower().replace("’", "'")
    for k, v in CONTRACTIONS.items():
        t = t.replace(k, v)
    return t


def critical_tokens(text: str) -> set[str]:
    """Tokens that must survive any rewrite."""
    crit: set[str] = set()
    for m in re.finditer(r"\d+(?:[.,]\d+)*%?", text):
        crit.add(m.group().lower())
    for m in re.finditer(r"\"([^\"]+)\"|`([^`]+)`", text):
        crit.add((m.group(1) or m.group(2)).lower().strip())
    for m in re.finditer(r"⟦\d+⟧", text):
        crit.add(m.group())
    words = _TOKEN_RE.findall(text)
    low = _norm(text)
    lowwords = set(_TOKEN_RE.findall(low))
    if lowwords & NEG_GROUP:
        crit.add("<NEG>")
    for w in lowwords:
        if w in STRICT_WORDS or w in TECH_WORDS:
            crit.add(w)
    # mid-sentence capitalised words / acronyms / camelCase / snake_case
    at_start = True
    for m in re.finditer(r"[A-Za-z0-9_+#]+(?:['’.\-][A-Za-z0-9_+#]+)*|[.!?:\n]", text):
        tok = m.group()
        if tok in ".!?:\n":
            at_start = True
            continue
        if not at_start and (tok[0].isupper() or "_" in tok or re.search(r"[a-z][A-Z]", tok)):
            crit.add(tok.lower())
        at_start = False
    return crit


def _present(tok: str, out_norm: str, out_words: set[str]) -> bool:
    if tok == "<NEG>":
        return bool(out_words & NEG_GROUP)
    if tok.isalnum() or re.fullmatch(r"[a-z0-9_+#]+", tok):
        return tok in out_words or tok + "s" in out_words or (tok.endswith("s") and tok[:-1] in out_words)
    return tok in out_norm


def missing_critical(original: str, optimized: str) -> list[str]:
    out_norm = _norm(optimized)
    out_words = set(_TOKEN_RE.findall(out_norm))
    return sorted(t for t in critical_tokens(original) if not _present(t, out_norm, out_words))


def check_preservation(original: str, optimized: str) -> tuple[float, list[str]]:
    """Fraction of critical tokens from the original still present (1.0 = all)."""
    crit = critical_tokens(original)
    if not crit:
        return 1.0, []
    miss = missing_critical(original, optimized)
    return (len(crit) - len(miss)) / len(crit), miss


# ------------------------------------------------------------------ rule tables
SAFE_RULES: list[tuple[str, str, str]] = [
    # (pattern, replacement, technique label)
    (r"^(?:hi|hello|hey)\b[\s,!.:-]*(?:there\b[\s,!.:-]*)?", "", "A"),
    (r"\bas an ai(?: language model)?,?\s*", "", "A"),
    (r"\b(?:please|kindly)\b,?\s*", "", "A"),
    (r"\bi would (?:really )?(?:appreciate|love) it if you (?:could|would|can)\s+", "", "C"),
    (r"\b(?:i would like|i want|i need|i'd like) you to\s+", "", "C"),
    (r"\b(?:i was |i am )?wondering if you (?:could|can|would)\s+", "", "C"),
    (r"^(?:is it possible for you to|do you think you could)\s+", "", "C"),
    (r"^(?:can|could|would|will) you\s+", "", "C"),
    (r"\bin order to\b", "to", "A"),
    (r"\bdue to the fact that\b", "because", "A"),
    (r"\bin the event that\b", "if", "A"),
    (r"\bfor the purpose of\b", "for", "A"),
    (r"\ba large number of\b", "many", "A"),
    (r"\bat this point in time\b", "now", "A"),
    (r"\b(?:with regard to|with respect to|in regard to)\b", "about", "A"),
    (r"\bit (?:is|should be) (?:worth|important to) not(?:e|ing) that\s+", "", "A"),
    (r"\b(?:really|basically|actually)\s+", "", "A"),
    (r"\bas well as\b", "and", "A"),
    (r"\b(?:thanks|thank you)(?: so much| very much| in advance)?[,.!]?\s*$", "", "A"),
]

_ADV = {"brief": "briefly", "short": "briefly", "concise": "concisely", "quick": "quickly", "detailed": "in detail"}
_NOUN_VERB = {"explanation": "explain", "summary": "summarize", "overview": "give an overview of", "description": "describe"}


def _noun_phrase_rewrite(m: re.Match) -> str:
    adj, noun = (m.group(1) or "").lower(), m.group(2).lower()
    verb = _NOUN_VERB[noun]
    if not adj:
        return verb + " "
    adv = _ADV[adj]
    return f"{verb} {adv} " if adv == "in detail" and False else (f"{adv} {verb} " if adv != "in detail" else f"{verb} in detail ")


GUARDED_RULES: list[tuple[str, object, str]] = [
    (r"\b(?:provide|give)(?: me)?(?: with)? an? (?:(brief|short|concise|quick|detailed) )?(explanation|summary|overview|description) of\s+",
     _noun_phrase_rewrite, "A"),
    (r"\bexplain to me\b", "explain", "A"),
    (r"\bin (?:a way|terms|simple terms|plain terms|plain language|simple language) that (?:is|are) (?:easy|simple|understandable)(?: enough)? for (?:an? |the )?((?:complete |absolute |total )?\w+?)s? to understand",
     lambda m: f"in {m.group(1).strip().replace(' ', '-') if ' ' not in m.group(1).strip() else m.group(1).strip().replace(' ', ' ')}-friendly language".replace("complete-", "complete "), "C"),
    (r"\b(explain|describe|define) what ((?:the )?[\w\- ]+?) (?:is|are)\b(?=\s*[.?!,]|\s*$|\s+(?:in|for|to|and)\b)", r"\1 \2", "C"),
    (r"\bthe (?:concept|idea|notion) of\s+", "", "C"),
    (r"\b(?:in addition|additionally|furthermore|moreover),?\s+", "", "A"),
]

PLEASANTRY_SENT = re.compile(
    r"^(?:i hope|hope) (?:you|this|all)\b.*|^how are you\b.*|^(?:thanks|thank you)\b.*|^i appreciate (?:your|the) (?:help|time)\b.*", re.I)

# ---- repeated-instruction concepts
BREVITY = {"short", "brief", "briefly", "concise", "concisely", "succinct", "succinctly", "compact", "terse", "shortly"}
LONGWORDS = {"long", "lengthy", "wordy"}
DETAIL_NOUNS = {"details", "detail", "information", "content", "fluff", "text", "words", "waffle"}
DETAIL_ADJ = {"unnecessary", "extra", "irrelevant", "superfluous", "needless", "excessive"}
CONCEPT_FILLER = {
    "keep", "your", "the", "a", "an", "answer", "answers", "response", "responses", "explanation", "reply", "output",
    "it", "its", "this", "that", "make", "be", "is", "are", "and", "also", "do", "does", "not", "avoid", "provide",
    "give", "include", "any", "to", "of", "too", "much", "no", "write", "should", "very", "really", "more",
    "details", "detail", "information", "content", "fluff", "text", "words", "waffle",
    "unnecessary", "extra", "irrelevant", "superfluous", "needless", "excessive",
} | BREVITY | LONGWORDS


def _concept_flags(sentence: str) -> Optional[tuple[bool, bool]]:
    """Return (brevity, no_unnecessary_details) if the sentence is ONLY such a vague style instruction."""
    low = _norm(sentence)
    words = _TOKEN_RE.findall(low)
    if not words or any(w not in CONCEPT_FILLER for w in words):
        return None
    wset = set(words)
    neg = "not" in wset or "no" in wset or "avoid" in wset
    brev = bool(wset & BREVITY)
    longw = bool(wset & LONGWORDS)
    details = bool(wset & DETAIL_ADJ) and bool(wset & DETAIL_NOUNS)
    if brev and neg and not details:
        return None                      # e.g. "do not be brief" -> opposite meaning, keep
    if longw and not neg:
        return None                      # e.g. "make it long"
    if longw and neg:
        brev = True
    if neg and not (details or longw):
        return None
    if not (brev or details):
        return None
    return brev, details


# ---- structured merge (technique F)
COMMON_VERBS = {
    "take", "calculate", "display", "print", "return", "read", "write", "sort", "store", "accept", "check",
    "validate", "handle", "output", "input", "compute", "show", "ask", "prompt", "convert", "remove", "add",
    "include", "support", "use", "save", "load", "open", "close", "count", "find", "search", "filter", "parse",
    "generate", "create", "send", "receive", "call", "list", "log", "raise", "loop", "iterate", "reverse",
}


def _third_person(word: str) -> str:
    if re.search(r"(?:s|x|z|ch|sh|o)$", word):
        return word + "es"
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    return word + "s"


def _conjugate_clause(clause: str) -> str:
    words = clause.split()
    if not words:
        return clause
    out = []
    for i, w in enumerate(words):
        prev = words[i - 1].lower() if i else ""
        if (i == 0 or prev == "and") and w.lower() in COMMON_VERBS:
            out.append(_third_person(w.lower()))
        else:
            out.append(w)
    return " ".join(out)


_BASE_RE = re.compile(r"^(write|create|build|implement|develop|make|generate)\s+(.+?\b(?:program|function|script|class|code|app|application|module))\b(.*?)\.?$", re.I)
_FOLLOW_RE = re.compile(r"^(?:(?:the|this) (?:program|function|script|class|code|app|application|module)|it) (?:should|will|needs to|has to) (.+?)\.?$", re.I)
_STRICT_BLOCK = re.compile(r"\b(?:must|never|not|only|exactly|always|don't|dont|without|no)\b|n't", re.I)


# ------------------------------------------------------------------ result type
@dataclass
class OptimizationResult:
    original: str
    optimized: str
    method: str = "rule-based"
    techniques: list[str] = field(default_factory=list)
    protected: list[str] = field(default_factory=list)   # constraints kept on purpose
    notes: list[str] = field(default_factory=list)
    preservation: float = 1.0
    missing: list[str] = field(default_factory=list)
    optimizer_usage: Optional[tuple] = None              # (input_tokens, output_tokens, model)


@dataclass
class _Sent:
    text: str
    kind: str = "prose"        # prose | list | data
    prefix: str = ""
    line: int = 0
    dropped: bool = False
    ender: str = ""
    note: str = ""


DATA_INTRO = re.compile(r"(?:\b(?:following|below)\b[^\n]*$|(?:text|article|passage|data|document|code|input|dataset|csv|table|email|essay)\b[^.\n]*:\s*$)", re.I)
DATA_LABEL = re.compile(r"^\s*(?:text|article|passage|data|input|document|content|code|csv|email|essay)\s*:", re.I)
LIST_ITEM = re.compile(r"^(\s*(?:[-*•]|\d+[.)])\s+)(.*)$")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _mask(text: str) -> tuple[str, list[str]]:
    store: list[str] = []

    def sub(m):
        store.append(m.group())
        return f"⟦{len(store) - 1}⟧"
    text = re.sub(r"```.*?```|`[^`\n]+`|\"[^\"\n]+\"", sub, text, flags=re.S)
    return text, store


def _unmask(text: str, store: list[str]) -> str:
    for i, s in enumerate(store):
        text = text.replace(f"⟦{i}⟧", s)
    return text


def _apply(rules, s: str, used: set[str]) -> str:
    for pat, rep, tag in rules:
        new = re.sub(pat, rep, s, flags=re.I)
        if new != s:
            used.add(tag)
            s = new
    return s


def _tidy(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r"^[,;:\s]+", "", s)
    return s


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _split_sentence(s: str) -> tuple[str, str]:
    m = re.match(r"^(.*?)([.!?]*)$", s.strip(), re.S)
    return m.group(1), m.group(2)


# ------------------------------------------------------------------ rule-based optimizer
def optimize_rule_based(text: str) -> OptimizationResult:
    res = OptimizationResult(original=text, optimized=text)
    if not text.strip():
        res.notes.append("Empty prompt: nothing to optimize.")
        return res

    masked, store = _mask(text)
    used: set[str] = set()
    lines = masked.split("\n")
    sents: list[_Sent] = []
    in_data = False

    for li, line in enumerate(lines):
        if not line.strip():
            continue
        if in_data:
            sents.append(_Sent(line, "data", line=li))
            continue
        if DATA_LABEL.match(line):
            in_data = True
            res.notes.append("Detected user-provided data block: left untouched.")
            sents.append(_Sent(line, "data", line=li))
            continue
        lm = LIST_ITEM.match(line)
        body, prefix = (lm.group(2), lm.group(1)) if lm else (line, "")
        parts = [p for p in SENT_SPLIT.split(body.strip()) if p]
        for p in parts:
            sents.append(_Sent(p, "list" if lm else "prose", prefix if p is parts[0] else "", li))
        if DATA_INTRO.search(line.strip()):
            in_data = True
            res.notes.append("Detected user-provided data block: left untouched.")

    # ---- pass 1: per-sentence cleaning (A, C) with critical-token guard
    for s in sents:
        if s.kind == "data":
            continue
        raw = s.text
        core, s.ender = _split_sentence(raw)
        if PLEASANTRY_SENT.match(core.strip()):
            s.dropped = True
            used.add("A")
            continue
        local: set[str] = set()
        safe = _tidy(_apply(SAFE_RULES, core, local))
        guarded = _tidy(_apply(GUARDED_RULES, safe, local))
        chosen = guarded
        miss = missing_critical(core, guarded) if guarded != safe else []
        miss_safe = missing_critical(core, safe)
        if miss_safe:                       # even safe rules dropped something -> keep raw
            chosen, local = core, set()
            s.note = core
        elif miss:
            chosen = safe
            s.note = f"{core}  [kept: rewrite would drop {miss}]"
            res.notes.append(f"Refused rewrite that would drop critical info {miss}.")
        elif critical_tokens(core) & (STRICT_WORDS | {"<NEG>"}):
            s.note = core
        if chosen != core:
            used |= local
        if "?" in s.ender and chosen != core and not re.match(
                r"(?:what|why|how|when|where|who|which|is|are|does|do|did|can|could|should|would|will)\b", chosen, re.I):
            s.ender = "."
        s.text = chosen
        if not s.text:
            s.dropped = True

    live = [s for s in sents if not s.dropped]

    # ---- pass 2: repeated vague style instructions -> one instruction (B)
    flags = [(s, _concept_flags(s.text)) for s in live if s.kind != "data"]
    concept = [(s, f) for s, f in flags if f]
    if sum(int(f[0]) + int(f[1]) for _, f in concept) >= 2:
        brev = any(f[0] for _, f in concept)
        det = any(f[1] for _, f in concept)
        canon = ("Answer concisely without unnecessary details" if brev and det
                 else "Be concise" if brev else "Avoid unnecessary details")
        first = concept[0][0]
        first.text, first.ender = canon, "."
        for s_, _ in concept:
            s_.note = ""
        for s, _ in concept[1:]:
            s.dropped = True
        used.add("B")

    elif len(concept) == 1 and concept[0][1] == (True, False):
        if any(re.match(r"(?:briefly|concisely|succinctly)\b", x.text, re.I) for x in live if x is not concept[0][0] and x.kind == "prose"):
            concept[0][0].dropped = True
            used.add("B")

    live = [s for s in sents if not s.dropped]
    for s in sents:  # merged vague-style sentences are not "protected constraints"
        if s.note and not s.dropped and s.kind != "data" and not (_concept_flags(s.text) and s.text.startswith(("Answer concisely", "Be concise", "Avoid unnecessary"))):
            res.protected.append(s.note)

    # ---- pass 3: drop sentences fully contained in another (E)
    prose = [s for s in live if s.kind != "data"]
    def wset(s): return set(_TOKEN_RE.findall(_norm(s.text)))
    for i, a in enumerate(prose):
        if a.dropped or len(wset(a)) < 3:
            continue
        for j, b in enumerate(prose):
            if i != j and not b.dropped and wset(a) <= wset(b) and (wset(a) != wset(b) or i < j):
                a.dropped = True
                used.add("E")
                break

    live = [s for s in sents if not s.dropped]

    # ---- pass 4: structured merge "Write X program. It should A. It should B." (F)
    i = 0
    while i < len(live):
        s = live[i]
        m = _BASE_RE.match(s.text) if s.kind == "prose" else None
        if m and not _STRICT_BLOCK.search(s.text):
            clauses, j = [], i + 1
            while j < len(live) and live[j].kind == "prose":
                fm = _FOLLOW_RE.match(live[j].text + live[j].ender)
                if not fm or _STRICT_BLOCK.search(live[j].text) or live[j].line != s.line:
                    break
                clauses.append(fm.group(1)); j += 1
            if clauses:
                conj = [_conjugate_clause(c) for c in clauses]
                conj = [re.sub(r"^takes (.+?) as input\b", r"inputs \1", c) for c in conj]
                sep = ", " if " and " in conj[-1] else " and "
                joined = conj[0] if len(conj) == 1 else ", ".join(conj[:-1]) + sep + conj[-1]
                s.text = f"{s.text.rstrip('.')} that {joined}"
                s.ender = "."
                for k in range(i + 1, j):
                    live[k].dropped = True
                used.add("F")
                live = [x for x in live if not x.dropped]
        i += 1

    # ---- reassemble
    out_lines: dict[int, list[str]] = {}
    for s in sents:
        if s.dropped:
            continue
        if s.kind == "data":
            out_lines.setdefault(s.line, []).append(s.text)
        else:
            t = _cap(s.text) + (s.ender or ("." if s.text and s.text[-1] not in ".!?" else ""))
            out_lines.setdefault(s.line, []).append(s.prefix + t if s.prefix else t)
    final = []
    for li in range(len(lines)):
        if li in out_lines:
            final.append(" ".join(out_lines[li]) if lines[li].strip() and not LIST_ITEM.match(lines[li]) or len(out_lines[li]) == 1 else " ".join(out_lines[li]))
        elif not lines[li].strip():
            final.append("")
    optimized = _unmask("\n".join(final), store)
    res.protected = [_unmask(x, store) for x in res.protected]
    optimized = re.sub(r"\n{3,}", "\n\n", optimized).strip()

    # never return something that lost critical info
    pres, miss = check_preservation(text, optimized)
    if miss:
        res.notes.append(f"Safety net: final check found missing {miss}; returning original prompt unchanged.")
        optimized, pres, miss = text, 1.0, []

    res.optimized = optimized
    res.preservation, res.missing = pres, miss
    labels = {"A": "A. Redundant words/filler removed", "B": "B. Repeated instructions merged",
              "C": "C. Verbose instructions simplified", "E": "E. Redundant context/sentences removed",
              "F": "F. Structured prompt compacted"}
    res.techniques = [labels[k] for k in sorted(used) if k in labels]
    if res.protected:
        res.techniques.append("D. Constraints preserved (not rewritten)")
    if optimized == text:
        res.notes.append("No safe optimization found; prompt returned unchanged.")
    return res


# ------------------------------------------------------------------ LLM-based optimizer
LLM_OPTIMIZER_SYSTEM = (
    "You are a prompt compression engine. Rewrite the user's prompt so it uses fewer tokens.\n"
    "Rules:\n"
    "- Preserve the original intent and ALL essential constraints (numbers, units, formats, languages, "
    "negative constraints, safety instructions, examples, user-provided data).\n"
    "- Remove redundant wording and repeated instructions.\n"
    "- Do NOT invent new requirements. Do NOT answer the prompt.\n"
    "- Prefer fewer tokens without sacrificing clarity.\n"
    "- Output ONLY the optimized prompt, with no preface, quotes or explanation."
)


def optimize_with_llm(text: str, provider, model: str, max_tokens: Optional[int] = None) -> OptimizationResult:
    """Rewrite a prompt with an LLM. Its token usage is reported separately (it is not free)."""
    res = OptimizationResult(original=text, optimized=text, method=f"llm ({getattr(provider, 'name', '?')}:{model})")
    if not text.strip():
        res.notes.append("Empty prompt: nothing to optimize.")
        return res
    r = provider.generate(text, model, temperature=0.0,
                          max_tokens=max_tokens or max(256, len(text.split()) * 3), system=LLM_OPTIMIZER_SYSTEM)
    out = r.text.strip()
    out = re.sub(r"^```(?:\w+)?\n|\n```$", "", out).strip()
    if len(out) > 1 and out[0] == out[-1] == '"' and '"' not in text[:1]:
        out = out[1:-1].strip()
    res.optimized = out or text
    res.optimizer_usage = (r.input_tokens, r.output_tokens, model)
    res.preservation, res.missing = check_preservation(text, res.optimized)
    res.techniques = ["G. LLM-based rewrite"]
    if res.missing:
        res.notes.append(f"WARNING: LLM rewrite may have dropped critical info: {res.missing}. Review before using.")
    return res


def optimize(text: str, method: str = "rule-based", provider=None, model: str = "") -> OptimizationResult:
    """method: 'rule-based' | 'llm' | 'hybrid' (rules first, then LLM)."""
    if method == "rule-based":
        return optimize_rule_based(text)
    if provider is None or not model:
        raise ValueError("LLM-based optimization needs a provider and model.")
    if method == "llm":
        return optimize_with_llm(text, provider, model)
    if method == "hybrid":
        rb = optimize_rule_based(text)
        llm = optimize_with_llm(rb.optimized, provider, model)
        llm.original, llm.method = text, f"hybrid (rules + {llm.method})"
        llm.techniques = rb.techniques + llm.techniques
        llm.protected = rb.protected
        llm.preservation, llm.missing = check_preservation(text, llm.optimized)
        return llm
    raise ValueError(f"Unknown optimization method: {method}")
