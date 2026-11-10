"""Run from any terminal with `python run.py ...`."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .engine import CreativeAgent
from .memory import ExperimentLedger


def main(argv=None):
    parser = argparse.ArgumentParser(prog="creative-intelligence", description="Reusable creative analysis and generation agent")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("evaluate", "improve", "generate", "compare", "track"):
        p = sub.add_parser(command, help=f"{command.title()} a creative brief")
        p.add_argument("--file", required=True, help="Input JSON file")
        p.add_argument("--output", help="Optional result JSON file")
        if command in {"evaluate", "improve", "generate", "compare"}:
            p.add_argument("--image", action="append", default=[], help="Local JPG/PNG/WEBP/GIF image (repeat up to five)")
        if command == "track":
            p.add_argument("--db", default="creative_experiments.sqlite", help="SQLite experiment ledger path")
    p = sub.add_parser("insights", help="Summarize recorded experimental outcomes")
    p.add_argument("--db", default="creative_experiments.sqlite")
    p.add_argument("--platform")
    p.add_argument("--metric")
    p.add_argument("--output")
    p = sub.add_parser("serve", help="Start local JSON HTTP server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--db", default="creative_experiments.sqlite")
    args = parser.parse_args(argv)
    try:
        if args.command == "serve":
            from .http_api import serve
            serve(args.host, args.port, args.db)
            return 0
        if args.command == "insights":
            result = ExperimentLedger(args.db).insights(args.platform, args.metric)
        else:
            payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
            if args.command == "track":
                result = ExperimentLedger(args.db).record(payload)
            else:
                result = getattr(CreativeAgent(), args.command)(payload, args.image)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
            print(f"Saved result to {args.output}", file=sys.stderr)
        else:
            print(output)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
