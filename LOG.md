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
