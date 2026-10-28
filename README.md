# agent-envelope

An open-source toolkit that maps where an AI agent works, finds where it breaks, and protects it at runtime.

> Status: week 1 of 12. Nothing usable yet.

## Idea

Flight-control verification and validation already knows how to answer "where is this system safe to operate?" agent-envelope applies the same methods to LLM agents.

| Flight control V&V | Agent envelope testing |
| --- | --- |
| Flight conditions (Mach, altitude, weight, CG) | Scenario variables (tool failure rate, user ambiguity, prompt injection, language, context length) |
| Flight envelope | Region where the agent succeeds ≥ 90% and violates policy ≤ 2% |
| Worst-case search | Bayesian optimisation and genetic search for failing scenarios |
| Envelope protection | Runtime monitor that predicts failure and switches to a safe fallback |
| Regression between software standards | Envelope diff between agent versions or models |

The testbed is [τ²-bench](https://github.com/sierra-research/tau2-bench).

## Planned deliverables

1. A pip-installable package with a CLI: `envelope run`, `envelope fit`, `envelope report`
2. An HTML envelope report comparing at least two agents or versions
3. A runtime protection layer with measured failure reduction and its cost
4. A technical report, blog posts and a short demo video

## Development

```bash
uv sync
uv run envelope
```

Progress notes live in [LOG.md](LOG.md); design decisions in [DECISIONS.md](DECISIONS.md).

## License

[MIT](LICENSE)
