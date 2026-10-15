"""FastAPI app: /api/status, /api/chat (SSE stream), and the static frontend."""
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import providers

app = FastAPI(title="Prompt Engineering Chatbot")
STATIC = Path(__file__).parent / "static"

DEFAULT_SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant.
Instructions:
1. Provide accurate and relevant answers.
2. Explain technical concepts in beginner-friendly language.
3. Use examples when they improve understanding.
4. Keep responses concise unless the user requests detail.
5. If you are uncertain, clearly acknowledge the uncertainty.
6. Follow the user's requested response format."""

PRESETS = {
    "General assistant": DEFAULT_SYSTEM_PROMPT,
    "Python tutor": "You are a patient Python tutor. Explain step by step, show short runnable examples, and end with one practice exercise.",
    "Data science assistant": "You are a data science assistant. Prefer pandas/scikit-learn examples, explain statistical reasoning plainly, and flag common pitfalls.",
    "Interview prep": "You are a technical interview coach. Ask one question at a time, wait for the answer, then give brief feedback and a better answer.",
}


class Msg(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    provider: str
    model: str
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    messages: list[Msg]
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=16, le=8192)


@app.get("/api/status")
async def status():
    return {
        "ollama": await providers.ollama_status(),
        "groq": {"configured": bool(providers.api_key("groq"))},
        "gemini": {"configured": bool(providers.api_key("gemini"))},
        "defaults": {p: providers.default_model(p) for p in ("ollama", "groq", "gemini")},
        "presets": PRESETS,
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    history = [m.model_dump() for m in req.messages if m.content.strip()]

    async def events():
        if not history:
            yield sse({"t": "error", "v": "Message is empty."})
            return
        try:
            async for kind, val in providers.stream_chat(
                req.provider, req.model, req.system_prompt, history, req.temperature, req.max_tokens
            ):
                yield sse({"t": "token", "v": val} if kind == "token" else {"t": "done", "truncated": val})
        except providers.ProviderError as e:
            yield sse({"t": "error", "v": str(e)})
        except Exception as e:  # last-resort guard so the UI never hangs
            yield sse({"t": "error", "v": f"Unexpected error: {e}"})

    return StreamingResponse(events(), media_type="text/event-stream")


def sse(obj):
    return f"data: {json.dumps(obj)}\n\n"


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
