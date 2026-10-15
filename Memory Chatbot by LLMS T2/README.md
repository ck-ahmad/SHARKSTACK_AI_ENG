<div align="center">

# 🧪 Prompt Lab Chat

**Switch LLM providers, tweak the system prompt, tune temperature, and watch tokens stream in.**

![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-black)
![Groq](https://img.shields.io/badge/Groq-cloud-F55036)
![Gemini](https://img.shields.io/badge/Gemini-cloud-4285F4?logo=google&logoColor=white)

</div>

---

## ✨ Features

- 🔀 **Switchable providers**: Ollama (local), Groq, Gemini
- 📝 **Editable system prompt** with presets
- 🌡️ **Temperature + max-token controls**
- ⚡ **Streaming responses**, token by token
- 🧠 **Auto history trimming** to stay within a character budget

---

## 🚀 Quick Start (Ubuntu)

```bash
# 1. Check Python
python3 --version                  # 3.10+

# 2. Create venv + install deps
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Install Ollama and pull a model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
ollama run llama3.1 "say hi"       # verify it works, then /bye

# 4. Configure env
cp .env.example .env

# 5. Run
uvicorn main:app --reload
```

Open **http://localhost:8000** 🎉

---

## 🔐 Configuration (`.env`)

```env
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:latest

GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

> ⚠️ `OLLAMA_URL` must be a URL, not a model name. Keys are optional; Ollama works without any.

| Provider | Get a key |
|---|---|
| Groq | [console.groq.com](https://console.groq.com) → API Keys |
| Gemini | [aistudio.google.com](https://aistudio.google.com) → Get API key |

Check current free-tier limits and model names before relying on them.

---

## 🎛️ Parameter Mapping

| Provider | Temperature | Token limit |
|---|---|---|
| **Ollama** | `options.temperature` | `options.num_predict` |
| **Groq** | `temperature` | `max_completion_tokens` |
| **Gemini** | `generationConfig.temperature` | `generationConfig.maxOutputTokens` |

**Temperature guide**

| Range | Feel |
|---|---|
| 0 – 0.3 | 🎯 Focused |
| 0.4 – 0.7 | ⚖️ Balanced |
| 0.8 – 1.2 | 🎨 Creative |
| 1.3 – 2 | 🌀 Unpredictable |

> Max tokens caps **reply length only**, not the context window.

---

## 🧪 Tests

```bash
pytest -q
```

Verifies payloads carry the chosen temperature and token limit.

---

## 🛠️ Troubleshooting

<details>
<summary><b>"Can't reach Ollama" / "Ollama not running"</b></summary>

- Check it's up: `curl http://127.0.0.1:11434/api/tags`
- Start it: `ollama serve` (or `systemctl status ollama`)
- "Address already in use" means it's already running, so skip `serve`
- Check `OLLAMA_URL` in `.env`: `python -c "from providers import OLLAMA_URL; print(repr(OLLAMA_URL))"`
- Restart the server after editing `.env`
- If `echo $OLLAMA_URL` prints something, `unset OLLAMA_URL` (shell vars override `.env`)

</details>

<details>
<summary><b>"Model not found"</b></summary>

`ollama pull <model>` and check with `ollama list`.

</details>

<details>
<summary><b>Out of memory</b></summary>

Use a smaller model (e.g. `llama3.2:3b`) or lower max tokens.

</details>

<details>
<summary><b>401 / 429 from online providers</b></summary>

Recheck your API key, or wait for the quota to reset.

</details>

<details>
<summary><b>Port busy</b></summary>

`uvicorn main:app --port 8001`

</details>
