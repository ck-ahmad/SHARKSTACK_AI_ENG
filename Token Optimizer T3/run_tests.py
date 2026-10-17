"""Run the demo prompts and write test_results.md.

  python run_tests.py                                   # offline: optimization + token stats only
  python run_tests.py --provider ollama --model llama3.1 --input-price 0.1 --output-price 0.4
  python run_tests.py --mock                            # exercises the comparison pipeline with a FAKE model (not real results)
"""
from __future__ import annotations

import argparse
import datetime as dt

import cost_calculator as cc
import pipeline as pl
from llm_provider import LLMResult, ProviderError, get_provider
from sample_prompts import SAMPLES


class MockProvider:
    """Deterministic fake model for pipeline smoke tests ONLY."""
    name = "mock"

    def generate(self, prompt, model, temperature=0.0, max_tokens=512, system=None, seed=42):
        text = f"[mock answer to a prompt of {len(prompt.split())} words] " + " ".join(prompt.split()[:12])
        return LLMResult(text, None, len(text.split()), 0.0, model)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider"); ap.add_argument("--model", default="")
    ap.add_argument("--judge-provider"); ap.add_argument("--judge-model", default="")
    ap.add_argument("--input-price", type=float); ap.add_argument("--output-price", type=float)
    ap.add_argument("--temperature", type=float, default=0.0); ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--out", default="test_results.md")
    a = ap.parse_args()

    provider = MockProvider() if a.mock else (get_provider(a.provider) if a.provider else None)
    model = "mock" if a.mock else a.model
    judge = get_provider(a.judge_provider) if a.judge_provider else None
    pricing = cc.Pricing(a.input_price, a.output_price)
    if provider and not a.mock:
        ok, msg = provider.check(model)
        if not ok:
            raise SystemExit(f"Provider not usable: {msg}")

    lines = [f"# Test results ({dt.datetime.now():%Y-%m-%d %H:%M})", "",
             f"- Target provider/model: {a.provider or 'none (offline)'} / {model or '-'}"
             + ("  **(MOCK MODEL: responses are fake, pipeline smoke test only)**" if a.mock else ""),
             f"- Pricing configured: {'yes' if pricing.configured else 'no'}", ""]
    summary = []
    for s in SAMPLES:
        run = pl.run_optimization(s["prompt"], "rule-based", provider, model)
        r = run.result
        lines += [f"## {s['name']}  ({s['category']})", "",
                  "**Original prompt**", "```", s["prompt"], "```", "**Optimized prompt**", "```", r.optimized, "```",
                  f"- Tokenizer: {run.orig_tokens.method}",
                  f"- Tokens: original {run.orig_tokens.label} -> optimized {run.opt_tokens.label}",
                  f"- Saved: {run.saved} tokens ({run.pct:.1f}%)  | status: {run.status}",
                  f"- Techniques: {', '.join(r.techniques) or 'none'}",
                  f"- Essential info preserved: {r.preservation * 100:.0f}% of critical tokens",
                  ]
        if r.protected:
            lines.append("- Constraints kept on purpose: " + "; ".join(f"`{p}`" for p in r.protected))
        for n in r.notes:
            lines.append(f"- Note: {n}")
        if provider:
            try:
                c = pl.run_comparison(run, provider, model, a.temperature, a.max_tokens, pricing,
                                      use_embeddings=False, judge_provider=judge, judge_model=a.judge_model)
                e = c.evaluation
                lines += ["", "**Original response**", "```", c.resp_original, "```",
                          "**Optimized response**", "```", c.resp_optimized, "```",
                          f"- Verdict: {e.verdict}", *[f"  - {x}" for x in e.reasons],
                          f"- Input cost savings: {cc.fmt_money(c.costs['input_cost_savings'])}; net: {cc.fmt_money(c.costs['net_savings'])}"]
            except ProviderError as ex:
                lines.append(f"- Comparison failed: {ex}")
        else:
            lines.append("- Responses: not generated (no provider selected; run with --provider to fill this in).")
        lines.append("")
        summary.append((s["name"], run.orig_tokens.count, run.opt_tokens.count, run.saved, run.pct))

    lines += ["## Summary", "", "| Prompt | Original | Optimized | Saved | % |", "|---|---|---|---|---|"]
    lines += [f"| {n} | {o} | {p} | {sv} | {pc:.1f}% |" for n, o, p, sv, pc in summary]
    open(a.out, "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
