# Test results (2026-10-17 08:54)

- Target provider/model: none (offline) / -
- Pricing configured: no

## Final demo: Python explanation  (Simple Q&A)

**Original prompt**
```
Can you please explain what Python programming is in simple terms that are easy for a complete beginner to understand? Please keep the explanation short and avoid unnecessary details.
```
**Optimized prompt**
```
Explain Python programming in complete beginner-friendly language. Answer concisely without unnecessary details.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~42 (estimate) -> optimized ~22 (estimate)
- Saved: 20 tokens (47.6%)  | status: Tokens reduced
- Techniques: A. Redundant words/filler removed, B. Repeated instructions merged, C. Verbose instructions simplified
- Essential info preserved: 100% of critical tokens
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Q&A: machine learning  (Simple Q&A)

**Original prompt**
```
Can you please provide me with a brief explanation of what machine learning is?
```
**Optimized prompt**
```
Briefly explain machine learning.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~19 (estimate) -> optimized ~7 (estimate)
- Saved: 12 tokens (63.2%)  | status: Tokens reduced
- Techniques: A. Redundant words/filler removed, C. Verbose instructions simplified
- Essential info preserved: 100% of critical tokens
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Python: sum of two numbers  (Python programming)

**Original prompt**
```
Write a Python program. The program should take two numbers as input. It should calculate their sum and display the result.
```
**Optimized prompt**
```
Write a Python program that inputs two numbers, calculates their sum and displays the result.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~29 (estimate) -> optimized ~22 (estimate)
- Saved: 7 tokens (24.1%)  | status: Tokens reduced
- Techniques: F. Structured prompt compacted
- Essential info preserved: 100% of critical tokens
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Summarization  (Summarization)

**Original prompt**
```
Hello! I hope you are doing well. Could you please provide me with a brief summary of the following text? I would really appreciate it if you could keep the summary short.

Text: Photosynthesis is the process by which green plants, algae and some bacteria convert light energy into chemical energy. Using chlorophyll, they absorb sunlight and use it to turn carbon dioxide and water into glucose and oxygen. The glucose fuels growth, while the oxygen is released into the atmosphere.
```
**Optimized prompt**
```
Briefly summarize the following text. Keep the summary short.

Text: Photosynthesis is the process by which green plants, algae and some bacteria convert light energy into chemical energy. Using chlorophyll, they absorb sunlight and use it to turn carbon dioxide and water into glucose and oxygen. The glucose fuels growth, while the oxygen is released into the atmosphere.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~114 (estimate) -> optimized ~85 (estimate)
- Saved: 29 tokens (25.4%)  | status: Tokens reduced
- Techniques: A. Redundant words/filler removed, C. Verbose instructions simplified
- Essential info preserved: 100% of critical tokens
- Note: Detected user-provided data block: left untouched.
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Data analysis (pandas)  (Data analysis)

**Original prompt**
```
I have a CSV file with the columns date, region, units and revenue. Could you please tell me how to use pandas in order to calculate the total revenue per region for 2024 and then sort the results in descending order? Please show the code and keep the explanation short.
```
**Optimized prompt**
```
I have a CSV file with the columns date, region, units and revenue. Tell me how to use pandas to calculate the total revenue per region for 2024 and then sort the results in descending order. Show the code and keep the explanation short.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~67 (estimate) -> optimized ~59 (estimate)
- Saved: 8 tokens (11.9%)  | status: Tokens reduced
- Techniques: A. Redundant words/filler removed, C. Verbose instructions simplified
- Essential info preserved: 100% of critical tokens
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Multiple constraints (optimizer must refuse to cut)  (Multiple constraints)

**Original prompt**
```
Please write a product description for a stainless steel water bottle. It must be under 60 words. Do not mention price. Never use the word "cheap". Use a friendly tone. Include the phrase "keeps drinks cold for 24 hours".
```
**Optimized prompt**
```
Write a product description for a stainless steel water bottle. It must be under 60 words. Do not mention price. Never use the word "cheap". Use a friendly tone. Include the phrase "keeps drinks cold for 24 hours".
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~54 (estimate) -> optimized ~52 (estimate)
- Saved: 2 tokens (3.7%)  | status: Tokens reduced
- Techniques: A. Redundant words/filler removed, D. Constraints preserved (not rewritten)
- Essential info preserved: 100% of critical tokens
- Constraints kept on purpose: `It must be under 60 words`; `Do not mention price`; `Never use the word "cheap"`
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Repeated instructions  (Repeated instructions)

**Original prompt**
```
Answer briefly. Keep your response short. Do not provide unnecessary details. Make the answer concise.
```
**Optimized prompt**
```
Answer concisely without unnecessary details.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~23 (estimate) -> optimized ~9 (estimate)
- Saved: 14 tokens (60.9%)  | status: Tokens reduced
- Techniques: B. Repeated instructions merged
- Essential info preserved: 100% of critical tokens
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Already minimal (no reduction expected)  (No-reduction case)

**Original prompt**
```
Explain recursion.
```
**Optimized prompt**
```
Explain recursion.
```
- Tokenizer: heuristic estimate (no tokenizer available)
- Tokens: original ~4 (estimate) -> optimized ~4 (estimate)
- Saved: 0 tokens (0.0%)  | status: No token reduction
- Techniques: none
- Essential info preserved: 100% of critical tokens
- Note: No safe optimization found; prompt returned unchanged.
- Responses: not generated (no provider selected; run with --provider to fill this in).

## Summary

| Prompt | Original | Optimized | Saved | % |
|---|---|---|---|---|
| Final demo: Python explanation | 42 | 22 | 20 | 47.6% |
| Q&A: machine learning | 19 | 7 | 12 | 63.2% |
| Python: sum of two numbers | 29 | 22 | 7 | 24.1% |
| Summarization | 114 | 85 | 29 | 25.4% |
| Data analysis (pandas) | 67 | 59 | 8 | 11.9% |
| Multiple constraints (optimizer must refuse to cut) | 54 | 52 | 2 | 3.7% |
| Repeated instructions | 23 | 9 | 14 | 60.9% |
| Already minimal (no reduction expected) | 4 | 4 | 0 | 0.0% |