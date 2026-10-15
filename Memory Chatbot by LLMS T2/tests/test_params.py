"""Run: pytest -q   (no network needed)"""
import providers as p

H = [{"role": "user", "content": "hi"}]


def test_ollama_params():
    d = p.build_ollama("llama3.1:8b", "sys", H, 1.3, 256)
    assert d["options"] == {"temperature": 1.3, "num_predict": 256}


def test_groq_params():
    d = p.build_groq("m", "sys", H, 0.2, 1024)
    assert d["temperature"] == 0.2 and d["max_completion_tokens"] == 1024


def test_gemini_params():
    d = p.build_gemini("m", "sys", H, 0.9, 128)
    assert d["generationConfig"] == {"temperature": 0.9, "maxOutputTokens": 128}


def test_trim_keeps_latest():
    hist = [{"role": "user", "content": "x" * 8000}] * 3
    assert len(p.trim_history(hist, 12000)) == 1 or len(p.trim_history(hist, 12000)) == 2
    assert p.trim_history(hist, 12000)[-1] is hist[-1]
