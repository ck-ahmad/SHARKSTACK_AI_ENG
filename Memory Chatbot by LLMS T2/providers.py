"""Provider layer: builds the right payload per provider and streams tokens back."""
import json
import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse"


class ProviderError(Exception):
    """Message is safe to show to the user."""


def default_model(provider: str) -> str:
    return {
        "ollama": "llama3.1:latest",
        "groq": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    }[provider]


def api_key(provider: str) -> str:
    return os.getenv({"groq": "GROQ_API_KEY", "gemini": "GEMINI_API_KEY"}.get(provider, ""), "")


# ---- payload builders: each provider names the token limit differently ----
def build_ollama(model, system, history, temperature, max_tokens):
    msgs = [{"role": "system", "content": system}] + history
    return {"model": model, "messages": msgs, "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens}}


def build_groq(model, system, history, temperature, max_tokens):
    msgs = [{"role": "system", "content": system}] + history
    return {"model": model, "messages": msgs, "stream": True,
            "temperature": temperature, "max_completion_tokens": max_tokens}


def build_gemini(model, system, history, temperature, max_tokens):
    contents = [{"role": "model" if m["role"] == "assistant" else "user",
                 "parts": [{"text": m["content"]}]} for m in history]
    return {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}


BUILDERS = {"ollama": build_ollama, "groq": build_groq, "gemini": build_gemini}


def trim_history(history, max_chars=12000):
    """Keep the most recent messages that fit a rough character budget (~3k tokens)."""
    kept, total = [], 0
    for m in reversed(history):
        total += len(m["content"])
        if total > max_chars and kept:
            break
        kept.append(m)
    return list(reversed(kept))


def explain(provider, status, body):
    low = body.lower()
    if provider == "ollama":
        if status == 404:
            return "Model not found locally. Run: ollama pull <model-name>"
        if "memory" in low:
            return "Ollama ran out of memory. Try a smaller model or lower max tokens."
    if status in (401, 403):
        return f"{provider.title()} rejected the API key. Check it in your .env file."
    if status == 429:
        return f"{provider.title()} rate limit or free quota reached. Wait a bit or switch provider."
    if status == 404:
        return f"Model unavailable on {provider.title()}. Pick another model name."
    return f"{provider.title()} error ({status}): {body[:200]}"


async def stream_chat(provider, model, system, history, temperature, max_tokens):
    """Async generator yielding ('token', text) then ('end', truncated_bool)."""
    if provider not in BUILDERS:
        raise ProviderError(f"Unknown provider: {provider}")
    key = api_key(provider)
    if provider != "ollama" and not key:
        raise ProviderError(f"{provider.title()} API key missing. Add it to .env or switch to Ollama.")

    payload = BUILDERS[provider](model, system, trim_history(history), temperature, max_tokens)
    headers = {}
    if provider == "ollama":
        url = f"{OLLAMA_URL}/api/chat"
    elif provider == "groq":
        url, headers = GROQ_URL, {"Authorization": f"Bearer {key}"}
    else:
        url, headers = GEMINI_URL.format(model=model), {"x-goog-api-key": key}

    truncated = False
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(None, connect=10)) as c:
            async with c.stream("POST", url, json=payload, headers=headers) as r:
                if r.status_code >= 400:
                    raise ProviderError(explain(provider, r.status_code, (await r.aread()).decode(errors="ignore")))
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    if provider != "ollama":
                        if not line.startswith("data:"):
                            continue
                        line = line[5:].strip()
                        if line == "[DONE]":
                            break
                    obj = json.loads(line)
                    if provider == "ollama":
                        tok = obj.get("message", {}).get("content", "")
                        if obj.get("done"):
                            truncated = obj.get("done_reason") == "length"
                    elif provider == "groq":
                        ch = (obj.get("choices") or [{}])[0]
                        tok = ch.get("delta", {}).get("content") or ""
                        if ch.get("finish_reason") == "length":
                            truncated = True
                    else:
                        ch = (obj.get("candidates") or [{}])[0]
                        tok = "".join(p.get("text", "") for p in ch.get("content", {}).get("parts", []))
                        if ch.get("finishReason") == "MAX_TOKENS":
                            truncated = True
                    if tok:
                        yield "token", tok
    except httpx.ConnectError:
        if provider == "ollama":
            raise ProviderError("Can't reach Ollama. Start it with: ollama serve")
        raise ProviderError("Network error. Check your internet connection.")
    except httpx.TimeoutException:
        raise ProviderError("Request timed out.")
    yield "end", truncated


async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            return {"running": True, "models": [m["name"] for m in r.json().get("models", [])]}
    except Exception:
        return {"running": False, "models": []}
