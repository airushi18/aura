# AURA | Creative Intelligence Agent

A **standalone, reusable Python repository** for creative evaluation, improvements, concept generation, comparisons, and tracking real post-publication outcomes. **This is not an MCP server.** No MCP setup or external framework is required.

## What is included

- **Creative engine:** `evaluate`, `improve`, `generate`, and `compare`
- **Quality gate:** seven weighted criteria, 0–100 scoring, `PASS`, `REVISE`, `REWORK` and `HUMAN_REVIEW`
- **Visual reviews:** optional up to five images when using a vision-capable model
- **Analytics ledger:** local SQLite records of actual performance metrics (not invented predictions)
- **CLI:** `aura` executable for automation and terminals
- **HTTP API:** basic JSON endpoints for external workflows
- **Python library:** import `CreativeAgent` into your existing projects
- **Universal instructions:** `AGENT_INSTRUCTIONS.md` for compatible AI assistants

## Get the entire code

- Clone: `git clone https://github.com/airushi18/aura.git`
- Or GitHub repository page → **Code → Download ZIP**

No existing application or video generation repository needs modification just to keep AURA as its own service.

## Install

Requires Python 3.11+. Install using either method:

```bash
# Directly from GitHub (after the complete source is pushed)
python -m pip install "git+https://github.com/airushi18/aura.git"

# Or from the cloned repository
python -m pip install .
```

`aura --help` should show the CLI. Standard-library CLI and HTTP modes need **no additional Python dependencies**.

## Configure the model

AURA uses an OpenAI-compatible **chat completions** endpoint for its creative judgment. It does not bundle a model, API key, or free hosted inference. Copy `.env.example` to `.env` in your working directory.

Example using local Ollama (model must be available and running):

```dotenv
CREATIVITY_BASE_URL=http://localhost:11434/v1
CREATIVITY_MODEL=gemma3:4b
CREATIVITY_API_KEY=
```

Or supply a compatible hosted endpoint, model and API key. Do **not** commit `.env`. Note: a ChatGPT subscription does not automatically include API credits.

## Run it

```bash
aura evaluate --file examples/vox_reel.json --output audit.json
aura improve --file examples/car_ad.json --output improved.json
aura generate --file examples/car_ad.json --output concept.json
aura compare --file examples/compare.json --output comparison.json
aura track --file examples/track.json --db performance.sqlite
aura insights --db performance.sqlite
```

A brief is JSON. Example:

```json
{
  "medium": "reel",
  "platform": "Instagram",
  "goal": "Increase completion rate",
  "audience": "International family audience",
  "brand_guidelines": "Clear action, original stories",
  "constraints": ["9:16", "under 40 seconds"],
  "content": "The storyboard or script to assess"
}
```

For image review: `aura evaluate --file examples/car_ad.json --image path/to/poster.png` (vision-enabled model required). For video: supply the transcript, storyboard, timings, and/or extracted frames. AURA does **not** decode videos or publish media.

## Python integration

```python
from creative_intelligence import CreativeAgent

agent = CreativeAgent()
result = agent.evaluate({
    "medium": "caption",
    "goal": "Qualified leads",
    "audience": "Premium car owners",
    "content": "Protect your investment with premium detailing."
})
print(result["score"], result["decision"])
```

### HTTP automation integration

```bash
aura serve --host 127.0.0.1 --port 8765
curl -X POST http://127.0.0.1:8765/evaluate \
  -H "Content-Type: application/json" \
  -d '{"medium":"caption","goal":"More inquiries","content":"Experience premium detailing."}'
```

Available routes: `GET /health`, `GET /insights`, `POST /evaluate`, `/improve`, `/generate`, `/compare`, `/track`, `/insights`. Bind on localhost by default. If exposed beyond localhost, set `CREATIVITY_SERVER_TOKEN` and use an HTTPS gateway, access controls and rate limiting. This sample server is not a hardened internet service.

## Quality and safety notes

- Creative scores are **editorial heuristics**, not a guarantee of views, sales or conversion.
- Facts and trends are **not externally verified**. `needs_verification` lists gaps.
- Critical unresolved flags result in `HUMAN_REVIEW`.
- The caller decides how to apply the gate; content is not published automatically.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use a simulated AI model, so they run without credentials. GitHub Actions also tests the code across supported Python versions. Live model performance still needs a configured endpoint.

## Antigravity and other orchestrators

See [INTEGRATION.md](INTEGRATION.md) for instructions. Antigravity can clone the repo, install `aura`, run it as a subprocess, import it as a library, or connect to its HTTP API. **No MCP is required.**

## License

MIT, see [LICENSE](LICENSE).
