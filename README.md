# AURA | Creative Intelligence Agent

A reusable, **repository-independent** creative-quality agent. Use it as a prompt in ChatGPT or another AI, as a CLI tool in scripts, via HTTP in automation tools, or as an MCP server in compatible agent hosts.

**Included:** evaluate, improve, generate, compare; seven-category scored quality gate; confidence, risk flags, factual verification gaps; optional image review through a vision-capable model; local SQLite observation ledger for creative experiment metrics.

## Install directly from GitHub (after publishing this repository)

AURA is packaged for source installation, so another project does not need to copy its code.

```bash
python -m pip install "aura-creative-intelligence[mcp] @ git+https://github.com/YOUR_USERNAME/aura-creative-intelligence.git"
```

**Replace `YOUR_USERNAME` with the actual GitHub account or organization after publishing.** For the standard CLI only, omit `[mcp]`. Public repositories are accessible without GitHub authentication; private repositories need an authorized Git credential path.

Then configure a model through environment variables (or a `.env` in the directory from which you run AURA), and execute:

```bash
aura evaluate --file examples/vox_reel.json
# or, for any brief located elsewhere:
aura evaluate --file /absolute/path/to/your-brief.json
```

To launch the MCP server from a GitHub install:

```bash
aura-mcp
```

A generic stdio MCP configuration after installing the optional `[mcp]` extra:

```json
{
  "mcpServers": {
    "aura": {
      "command": "aura-mcp",
      "env": {
        "CREATIVITY_MODEL": "YOUR_MODEL",
        "CREATIVITY_BASE_URL": "https://YOUR_PROVIDER/v1",
        "CREATIVITY_API_KEY": "YOUR_SECRET"
      }
    }
  }
}
```

Keep credentials in the host's secrets manager where available. For hosts that don't resolve `aura-mcp`, use the absolute path to the installed executable or Python environment. MCP requires the selected host to support local stdio servers; remotely hosted environments cannot use your local stdio process without access to it.

### Publish the repository on GitHub

**Option A: using GitHub integration in your AI host.** Connect GitHub, create an empty `aura-creative-intelligence` repo, then commit the tracked files from this package. Do not commit `.env` or API secrets.

**Option B: Windows, one command after Git and GitHub CLI login:**

```powershell
gh auth login
powershell -ExecutionPolicy Bypass -File .\scripts\publish-github.ps1
```

The script creates a **private** GitHub repository by default. To publish publicly, explicitly add `-Visibility public`. The script does nothing unless you execute it yourself. On first use, it commits tracked code and pushes to `main`.

### Repository quality checks

A GitHub Actions workflow runs the fake-provider tests against Python 3.11, 3.12 and 3.13. Passing these checks confirms software-level behavior, **not** real-model creativity or live MCP operation.

---

## 1. The fastest way: no installation

Open `AGENT_INSTRUCTIONS.md`. Copy its contents into the **system/custom instructions** of whichever AI or agent you are using, or attach it to a project and ask that AI to act as AURA. This is the most portable mode and does not require coding or a separate API key beyond what your chosen host offers.

This prompt-only mode is **not** a software service; it depends on the host to supply creative judgment, tool access, state and output.

## 2. Install the executable agent

Requirements: **Python 3.11+**. CLI and HTTP modes use only the Python standard library. MCP mode optionally requires the official MCP Python SDK v2.

**Windows PowerShell:**

```powershell
cd "path\to\creative-intelligence-agent"
Copy-Item .env.example .env
notepad .env
python run.py evaluate --file examples\vox_reel.json --output audit.json
```

**macOS/Linux:**

```bash
cd /path/to/creative-intelligence-agent
cp .env.example .env
# Edit .env with your model connection details.
python3 run.py evaluate --file examples/vox_reel.json --output audit.json
```

You must configure **CREATIVITY_MODEL** and a compatible model connection before the LLM-powered CLI, API or MCP agent can evaluate. You can reuse an existing OpenAI-compatible API or run a local model. The package does not supply or host a model.

### Model provider examples

**Free local inference with Ollama (if your hardware supports the model):**

```bash
ollama pull gemma3:4b
ollama serve
```

Then use the defaults in `.env`:

```dotenv
CREATIVITY_BASE_URL=http://localhost:11434/v1
CREATIVITY_MODEL=gemma3:4b
CREATIVITY_API_KEY=
```

If Ollama is already running, you don't need a second `ollama serve` process. `gemma3:4b` is an example, not an included model. For image review, choose a model/provider that accepts images with OpenAI-style `image_url` fields; some OpenAI-compatible endpoints are text-only.

**Hosted OpenAI-compatible inference:**

```dotenv
CREATIVITY_BASE_URL=https://YOUR_PROVIDER/v1
CREATIVITY_MODEL=YOUR_MODEL_NAME
CREATIVITY_API_KEY=YOUR_API_KEY
```

The provider must support `POST /chat/completions` and reply using a `choices[0].message.content` JSON text response. Different providers may bill separately. An ordinary ChatGPT subscription is not an API balance.

## 3. Operation examples

```bash
python run.py evaluate --file examples/vox_reel.json --output audit.json
python run.py improve --file examples/car_ad.json --output better_ad.json
python run.py generate --file examples/car_ad.json --output new_concept.json
python run.py compare --file examples/compare.json --output comparison.json
```

**Actual image review**, provided you use a vision model:

```bash
python run.py evaluate --file examples/car_ad.json --image "my-poster.png" --output visual-audit.json
```

For video, give it a transcript, timestamps, storyboards and/or up to five extracted frames. The package **does not decode video itself**. That is deliberate: the creative engine works independently of your media renderer.

### JSON brief contract

Input file shape:

```json
{
  "medium": "reel",
  "platform": "Instagram Reels",
  "goal": "Increase story completion",
  "audience": "English-speaking family audience",
  "brand_guidelines": "Original cinematic stories, clear action",
  "constraints": ["9:16", "under 40 seconds"],
  "success_metric": "7-day average percentage viewed",
  "content": "Your script, concept, caption, brief or art direction here"
}
```

The optional `images` input field may contain up to five base64 `data:image/...` URIs if calling the API directly. Do **not** send remote or local file paths in that field. CLI uses `--image` for local files. Image size limit is 4 MB per local image, and a maximum 5 images per call.

`compare` uses an additional `alternatives` array with 2-5 objects containing `name` and `content`. `generate` needs `goal` but not `content`.

## 4. Integrate in any automation (HTTP API)

Start:

```bash
python run.py serve --host 127.0.0.1 --port 8765
```

Endpoints: `GET /health`, `POST /evaluate`, `/improve`, `/generate`, `/compare`, `/track`, `/insights`; `GET /insights`.

Example:

```bash
curl -X POST http://127.0.0.1:8765/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"medium":"caption","goal":"Qualified leads","audience":"Urban drivers","content":"Premium protection. Contact us."}'
```

Use the same JSON body in n8n, Make, Antigravity orchestration, custom web apps or a content queue. Add a condition such as `decision == PASS` before sending a creative to publishing. For `HUMAN_REVIEW`, pause for approval; for `REVISE` or `REWORK`, route to improvement and recheck. Scores alone should not trigger fully automated public publishing without reasonable quality and safety controls.

**Security:** Default server binds to localhost. To listen on all interfaces, first set a long `CREATIVITY_SERVER_TOKEN` environment variable (then use `Authorization: Bearer ...`). If deploying publicly, put it behind HTTPS, identity/access controls and rate limits; the sample HTTP server itself is not a production-grade gateway.

## 5. Connect as an MCP server (Codex, Antigravity, compatible agent IDEs)

Install the official current MCP SDK:

```bash
python -m pip install "mcp>=2,<3"
```

Launch:

```bash
python mcp_server.py
```

Your MCP host **starts** this process over stdio. In its MCP server configuration use the following generic structure (replace `python` with the absolute Python interpreter and the path with your actual installation path):

```json
{
  "mcpServers": {
    "creative-intelligence": {
      "command": "python",
      "args": ["C:/PATH/TO/creative-intelligence-agent/mcp_server.py"],
      "env": {
        "CREATIVITY_MODEL": "gemma3:4b",
        "CREATIVITY_BASE_URL": "http://localhost:11434/v1"
      }
    }
  }
}
```

Different hosts use different MCP settings formats and support, so adapt the config to the host. Tools exposed: `creative_evaluate`, `creative_improve`, `creative_generate`, `creative_compare`, `creative_track`, `creative_insights`. The MCP interface accepts text briefs; use the CLI or HTTP API for actual images.

MCP uses the official SDK instead of a hand-rolled protocol for compatibility with evolving MCP protocol versions.

## 6. Run inside another Python application

```python
from creative_intelligence import CreativeAgent
agent = CreativeAgent()
report = agent.evaluate({
    "medium": "story",
    "goal": "Stronger ending",
    "audience": "Family entertainment",
    "content": "My original storyline..."
})
print(report["score"], report["decision"])
```

The host agent can consume reports as JSON and decide whether to revise, escalate, or publish. Do **not** modify your existing renderer/repo just to use this layer. Call it before and after your existing render stage.

## 7. Record measured outcomes (optional local memory)

```bash
python run.py track --file examples/track.json --db creative_experiments.sqlite
python run.py insights --db creative_experiments.sqlite
```

`examples/track.json` contains **synthetic sample numbers**. Replace them with real analytics. These results are stored only in the local SQLite file and are not automatically fetched from Instagram/YouTube. Summaries are descriptive averages; no unearned causal inference or self-training is performed. You can pass observations into a future brief to produce informed tests.

## 8. Recommended automation placement

```text
Discovery / Brief
      |
      v
AURA: generate + evaluate
      |
   PASS? ------ no --> improve once --> re-evaluate --> human review if unresolved
      |
     yes
      v
Existing render engine (untouched)
      |
      v
Frame, audio, technical and rights QC
      |
      v
Human approval / Publishing system
      |
      v
Real analytics --> experiment ledger --> next creative brief
```

Do not let the LLM repeatedly rewrite until it assigns itself a perfect score. Use a maximum iteration count and actual humans/metrics for validation.

## 9. Tests

```bash
python -m unittest discover -s tests -v
```

These tests use a fake provider to check scoring, workflow and local memory, so they can run without an API key or Ollama model. They do not certify real-world creative judgment.

## Known limitations

- Not a hosted 24/7 agent. The process requires a runtime or remote deployment, and API/MCP callers must be able to reach it.
- No native image generation or video rendering. It reviews or plans creative; your renderer remains the producer.
- No built-in browser, fact-checking service, platform analytics connector, rights database or posting access.
- Editorial scores are subjective; even re-scoring is not proof of quality or commercial results.
- A vision-capable model is required to inspect actual images. It cannot reliably judge complete video motion/sound from script and a handful of frames.
- Untrusted internet model endpoints should not receive private customer content. Choose providers and policies accordingly.
- Model context sizes and JSON reliability vary. If your model returns malformed results, upgrade the model or shorten the brief.

## License

MIT. See `LICENSE`.
