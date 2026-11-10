# Integrate AURA into Antigravity or another project

Repository: https://github.com/airushi18/aura

## Instructions for your AI coding agent

> Integrate AURA as a **separate Python service/library**, not MCP. Clone
> `https://github.com/airushi18/aura.git`, inspect `README.md`,
> `AGENT_INSTRUCTIONS.md` and `pyproject.toml`, create an isolated Python
> environment, and run the test suite. Configure the existing compatible model
> endpoint via environment variables. Do not edit or replace the existing video
> engine. Integrate with AURA through its `aura` CLI, Python `CreativeAgent`
> class, or JSON HTTP API. For every creative brief: evaluate → revise if
> required → reevaluate → produce a structured quality report. Route unresolved
> critical flags to human review, cap revision attempts, and do not auto-publish
> without authorization. Report actual tests and any model configuration gaps.

## Repository layout

- `creative_intelligence/` → Python engine, model connector, scoring rubric, CLI, HTTP server, metrics ledger
- `tests/` → automated unit tests
- `examples/` → input payloads
- `AGENT_INSTRUCTIONS.md` → portable creative decision rules
- `.github/workflows/` → CI tests
- `pyproject.toml` → one-command installation

## Integration options

1. **Direct Python library:** `from creative_intelligence import CreativeAgent`
2. **Subprocess/CLI:** run `aura evaluate --file brief.json --output audit.json`
3. **HTTP:** send JSON to `http://127.0.0.1:8765/evaluate` after `aura serve`

Use the option supported by your environment. No MCP server, adapter, or plugin is necessary.

## Production safeguards

- Never send secrets in creative briefs or commit `.env` files.
- If an evaluation fails, mark the job failed instead of approving by default.
- Treat `PASS` as an editorial gate, not a legal, factual, or performance guarantee.
- Identify each job, cap retries, and log publication outcomes in the parent workflow.
