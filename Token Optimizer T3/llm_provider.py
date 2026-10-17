"""LLM providers: Ollama (local) and OpenAI-compatible APIs (OpenAI, Groq, Gemini, custom)."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass


class ProviderError(Exception):
    """User-presentable provider error (never contains secrets)."""


@dataclass
class LLMResult:
    text: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    latency_s: float
    model: str


class BaseProvider:
    name = "base"

    def check(self, model: str) -> tuple[bool, str]:
        raise NotImplementedError

    def list_models(self) -> list[str]:
        return []

    def generate(self, prompt: str, model: str, temperature: float = 0.0,
                 max_tokens: int = 512, system: Optional[str] = None, seed: int = 42) -> LLMResult:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, host: Optional[str] = None):
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/").replace("localhost", "127.0.0.1")
        if not self.host.startswith("http"):
            self.host = "http://" + self.host

    def _get(self, path):
        try:
            r = requests.get(self.host + path, timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.ConnectionError:
            raise ProviderError(f"Cannot reach Ollama at {self.host}. Is it running? (`ollama serve`)")
        except requests.RequestException as e:
            raise ProviderError(f"Ollama error: {e}")

    def list_models(self) -> list[str]:
        try:
            return [m["name"] for m in self._get("/api/tags").get("models", [])]
        except ProviderError:
            return []

    def check(self, model: str) -> tuple[bool, str]:
        try:
            models = [m["name"] for m in self._get("/api/tags").get("models", [])]
        except ProviderError as e:
            return False, str(e)
        if not model:
            return False, "No model configured."
        if model not in models and f"{model}:latest" not in models:
            return False, f"Model '{model}' not installed. Run `ollama pull {model}`. Installed: {models or 'none'}"
        return True, "OK"

    def count_tokens(self, text: str, model: str) -> Optional[int]:
        """Model-specific count via prompt_eval_count with raw=True (no chat template)."""
        try:
            r = requests.post(self.host + "/api/generate", timeout=60, json={
                "model": model, "prompt": text, "raw": True, "stream": False,
                "options": {"num_predict": 1, "temperature": 0}})
            r.raise_for_status()
            return r.json().get("prompt_eval_count")
        except requests.RequestException:
            return None

    def generate(self, prompt, model, temperature=0.0, max_tokens=512, system=None, seed=42) -> LLMResult:
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        t0 = time.time()
        try:
            r = requests.post(self.host + "/api/chat", timeout=300, json={
                "model": model, "messages": msgs, "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens, "seed": seed}})
            if r.status_code == 404:
                raise ProviderError(f"Model '{model}' not found in Ollama. Run `ollama pull {model}`.")
            r.raise_for_status()
        except requests.ConnectionError:
            raise ProviderError(f"Cannot reach Ollama at {self.host}.")
        except requests.RequestException as e:
            raise ProviderError(f"Ollama request failed: {e}")
        d = r.json()
        return LLMResult(d.get("message", {}).get("content", "").strip(),
                         d.get("prompt_eval_count"), d.get("eval_count"), time.time() - t0, model)


class OpenAICompatProvider(BaseProvider):
    PRESETS = {
        "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
        "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
        "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
        "openai-compatible": (None, "OPENAI_API_KEY"),  # base URL from OPENAI_BASE_URL
    }

    def __init__(self, name: str):
        if name not in self.PRESETS:
            raise ProviderError(f"Unknown provider '{name}'.")
        self.name = name
        base, self.key_env = self.PRESETS[name]
        self.base_url = (os.getenv("OPENAI_BASE_URL") if name == "openai-compatible" else base) or ""
        self.base_url = self.base_url.rstrip("/")

    def _key(self) -> str:
        key = os.getenv(self.key_env)
        if not key:
            raise ProviderError(f"Missing API key: set {self.key_env} in your environment or .env file.")
        return key

    def check(self, model: str) -> tuple[bool, str]:
        if not self.base_url:
            return False, "Set OPENAI_BASE_URL for the 'openai-compatible' provider."
        if not os.getenv(self.key_env):
            return False, f"Missing API key: set {self.key_env}."
        if not model:
            return False, "No model configured."
        return True, "OK (credentials present; availability is verified on first call)"

    def generate(self, prompt, model, temperature=0.0, max_tokens=512, system=None, seed=42) -> LLMResult:
        ok, msg = self.check(model)
        if not ok:
            raise ProviderError(msg)
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = {"model": model, "messages": msgs, "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
        headers = {"Authorization": f"Bearer {self._key()}", "Content-Type": "application/json"}
        t0 = time.time()
        for attempt in range(2):
            try:
                r = requests.post(self.base_url + "/chat/completions", json=body, headers=headers, timeout=120)
            except requests.RequestException as e:
                raise ProviderError(f"Network error calling {self.name}: {type(e).__name__}")
            if r.status_code == 400 and attempt == 0 and "max_completion_tokens" in r.text:
                body["max_completion_tokens"] = body.pop("max_tokens")
                continue
            break
        if r.status_code == 401:
            raise ProviderError(f"{self.name}: authentication failed (check {self.key_env}).")
        if r.status_code == 404:
            raise ProviderError(f"{self.name}: model '{model}' or endpoint not found.")
        if r.status_code == 429:
            raise ProviderError(f"{self.name}: rate limit or quota exceeded.")
        if not r.ok:
            raise ProviderError(f"{self.name}: HTTP {r.status_code}: {r.text[:300]}")
        d = r.json()
        u = d.get("usage") or {}
        text = (d["choices"][0]["message"].get("content") or "").strip()
        return LLMResult(text, u.get("prompt_tokens"), u.get("completion_tokens"), time.time() - t0, model)


PROVIDER_NAMES = ["ollama", "openai", "groq", "gemini", "openai-compatible"]


def get_provider(name: str) -> BaseProvider:
    return OllamaProvider() if name == "ollama" else OpenAICompatProvider(name)
