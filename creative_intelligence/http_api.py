"""Local HTTP JSON API. Keep behind a TLS/auth gateway if exposing beyond localhost."""
from __future__ import annotations
import hmac
import json
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from .engine import CreativeAgent
from .memory import ExperimentLedger

MAX_BODY = 12_000_000


def serve(host: str = "127.0.0.1", port: int = 8765, db_path: str = "creative_experiments.sqlite") -> None:
    auth_token = os.getenv("CREATIVITY_SERVER_TOKEN", "")
    if host not in ("127.0.0.1", "localhost", "::1") and not auth_token:
        raise RuntimeError("Refusing non-local binding without CREATIVITY_SERVER_TOKEN")
    class Handler(BaseHTTPRequestHandler):
        def _response(self, code, data):
            blob = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)

        def _authorized(self):
            if not auth_token:
                return True
            header = self.headers.get("Authorization", "")
            return hmac.compare_digest(header, "Bearer " + auth_token)

        def do_GET(self):
            if self.path == "/health":
                return self._response(200, {"ok": True, "service": "creative-intelligence", "status": "ready"})
            if not self._authorized():
                return self._response(401, {"error": "unauthorized"})
            if self.path == "/insights":
                return self._response(200, ExperimentLedger(db_path).insights())
            return self._response(404, {"error": "unknown endpoint"})

        def do_POST(self):
            if not self._authorized():
                return self._response(401, {"error": "unauthorized"})
            op = self.path.lstrip("/")
            if op not in {"evaluate", "improve", "generate", "compare", "track", "insights"}:
                return self._response(404, {"error": "unknown endpoint"})
            size = self.headers.get("Content-Length")
            if not size or not size.isdigit():
                return self._response(411, {"error": "Content-Length required"})
            if int(size) > MAX_BODY:
                return self._response(413, {"error": "request too large"})
            try:
                data = json.loads(self.rfile.read(int(size)))
                if not isinstance(data, dict):
                    raise ValueError("Request body must be a JSON object")
                if op == "track":
                    result = ExperimentLedger(db_path).record(data)
                elif op == "insights":
                    result = ExperimentLedger(db_path).insights(
                        platform=data.get("platform"), metric=data.get("metric"))
                else:
                    agent = CreativeAgent()
                    result = getattr(agent, op)(data)
                return self._response(200, result)
            except (ValueError, TypeError) as exc:
                return self._response(400, {"error": str(exc)[:500]})
            except RuntimeError as exc:
                return self._response(503, {"error": str(exc)[:500]})
            except Exception as exc:
                # Avoid leaking provider secrets / traces in API responses.
                return self._response(502, {"error": "Model or service operation failed", "type": type(exc).__name__})

        def log_message(self, fmt, *args):
            # Do not log private creative content or authorization headers.
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Creative Intelligence API listening at http://{host}:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
