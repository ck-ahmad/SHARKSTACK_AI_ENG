"""Cost estimation. Prices are always user-configured; nothing is hardcoded."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

COST_CAVEAT = (
    "Input-token savings do not guarantee lower total cost: output length, optimizer and "
    "evaluator API calls, prompt caching and provider-specific billing can all change the result. "
    "All figures are estimates based on the prices you entered."
)


@dataclass
class Pricing:
    input_per_m: Optional[float] = None   # USD per 1M input tokens
    output_per_m: Optional[float] = None  # USD per 1M output tokens

    @property
    def configured(self) -> bool:
        return self.input_per_m is not None


def input_cost(tokens: Optional[int], pricing: Pricing) -> Optional[float]:
    if tokens is None or pricing.input_per_m is None:
        return None
    return tokens / 1_000_000 * pricing.input_per_m


def output_cost(tokens: Optional[int], pricing: Pricing) -> Optional[float]:
    if tokens is None or pricing.output_per_m is None:
        return None
    return tokens / 1_000_000 * pricing.output_per_m


def call_cost(input_tokens: Optional[int], output_tokens: Optional[int], pricing: Pricing) -> Optional[float]:
    parts = [input_cost(input_tokens, pricing), output_cost(output_tokens, pricing)]
    parts = [p for p in parts if p is not None]
    return sum(parts) if parts else None


def build_cost_report(orig_in: int, opt_in: int, target: Pricing,
                      orig_out: Optional[int] = None, opt_out: Optional[int] = None,
                      optimizer_usage: Optional[tuple] = None, optimizer_pricing: Optional[Pricing] = None,
                      eval_usage: Optional[tuple] = None, eval_pricing: Optional[Pricing] = None) -> dict:
    """Returns the six required lines (+ output delta). None means 'not computable / not configured'."""
    c_orig = input_cost(orig_in, target)
    c_opt = input_cost(opt_in, target)
    saving = None if c_orig is None or c_opt is None else c_orig - c_opt

    out_delta = None  # positive = optimized response was cheaper
    if orig_out is not None and opt_out is not None:
        o1, o2 = output_cost(orig_out, target), output_cost(opt_out, target)
        if o1 is not None and o2 is not None:
            out_delta = o1 - o2

    opt_api = call_cost(*optimizer_usage, optimizer_pricing) if optimizer_usage and optimizer_pricing else (0.0 if not optimizer_usage else None)
    eval_api = call_cost(*eval_usage, eval_pricing) if eval_usage and eval_pricing else (0.0 if not eval_usage else None)

    net = None
    if saving is not None and opt_api is not None and eval_api is not None:
        net = saving + (out_delta or 0.0) - opt_api - eval_api

    return {
        "original_input_cost": c_orig,
        "optimized_input_cost": c_opt,
        "input_cost_savings": saving,
        "output_cost_difference": out_delta,
        "optimization_api_cost": opt_api,
        "evaluation_api_cost": eval_api,
        "net_savings": net,
        "caveat": COST_CAVEAT,
    }


def fmt_money(x: Optional[float]) -> str:
    if x is None:
        return "N/A (pricing not configured)"
    return f"${x:.8f}" if abs(x) < 0.01 else f"${x:.4f}"
