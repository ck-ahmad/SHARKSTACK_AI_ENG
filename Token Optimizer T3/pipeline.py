"""Glue between optimizer, tokenizer, providers, evaluator and cost calculator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cost_calculator as cc
import evaluator as ev
import optimizer as op
import token_counter as tc


@dataclass
class OptimizationRun:
    result: op.OptimizationResult
    orig_tokens: tc.TokenCount
    opt_tokens: tc.TokenCount

    @property
    def saved(self) -> int:
        return tc.tokens_saved(self.orig_tokens.count, self.opt_tokens.count)

    @property
    def pct(self) -> float:
        return tc.reduction_pct(self.orig_tokens.count, self.opt_tokens.count)

    @property
    def status(self) -> str:
        if self.result.missing:
            return "Warning: critical information may be missing"
        if self.saved > 0:
            return "Tokens reduced"
        if self.saved == 0:
            return "No token reduction"
        return "Optimization INCREASED tokens"


def run_optimization(prompt: str, method: str, target_provider=None, target_model: str = "",
                     optimizer_provider=None, optimizer_model: str = "") -> OptimizationRun:
    res = op.optimize(prompt, method, optimizer_provider, optimizer_model)
    return OptimizationRun(res, tc.count_tokens(prompt, target_model, target_provider),
                           tc.count_tokens(res.optimized, target_model, target_provider))


@dataclass
class ComparisonRun:
    resp_original: str
    resp_optimized: str
    api_in_original: Optional[int]
    api_in_optimized: Optional[int]
    api_out_original: Optional[int]
    api_out_optimized: Optional[int]
    evaluation: ev.EvaluationResult
    judge_usage: Optional[tuple]
    costs: dict


def run_comparison(run: OptimizationRun, provider, model: str, temperature: float, max_tokens: int,
                   target_pricing: cc.Pricing, use_embeddings: bool = True,
                   judge_provider=None, judge_model: str = "",
                   optimizer_pricing: Optional[cc.Pricing] = None,
                   judge_pricing: Optional[cc.Pricing] = None, seed: int = 42) -> ComparisonRun:
    """Same model + identical settings for both prompts."""
    kw = dict(temperature=temperature, max_tokens=max_tokens, seed=seed)
    r1 = provider.generate(run.result.original, model, **kw)
    r2 = provider.generate(run.result.optimized, model, **kw)

    judge, judge_usage = None, None
    if judge_provider and judge_model:
        judge, judge_usage = ev.llm_judge(judge_provider, judge_model, run.result.original, r1.text, r2.text)

    evaluation = ev.evaluate(run.result.original, r1.text, r2.text, use_embeddings, judge)

    # prefer API-reported input tokens (what is actually billed) for target-model cost
    in_o = r1.input_tokens if r1.input_tokens is not None else run.orig_tokens.count
    in_p = r2.input_tokens if r2.input_tokens is not None else run.opt_tokens.count
    opt_usage = None
    if run.result.optimizer_usage:
        i, o, _ = run.result.optimizer_usage
        opt_usage = (i, o)
    costs = cc.build_cost_report(in_o, in_p, target_pricing, r1.output_tokens, r2.output_tokens,
                                 opt_usage, optimizer_pricing, judge_usage[:2] if judge_usage else None, judge_pricing)
    return ComparisonRun(r1.text, r2.text, r1.input_tokens, r2.input_tokens, r1.output_tokens, r2.output_tokens,
                         evaluation, judge_usage, costs)
