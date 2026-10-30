# Decisions

Design decisions and the reasons for them, newest first.

## 2026-10-28: Model choices for week 1

- **Agent: `ministral-8b-latest` for now, not Mistral Small.** On the Experiment plan, `mistral-small-latest` and `mistral-small-2603` return 429 on every call, even though the limits page shows 20k tokens/min and 1 req/s. Nemo and Ministral 8B work. Retry Small before the Sunday baseline.
- **User simulator: `gemini-flash-lite-latest`, not `gemini-flash-latest`.** One-line prompt took 98 s on Flash and 0.9 s on Flash-Lite on the free tier. Flash would make overnight runs far too slow.
- **Gemini key lives in a project with no billing linked.** The default project is on prepay with a €0 balance and returns 402.

## 2026-10-29: Pin τ²-bench to v2.0.0

- Cloned to `../tau2-bench`, checked out tag `v2.0.0` = `989d3285ae669e49503324bdb9981bf14fccedeb` (2026-10-19).
- `main` was 100 commits ahead, but those are voice and leaderboard fixes; the text domains are unaffected. A release tag is easier to cite in the report.
- τ²-bench requires Python `>=3.12,<3.14`. agent-envelope must move from 3.14 to 3.12 before it can import `tau2`.

## 2026-10-30: Score COMMUNICATE with substring matching

- τ²-bench v2.0.0 defaults to a semantic LLM judge (`gpt-5.5`) for the `COMMUNICATE` check. We have no OpenAI key, and a judge adds cost, noise and another model to the measurement.
- Use `--communicate-scorer substring`, the original τ-bench rule: each required string must appear in the agent's messages. Free and deterministic. Airline tasks are English, so formatting mismatches are the main risk; check failures caused only by `COMMUNICATE` by hand.
