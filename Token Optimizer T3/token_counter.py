"""Token counting with honest labelling (exact vs. estimate)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

OPENAI_PREFIXES = ("gpt-", "o1", "o3", "o4", "chatgpt", "text-embedding")


@dataclass(frozen=True)
class TokenCount:
    count: int
    exact: bool
    method: str

    @property
    def label(self) -> str:
        return str(self.count) if self.exact else f"~{self.count} (estimate)"


def word_count(text: str) -> int:
    return len(text.split())


def _estimate(text: str) -> int:
    """Heuristic only: average of chars/4 and words*1.33. NOT exact."""
    if not text.strip():
        return 0
    return max(1, round((len(text) / 4 + len(text.split()) * 1.33) / 2))


@lru_cache(maxsize=16)
def _get_encoding(model: str):
    """Return (encoding, is_model_specific) or (None, False) if tiktoken/encodings unavailable."""
    try:
        import tiktoken
    except ImportError:
        return None, False
    try:
        return tiktoken.encoding_for_model(model), True
    except KeyError:
        pass
    except Exception:
        return None, False  # e.g. offline: encoding file cannot be downloaded
    try:
        return tiktoken.get_encoding("o200k_base"), False
    except Exception:
        return None, False


def count_tokens(text: str, model: str = "", provider=None) -> TokenCount:
    """Priority: provider-native count (Ollama) > tiktoken (OpenAI models exact) >
    tiktoken as approximation for other models > heuristic estimate."""
    if not text.strip():
        return TokenCount(0, True, "empty prompt")

    if provider is not None and hasattr(provider, "count_tokens"):
        try:
            n = provider.count_tokens(text, model)
            if n is not None:
                return TokenCount(int(n), True, f"{provider.name} native tokenizer ({model})")
        except Exception:
            pass

    enc, specific = _get_encoding(model or "gpt-4o")
    if enc is not None:
        n = len(enc.encode(text))
        if specific and model.lower().startswith(OPENAI_PREFIXES):
            return TokenCount(n, True, f"tiktoken ({model})")
        return TokenCount(n, False, "tiktoken o200k_base approximation (not this model's own tokenizer)")

    return TokenCount(_estimate(text), False, "heuristic estimate (no tokenizer available)")


def tokens_saved(original: int, optimized: int) -> int:
    return original - optimized


def reduction_pct(original: int, optimized: int) -> float:
    """Negative result = optimization INCREASED tokens. Zero-safe."""
    if original <= 0:
        return 0.0
    return (original - optimized) / original * 100.0
