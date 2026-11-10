"""Standard-library OpenAI-compatible client (OpenAI, NVIDIA NIM, Ollama, etc.)."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


def load_dotenv(path: Path | None = None) -> None:
    # Support editable installs, git installs, and project-local configurations.
    candidates = [path] if path is not None else [
        Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"
    ]
    path = next((item for item in candidates if item is not None and item.is_file()), None)
    if path is None:
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key.isidentifier():
            os.environ.setdefault(key, val)


def parse_json_text(text: str) -> dict:
    if not isinstance(text, str):
        raise ValueError("The model returned no text")
    data = text.strip()
    if data.startswith("```"):
        data = re.sub(r"^```(?:json)?\s*", "", data, flags=re.I)
        data = re.sub(r"\s*```$", "", data)
    try:
        item = json.loads(data)
    except json.JSONDecodeError:
        start = data.find("{")
        if start < 0:
            raise ValueError("No JSON object found in model response")
        item, _ = json.JSONDecoder().raw_decode(data[start:])
    if not isinstance(item, dict):
        raise ValueError("Model must return a JSON object")
    return item


class ChatClient:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("CREATIVITY_MODEL", "").strip()
        self.base_url = os.getenv("CREATIVITY_BASE_URL", "http://localhost:11434/v1").rstrip("/")
        self.api_key = os.getenv("CREATIVITY_API_KEY", "").strip()
        self.timeout = max(10, min(240, int(os.getenv("CREATIVITY_TIMEOUT", "90"))))
        if not self.model:
            raise RuntimeError("CREATIVITY_MODEL not set. Copy .env.example to .env and choose a model. See README.")
        if self.base_url.endswith("/chat/completions"):
            self.endpoint = self.base_url
        else:
            self.endpoint = self.base_url + "/chat/completions"
        if not self.endpoint.startswith(("http://", "https://")):
            raise ValueError("CREATIVITY_BASE_URL must start with http:// or https://")

    def complete_json(self, system: str, user: str, images: list[str] | None = None) -> dict:
        user_message = user
        if images:
            parts = [{"type": "text", "text": user}]
            for item in images[:5]:
                if not item.startswith("data:image/"):
                    raise ValueError("Only base64 image data URIs are allowed")
                if len(item) > 8_000_000:
                    raise ValueError("Image is too large")
                parts.append({"type": "image_url", "image_url": {"url": item}})
            user_message = parts
        body = {"model": self.model, "temperature": 0.35,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_message}]}
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        last_error = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    payload = json.loads(response.read(8_000_000).decode("utf-8"))
                text = payload["choices"][0]["message"]["content"]
                if isinstance(text, list):
                    text = "\n".join(part.get("text", "") for part in text if isinstance(part, dict))
                return parse_json_text(text)
            except urllib.error.HTTPError as exc:
                detail = exc.read(700).decode("utf-8", errors="replace")
                last_error = RuntimeError(f"Model HTTP {exc.code}: {detail}")
                if exc.code not in {429, 500, 502, 503, 504}:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = RuntimeError(f"Model connection failed: {exc}")
            if attempt < 2:
                time.sleep(1 + attempt)
        raise last_error or RuntimeError("Model request failed")
