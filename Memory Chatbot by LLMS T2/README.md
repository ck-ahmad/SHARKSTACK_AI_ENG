# Prompt Lab Chat (FastAPI + vanilla JS)

Chatbot with switchable providers (Ollama / Groq / Gemini), editable system prompt,
temperature and max-token controls, streaming responses.

## Setup (Ubuntu)
```bash
python3 --version                      # 3.10+
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
ollama run llama3.1:8b "say hi"        # verify the model works, then /bye

cp .env.example .env                   # optional: add GROQ_API_KEY / GEMINI_API_KEY
uvicorn main:app --reload
```
Open http://localhost:8000

## API keys (optional)
- Groq: console.groq.com -> API Keys
- Gemini: aistudio.google.com -> Get API key
Check current free-tier limits and model names before relying on them.

## Parameter mapping
| Provider | Temperature | Token limit |
|---|---|---|
| Ollama | options.temperature | options.num_predict |
| Groq | temperature | max_completion_tokens |
| Gemini | generationConfig.temperature | generationConfig.maxOutputTokens |

Temperature: 0-0.3 focused, 0.4-0.7 balanced, 0.8-1.2 creative, 1.3-2 unpredictable.
Max tokens: caps reply length only, not the context window.

## Tests
`pytest -q` verifies the payloads carry the chosen temperature and token limit.

## Troubleshooting
- "Can't reach Ollama": `ollama serve` (or `systemctl status ollama`)
- "Model not found": `ollama pull <model>`
- Out of memory: smaller model (e.g. llama3.2:3b) or lower max tokens
- 401/429 from online providers: recheck key / wait for quota reset
- Port busy: `uvicorn main:app --port 8001`
