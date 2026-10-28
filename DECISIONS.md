# Decisions

Design decisions and the reasons for them, newest first.

## 2026-10-28: Model choices for week 1

- **Agent: `ministral-8b-latest` for now, not Mistral Small.** On the Experiment plan, `mistral-small-latest` and `mistral-small-2603` return 429 on every call, even though the limits page shows 20k tokens/min and 1 req/s. Nemo and Ministral 8B work. Retry Small before the Sunday baseline.
- **User simulator: `gemini-flash-lite-latest`, not `gemini-flash-latest`.** One-line prompt took 98 s on Flash and 0.9 s on Flash-Lite on the free tier. Flash would make overnight runs far too slow.
- **Gemini key lives in a project with no billing linked.** The default project is on prepay with a €0 balance and returns 402.
