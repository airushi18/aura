"""Simple portable SQLite experiment ledger. No automated causal attribution."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ExperimentLedger:
    def __init__(self, path: str = "creative_experiments.sqlite"):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                creative_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                variant TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                sample_size INTEGER,
                notes TEXT
            )""")

    def record(self, item: dict) -> dict:
        required = ["creative_id", "platform", "variant", "metric", "value"]
        if any(key not in item or item[key] in (None, "") for key in required):
            raise ValueError("track requires creative_id, platform, variant, metric, value")
        value = float(item["value"])
        if not (-1e12 < value < 1e12):
            raise ValueError("Metric value out of range")
        sample_size = item.get("sample_size")
        if sample_size is not None:
            sample_size = int(sample_size)
            if sample_size < 0:
                raise ValueError("sample_size cannot be negative")
        row = (
            datetime.now(timezone.utc).isoformat(),
            str(item["creative_id"])[:200], str(item["platform"])[:100],
            str(item["variant"])[:100], str(item["metric"])[:100].lower(),
            value, sample_size, str(item.get("notes", ""))[:1500],
        )
        with sqlite3.connect(self.path) as db:
            cur = db.execute("""INSERT INTO results (recorded_at, creative_id, platform, variant,
                metric, value, sample_size, notes) VALUES (?,?,?,?,?,?,?,?)""", row)
            return {"recorded": True, "id": cur.lastrowid, "creative_id": row[1]}

    def insights(self, platform: str | None = None, metric: str | None = None, limit: int = 50) -> dict:
        query = "SELECT recorded_at, creative_id, platform, variant, metric, value, sample_size, notes FROM results WHERE 1=1"
        args = []
        if platform:
            query += " AND platform=?"
            args.append(platform)
        if metric:
            query += " AND metric=?"
            args.append(metric.lower())
        query += " ORDER BY id DESC LIMIT ?"
        args.append(max(1, min(250, limit)))
        with sqlite3.connect(self.path) as db:
            rows = db.execute(query, args).fetchall()
        keys = ["recorded_at", "creative_id", "platform", "variant", "metric", "value", "sample_size", "notes"]
        observations = [dict(zip(keys, row)) for row in rows]
        groups = {}
        for row in observations:
            key = (row["platform"], row["metric"])
            slot = groups.setdefault(key, [])
            slot.append(row["value"])
        return {"observation_count": len(observations),
                "group_summaries": [{"platform": k[0], "metric": k[1], "count": len(v),
                                    "unweighted_mean": round(sum(v)/len(v), 4)} for k, v in groups.items()],
                "observations": observations,
                "caution": "Descriptive statistics only. Different audience sizes, time windows and formats are not controlled; no causal learning is implied."}
