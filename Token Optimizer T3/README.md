# LLM Token Optimizer

Compresses prompts, measures **actual** token counts, sends original vs. optimized prompts to the same model with identical settings, and evaluates whether response quality survived. Rule-based mode works fully offline.

## Install
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # fill only what you use
streamlit run app.py
```
Optional: `pip install sentence-transformers` for embedding-based similarity (otherwise a weaker lexical cosine is used and labelled as such).

## Providers
| Provider | Setup |
|---|---|
| Ollama (local, free) | `ollama serve` + `ollama pull llama3.1`; optional `OLLAMA_HOST` |
| OpenAI / Groq / Gemini | set `OPENAI_API_KEY` / `GROQ_API_KEY` / `GEMINI_API_KEY` in `.env` |
| Any OpenAI-compatible endpoint | `OPENAI_BASE_URL` + `OPENAI_API_KEY`, provider `openai-compatible` |

Keys are read from the environment only and never shown or logged. Not every provider is free; check yours.

## Token counting (priority order)
1. Ollama: model-native count (`prompt_eval_count`) - exact.
2. OpenAI model names: `tiktoken` for that model - exact.
3. Other models: tiktoken `o200k_base` - labelled **approximation**.
4. No tokenizer (e.g. offline): heuristic - labelled **estimate**.

## Optimization methods
- **rule-based**: filler removal (A), repeated-instruction merging (B), verbose-phrase simplification (C), constraint preservation (D), duplicate/redundant sentence removal (E), compact structured prompts (F). Every aggressive rewrite is checked against "critical tokens" (numbers, quoted text, negations, formats, languages, proper nouns); if one would be dropped, the rewrite is refused. Text after "the following text:" / `Text:` is user data and never touched.
- **llm**: an LLM rewrites the prompt (G). Its usage/cost is reported separately; output is checked for dropped constraints.
- **hybrid**: rules first, then LLM.

## Evaluation (automated, not a guarantee)
Semantic similarity + rule-checked requirements from the original prompt (word/sentence/bullet limits, JSON, table, Python code, forbidden/required phrases) + optional LLM judge. Similarity alone never decides the verdict; a violated requirement or a judge "not equivalent" overrides it.

## Costs
Enter your own per-1M-token prices (nothing is hardcoded). Reports target input cost (original/optimized/savings), optimizer cost, evaluation cost and net savings. Input savings do not guarantee lower total cost.

## Tests
```bash
python run_tests.py                                   # offline: token + optimization results
python run_tests.py --provider ollama --model llama3.1 --input-price 0.1 --output-price 0.4
python run_tests.py --mock                            # pipeline smoke test with a FAKE model
```
Writes `test_results.md`. Includes five categories, a refusal case (multiple constraints) and a no-reduction case.

## Layout
`app.py` UI | `pipeline.py` orchestration | `optimizer.py` | `token_counter.py` | `llm_provider.py` | `evaluator.py` | `cost_calculator.py` | `sample_prompts.py` | `run_tests.py`

## Limitations
Rules are English-only and heuristic. Semantic equivalence cannot be guaranteed. Always review the optimized prompt for important tasks.
