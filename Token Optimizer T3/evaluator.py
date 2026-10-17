"""Response-quality evaluation.

Automated scores are heuristics, NOT guarantees of correctness or equivalence:
  1. semantic similarity (sentence-transformers if installed, else lexical TF cosine)
  2. rule-checked requirements extracted from the ORIGINAL prompt (length, format, forbidden terms)
  3. optional LLM judge (separate evaluation model) for factual consistency / completeness
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

DISCLAIMER = ("Automated evaluation only. High similarity can hide an omitted fact or constraint, and none of these "
              "scores guarantees correctness or equivalence.")

_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_STOP = set("a an the of to and or in on for is are be it this that with as at by from".split())


# ------------------------------------------------------------------ similarity
@lru_cache(maxsize=1)
def _load_st(name: str):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


def _lexical_cosine(a: str, b: str) -> float:
    ta = Counter(w for w in re.findall(r"[a-z0-9']+", a.lower()) if w not in _STOP)
    tb = Counter(w for w in re.findall(r"[a-z0-9']+", b.lower()) if w not in _STOP)
    dot = sum(ta[w] * tb[w] for w in ta)
    na, nb = math.sqrt(sum(v * v for v in ta.values())), math.sqrt(sum(v * v for v in tb.values()))
    return dot / (na * nb) if na and nb else 0.0


def semantic_similarity(a: str, b: str, use_embeddings: bool = True,
                        model_name: str = "all-MiniLM-L6-v2") -> tuple[float, str]:
    """Returns (score 0..1, method label)."""
    if not a.strip() or not b.strip():
        return 0.0, "n/a (empty response)"
    if use_embeddings:
        try:
            m = _load_st(model_name)
            e = m.encode([a, b], normalize_embeddings=True)
            return max(0.0, float((e[0] * e[1]).sum())), f"sentence-transformers ({model_name})"
        except Exception:
            pass
    return _lexical_cosine(a, b), "lexical TF cosine (fallback; weaker than embeddings)"


# ------------------------------------------------------------------ requirement checks
@dataclass
class Requirement:
    kind: str
    description: str
    value: object = None


def _num(tok: str) -> Optional[int]:
    return int(tok) if tok.isdigit() else _NUM_WORDS.get(tok.lower())


def extract_requirements(prompt: str) -> list[Requirement]:
    reqs: list[Requirement] = []
    low = prompt.lower()
    for m in re.finditer(r"(?:under|within|at most|no more than|max(?:imum)?(?: of)?|less than|up to|fewer than|in)\s+(\d+)\s+words", low):
        reqs.append(Requirement("max_words", f"at most {m.group(1)} words", int(m.group(1))))
    for m in re.finditer(r"(exactly\s+)?(\d+|one|two|three|four|five|six)\s+(?:bullet points?|bullets?)", low):
        reqs.append(Requirement("bullets", f"{m.group(2)} bullet points", _num(m.group(2))))
    for m in re.finditer(r"(?:in|under|within|at most|no more than|exactly|up to)\s+(\d+|one|two|three|four|five)\s+sentences?", low):
        reqs.append(Requirement("max_sentences", f"at most {m.group(1)} sentences", _num(m.group(1))))
    if re.search(r"\bjson\b", low):
        reqs.append(Requirement("json", "valid JSON output"))
    if re.search(r"\b(?:markdown )?table\b", low) and re.search(r"\b(?:as|in|into|a|use)\b.{0,20}\btable\b", low):
        reqs.append(Requirement("table", "table format"))
    if re.search(r"\bpython\b", low) and re.search(r"\b(?:write|program|function|script|code|implement)\b", low):
        reqs.append(Requirement("python_code", "contains Python code"))
    for m in re.finditer(r"(?:do not|don't|never|avoid|without)\s+(?:using|use|mention(?:ing)?|including|include|providing|provide|giving|give)?\s*(?:the word\s+|the phrase\s+|any\s+)?[\"“]?([a-z][a-z\- ]{1,30}?)[\"”]?(?=[.,;!?]|$|\s+and\b|\s+or\b)", low):
        term = m.group(1).strip()
        if term and not set(term.split()) & {"unnecessary", "extra", "irrelevant", "details", "detail", "jargon words"}:
            reqs.append(Requirement("forbidden", f"must not contain '{term}'", term))
    for m in re.finditer(r"\"([^\"]{3,60})\"", prompt):
        if re.search(r"(?:include|contain|use|say|add)[^\"]{0,30}$", prompt[:m.start()].lower()[-50:]) and "word \"" not in prompt[:m.start()].lower()[-8:]:
            reqs.append(Requirement("required_phrase", f"must contain '{m.group(1)}'", m.group(1).lower()))
    return reqs


def check_requirement(req: Requirement, response: str) -> bool:
    r, low = response, response.lower()
    if req.kind == "max_words":
        return len(r.split()) <= req.value
    if req.kind == "bullets":
        return len(re.findall(r"^\s*(?:[-*•]|\d+[.)])\s+", r, re.M)) == req.value
    if req.kind == "max_sentences":
        return len([s for s in re.split(r"(?<=[.!?])\s+", r.strip()) if s]) <= req.value
    if req.kind == "json":
        t = re.sub(r"^```(?:json)?|```$", "", r.strip(), flags=re.M).strip()
        try:
            json.loads(t); return True
        except Exception:
            return False
    if req.kind == "table":
        return r.count("|") >= 4
    if req.kind == "python_code":
        return "```" in r or bool(re.search(r"^\s*(?:def |import |print\(|for |class )", r, re.M))
    if req.kind == "forbidden":
        return req.value not in low
    if req.kind == "required_phrase":
        return req.value in low
    return True


@dataclass
class RequirementReport:
    requirements: list[Requirement]
    original_pass: list[bool]
    optimized_pass: list[bool]

    @property
    def regressions(self) -> list[str]:
        return [q.description for q, o, p in zip(self.requirements, self.original_pass, self.optimized_pass) if o and not p]

    def score(self, which: str) -> Optional[float]:
        flags = self.original_pass if which == "original" else self.optimized_pass
        return sum(flags) / len(flags) if flags else None


# ------------------------------------------------------------------ LLM judge
JUDGE_SYSTEM = "You are a strict, impartial evaluator of LLM responses. Reply with JSON only."
JUDGE_TEMPLATE = """Task given to an assistant (ORIGINAL prompt):
<<<
{task}
>>>

Response A:
<<<
{a}
>>>

Response B:
<<<
{b}
>>>

Compare A and B against the ORIGINAL task requirements. Return ONLY JSON:
{{"factual_consistency": 1-5, "completeness": 1-5, "instruction_compliance": 1-5, "format_compliance": 1-5,
 "equivalent": true/false, "omitted_in_B": ["facts/constraints present in A but missing in B"], "notes": "one sentence"}}
(Scores rate B relative to A and the task: 5 = fully equal or better.)"""


def llm_judge(provider, model: str, task: str, resp_a: str, resp_b: str):
    """Returns (parsed dict or None, usage tuple (in, out, model))."""
    r = provider.generate(JUDGE_TEMPLATE.format(task=task, a=resp_a, b=resp_b), model,
                          temperature=0.0, max_tokens=400, system=JUDGE_SYSTEM)
    usage = (r.input_tokens, r.output_tokens, model)
    m = re.search(r"\{.*\}", r.text, re.S)
    try:
        return json.loads(m.group()), usage
    except Exception:
        return None, usage


# ------------------------------------------------------------------ overall
@dataclass
class EvaluationResult:
    similarity: float
    similarity_method: str
    requirements: RequirementReport
    judge: Optional[dict]
    verdict: str
    reasons: list[str] = field(default_factory=list)
    length_original: int = 0
    length_optimized: int = 0
    disclaimer: str = DISCLAIMER


def evaluate(original_prompt: str, resp_original: str, resp_optimized: str,
             use_embeddings: bool = True, judge: Optional[dict] = None) -> EvaluationResult:
    sim, method = semantic_similarity(resp_original, resp_optimized, use_embeddings)
    reqs = extract_requirements(original_prompt)
    rep = RequirementReport(reqs, [check_requirement(q, resp_original) for q in reqs],
                            [check_requirement(q, resp_optimized) for q in reqs])
    threshold = 0.80 if method.startswith("sentence") else 0.45
    reasons = [f"Similarity {sim:.2f} ({'above' if sim >= threshold else 'below'} {threshold:.2f} threshold; {method})"]
    if reqs:
        reasons.append(f"Checkable requirements: original {sum(rep.original_pass)}/{len(reqs)}, optimized {sum(rep.optimized_pass)}/{len(reqs)}")
    else:
        reasons.append("No rule-checkable requirements found in the prompt (length/format/forbidden terms).")

    if rep.regressions:
        verdict = "Degraded: optimized response violates requirement(s) the original met"
        reasons.append("Regressions: " + "; ".join(rep.regressions))
    elif judge and judge.get("equivalent") is False:
        verdict = "Possibly degraded: judge model flagged differences"
        reasons.append(f"Judge: {judge.get('notes', '')} Omitted: {judge.get('omitted_in_B')}")
    elif sim >= threshold and (judge is None or judge.get("equivalent") is True):
        verdict = "Preserved (automated check)" + ("" if judge else "; no judge model used")
        if judge:
            reasons.append(f"Judge: {judge.get('notes', '')}")
    else:
        verdict = "Inconclusive: low similarity, review responses manually"
    return EvaluationResult(sim, method, rep, judge, verdict, reasons, len(resp_original.split()), len(resp_optimized.split()))
