# Log

Weekly progress notes.

## Week 1

- Created the repo.
- Mistral (Experiment plan) and Gemini (free tier) keys working: `scripts/smoke_test.py` passes.

### Tue: τ²-bench paper notes

Sources: [τ²-bench, Barres et al. 2025 (arXiv 2506.07982)](https://arxiv.org/abs/2506.07982), [τ-bench, Yao et al. 2024 (arXiv 2406.12045)](https://arxiv.org/abs/2406.12045), [`evaluator.py`](https://github.com/sierra-research/tau2-bench/blob/main/src/tau2/evaluator/evaluator.py) on `main`.

**Dual control.** τ²-bench models a conversation as a Dec-POMDP with two players, agent and user. Each has its own tools and its own database: in telecom the agent sees the CRM (customers, lines, plans) and the user holds a mocked phone (airplane mode, signal, data toggle). Only one player acts per turn; an action is either a tool call or a message to the other player. A global reward R(state) in [0, 1] is computed from the final state (both databases plus the message history).

- Only **telecom** is dual-control (15 read + 15 write user tools). **Airline (50 tasks) and retail (115 tasks) have no user tools**: there the user only talks, as in the original τ-bench.
- Ablation modes in telecom: *Default* (dual control), *No-User* (agent gets a ticket and runs every tool itself), *Oracle Plan* (agent gets the exact tool sequence). Default vs No-User costs about 18-25 points of pass^1, so coordinating a user is a separate failure source from reasoning.
- Telecom tasks are composed from atomic subtasks (init calls, solution calls, assertion calls). 2,285 combinations, 114 sampled. Difficulty scales with number of subtasks and actions: pass^1 near zero above 7 actions in Default mode.

**User simulator.** An LLM (gpt-4.1 in the paper) with generic guidelines, a hidden task-specific instruction (identity, intent, preferences), an optional persona (None / Easy / Hard), and in telecom its own tools. Tools return only human-readable output and the user acts only when the agent asks, which keeps it from solving the task alone ("complexity asymmetry").

- Human-annotated **user simulator error rates: airline 47% (13% critical), retail 40% (12% critical), telecom 16% (6% critical).** A critical error is one that stops the agent from solving the task. So on airline, roughly 1 run in 8 can fail because of the user, not the agent.
- Persona matters: Easy beats Hard; *no persona* is on par with or worse than Hard.

**Success per task.** Reward is binary in practice: the product of the checks listed in the task's `reward_basis`:

| Check | Passes when |
| --- | --- |
| `DB` | Final database equals the ground-truth database (replay of the gold write actions). Read calls and conversation wording can vary freely. |
| `ENV_ASSERTION` | Assertion functions on the final world state hold (e.g. service connected). Telecom uses only this. |
| `ACTION` | Every gold solution call appears in the trajectory. |
| `COMMUNICATE` | Agent's messages to the user contain every required info string (e.g. "54.04"). |
| `NL_ASSERTION` | An LLM judge confirms a natural-language condition on the history ("agent diagnosed the cause"). |

- A run that ends any way other than `AGENT_STOP` or `USER_STOP` (max steps, errors) scores **0** before any check runs.
- reward = 1 is necessary, not sufficient: τ-bench notes an agent can reach the right DB state while breaking policy (e.g. acting without explicit user confirmation). Policy violations are **not** scored directly.

**pass^k.** Probability that all k i.i.d. trials of a task succeed, averaged over tasks. With n trials and c successes per task, the unbiased estimate is

pass^k = E_task[ C(c, k) / C(n, k) ]

pass^1 = mean reward. It falls fast with k: gpt-4o retail pass^1 > 60% but pass^8 < 25% (τ-bench). Paper setup: 4 trials per task, temperature 0, LiteLLM, about $40 per full pass of all domains with gpt-4.1.

**What this means for agent-envelope**

1. The plan's "success ≥ 90%" maps to mean reward (pass^1) over seeds in a scenario cell. Report pass^k too, since the envelope is about reliability.
2. "Policy violation ≤ 2%" has **no built-in metric**. We need our own violation detector (rule checks on the trajectory, or an LLM judge). Decide in week 2.
3. The working set is airline, which is single-control and has the noisiest user simulator (47% errors). Our user is Gemini Flash-Lite, likely noisier than gpt-4.1. Before blaming the agent for a failure, tag user-caused failures; add "user simulator error" to the failure taxonomy on Friday.
4. Premature termination scores 0. Injecting tool failures could push runs into max-steps and inflate failure rates; log `termination_reason` separately from reward.
5. Open question: switch the working set to telecom for real dual control and the cleaner user sim, or stay on airline for simpler tasks? Check run time per task on Thursday before deciding.

### Wed: τ²-bench running

- Cloned to `../tau2-bench`, pinned to `v2.0.0`. `uv sync`, `tau2 intro`, then one mock task: `create_task_1`, agent `mistral/ministral-8b-latest`, user `gemini/gemini-flash-lite-latest`.
- Result: reward 1.0 (basis `DB` + `COMMUNICATE`), `user_stop`, 3.8 s, 6 messages, 2 tool calls (`get_users`, `create_task`). Viewed with `tau2 view`.
- LiteLLM cost tracking is useless for us: it prices Gemini at paid rates although we are on the free tier, and has no price for Ministral (`agent_cost: None`). Count calls and tokens ourselves.
- Pitfall: the Claude desktop app sandboxes `AppData\Roaming`, so `pip install --user` run from Claude's shell is invisible to your own terminal. Install Python tools from your own terminal.

### Thu: airline throughput

5 airline tasks, agent `mistral/ministral-8b-latest`, user `gemini/gemini-flash-lite-latest`, 1 trial, concurrency 1 (`data/simulations/airline-throughput`).

| Task | Reward | Seconds | Agent calls | User calls | Tool calls | Agent tokens | User tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 (DB mismatch) | 17.9 | 7 | 4 | 3 | 33,230 | 3,554 |
| 1 | 0 (DB mismatch) | 26.5 | 14 | 7 | 7 | 85,428 | 8,404 |
| 2 | 0 (DB mismatch) | 17.6 | 8 | 5 | 3 | 41,133 | 6,674 |
| 3 | crashed in scoring | - | - | - | - | - | - |
| 4 | 1 | 11.8 | 10 | 4 | 6 | 51,006 | 3,701 |

- Per completed run: **18.5 s, 14.8 LLM calls (10 agent, 5 user), about 53k agent tokens and 5.6k user tokens.** The agent re-sends the whole policy and history every turn, so agent tokens dominate.
- At concurrency 1: about 195 runs per hour. Sunday's baseline (20 tasks × 3 seeds = 60 runs) is about 20 minutes, 3.2M agent tokens, 300 Gemini calls.
- pass^1 on 4 scored tasks: 1/4. Ministral 8B is weak on airline, which leaves room for the envelope to move.
- Task 3 crashed: τ²-bench v2.0.0 scores `COMMUNICATE` with a semantic LLM judge, `gpt-5.5` by default, and we have no OpenAI key. Tasks with no required info skip the judge, which is why 0, 1, 2 and 4 scored.
