"""Platform-neutral creative audit rubric and response validation."""
from __future__ import annotations

CRITERIA = {
    "objective_fit": (15, "Does the creative accomplish the stated business or storytelling objective?"),
    "audience_relevance": (15, "Will the intended audience find it relevant and understandable?"),
    "attention_and_hook": (15, "Does it earn attention appropriately for its medium and context?"),
    "clarity_and_hierarchy": (15, "Is the message, structure, and visual/verbal hierarchy clear?"),
    "distinctiveness": (15, "Is the concept distinctive rather than derivative or formulaic?"),
    "craft_and_feasibility": (15, "Is the execution polished, on-brief, and feasible with the constraints?"),
    "trust_brand_and_safety": (10, "Are facts, accessibility, appropriateness, rights, and brand considerations respected?"),
}

DEFAULT_PASS = 80
DEFAULT_REVISE = 60


def normalize_audit(raw: dict, source_label: str = "creative") -> dict:
    """Strictly calculate scores locally rather than trusting a model's overall number."""
    if not isinstance(raw, dict):
        raise ValueError("The model returned a non-object audit")
    entries = raw.get("rubric")
    if not isinstance(entries, dict):
        raise ValueError("Model response missing rubric object")

    total = 0.0
    rubric = {}
    for key, (weight, meaning) in CRITERIA.items():
        entry = entries.get(key)
        if not isinstance(entry, dict):
            raise ValueError(f"Rubric missing criterion: {key}")
        value = entry.get("score")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Non-numeric score for {key}")
        score = round(max(0.0, min(10.0, float(value))), 1)
        reason = str(entry.get("reason", "")).strip()
        fix = str(entry.get("improvement", "")).strip()
        if not reason:
            raise ValueError(f"Rubric missing explanation for {key}")
        total += score * weight / 10.0
        rubric[key] = {"score": score, "weight": weight, "why": reason, "improvement": fix, "definition": meaning}

    risk_flags = raw.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        risk_flags = []
    normalized_flags = []
    for flag in risk_flags[:12]:
        if not isinstance(flag, dict):
            continue
        severity = str(flag.get("severity", "medium")).lower()
        if severity not in {"critical", "high", "medium", "low"}:
            severity = "medium"
        normalized_flags.append({
            "severity": severity,
            "issue": str(flag.get("issue", ""))[:800],
            "remedy": str(flag.get("remedy", ""))[:800],
            "unresolved": flag.get("unresolved") is True,
        })

    score = int(round(total))
    if any(f["severity"] == "critical" and f["unresolved"] for f in normalized_flags):
        verdict = "HUMAN_REVIEW"
    else:
        verdict = "PASS" if score >= DEFAULT_PASS else "REVISE" if score >= DEFAULT_REVISE else "REWORK"

    def strings(field, count=8):
        values = raw.get(field, [])
        if not isinstance(values, list):
            return []
        return [str(v)[:1200] for v in values[:count] if isinstance(v, (str, int, float))]

    variants = raw.get("test_variants", [])
    if not isinstance(variants, list):
        variants = []
    return {
        "source": source_label,
        "score": score,
        "decision": verdict,
        "confidence": str(raw.get("confidence", "low")) if raw.get("confidence") in {"low", "medium", "high"} else "low",
        "summary": str(raw.get("summary", ""))[:1500],
        "rubric": rubric,
        "strengths": strings("strengths"),
        "weaknesses": strings("weaknesses"),
        "improvements_in_priority_order": strings("improvement_plan"),
        "risk_flags": normalized_flags,
        "needs_verification": strings("needs_verification"),
        "test_variants": [v for v in variants[:4] if isinstance(v, dict)],
        "notes": "Scores are subjective editorial judgments, not measured engagement or forecasted results. Facts are not independently researched.",
    }
