#!/usr/bin/env python3
"""Stage 2 orchestrator: sequences agents 1-8 for real against a running
taskflow-ops, writes real evidence files. Stops before agent 9
(independent-review) and prints exactly what a human needs to decide —
this script never fakes that gate, and never runs agent 9 in the same
process/session that produced the tuning proposal, per
agents/independent-review/AGENT.md.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
KNOWLEDGE_DIR = ROOT / "knowledge"


def write_evidence(name: str, data: dict[str, Any]) -> Path:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    path = EVIDENCE_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


# --- Agent 2: product-discovery -------------------------------------------


def product_discovery(requirement: str, journey: list[str]) -> dict[str, Any]:
    with open(KNOWLEDGE_DIR / "api" / "openapi.json") as f:
        spec = json.load(f)
    known_paths = set(spec["paths"].keys())

    unknowns = [step for step in journey if step not in known_paths]
    result = {
        "requirement": requirement,
        "journey": journey,
        "journey_verified_against": "knowledge/api/openapi.json",
        "unknowns": unknowns,
        "gate_passed": len(unknowns) == 0,
    }
    write_evidence("product-discovery", result)
    return result


# --- Agent 3: risk-workload -------------------------------------------------


def risk_workload() -> dict[str, Any]:
    objectives_gap = (KNOWLEDGE_DIR / "objectives" / "GAP.md").exists()
    traffic_gap = (KNOWLEDGE_DIR / "traffic" / "GAP.md").exists()

    result = {
        "user_ramp": [1, 5, 10],
        "p95_target_ms": 200,
        "error_rate_limit": 0.0,
        "targets_are_placeholder": objectives_gap or traffic_gap,
        "placeholder_reason": (
            "knowledge/objectives/ and knowledge/traffic/ are both GAP "
            "folders for taskflow-ops — no real SLO or traffic shape exists yet"
            if (objectives_gap or traffic_gap)
            else None
        ),
    }
    write_evidence("risk-workload", result)
    return result


# --- Agent 5: observability --------------------------------------------------


async def observability(base_url: str) -> dict[str, Any]:
    try:
        response = await httpx.AsyncClient(timeout=5.0).get(f"{base_url}/metrics")
        reachable = response.status_code == 200
        fields = list(response.json().keys()) if reachable else []
    except httpx.HTTPError:
        reachable = False
        fields = []

    result = {
        "target": f"{base_url}/metrics",
        "reachable": reachable,
        "fields_confirmed": fields,
        "tracing_available": False,
        "tracing_gap_note": "no OpenTelemetry wiring exists in taskflow-ops yet",
        "gate_passed": reachable,
    }
    write_evidence("observability", result)
    return result


# --- Agent 6: execution -------------------------------------------------------


async def execution(base_url: str, count: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            before = (await client.get(f"{base_url}/metrics")).json()
        except httpx.HTTPError as exc:
            result = {"target_reachable": False, "error": str(exc)}
            write_evidence("execution", result)
            return result

        async def create_one(i: int) -> tuple[int, str | None]:
            try:
                r = await client.post(f"{base_url}/tasks", json={"name": f"load-{i}"})
                return r.status_code, (r.json().get("task_id") if r.status_code == 201 else None)
            except httpx.HTTPError:
                return 0, None

        results = await asyncio.gather(*(create_one(i) for i in range(count)))
        status_codes = [r[0] for r in results]
        task_ids = [r[1] for r in results if r[1] is not None]

        after = (await client.get(f"{base_url}/metrics")).json()

    result = {
        "target_reachable": True,
        "requests_sent": count,
        "successes": len(task_ids),
        "distinct_task_ids": len(set(task_ids)),
        "status_codes": status_codes,
        "metrics_before": before,
        "metrics_after": after,
    }
    write_evidence("execution", result)
    return result


# --- Agent 7: performance-analyst --------------------------------------------


def performance_analyst(risk: dict[str, Any], exec_result: dict[str, Any]) -> dict[str, Any]:
    if not exec_result.get("target_reachable"):
        result = {"insufficient_evidence": True, "reason": "execution target unreachable"}
        write_evidence("performance-analyst", result)
        return result

    successes = int(exec_result["successes"])
    requests_sent = int(exec_result["requests_sent"])
    distinct_task_ids = int(exec_result["distinct_task_ids"])

    success_rate = successes / requests_sent
    duplicate_ids = distinct_task_ids != successes

    if duplicate_ids:
        finding = "duplicate task_ids under concurrency"
        confidence = "confirmed"
    elif success_rate < 1.0:
        finding = f"request failures under concurrency (success rate {success_rate:.0%})"
        confidence = "confirmed"
    else:
        finding = "no bottleneck observed at this load level"
        confidence = "likely" if risk.get("targets_are_placeholder") else "confirmed"

    result = {
        "insufficient_evidence": False,
        "finding": finding,
        "confidence": confidence,
        "confidence_capped_reason": (
            "risk-workload targets are placeholders, not real SLOs"
            if risk.get("targets_are_placeholder")
            else None
        ),
        "success_rate": success_rate,
    }
    write_evidence("performance-analyst", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8001")
    parser.add_argument("--requirement", default="Support concurrent task creation without duplicates")
    parser.add_argument("--journey", nargs="+", default=["/tasks", "/tasks/{task_id}", "/metrics"])
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    print("=== Agent 2: product-discovery ===")
    discovery = product_discovery(args.requirement, args.journey)
    print(json.dumps(discovery, indent=2))
    if not discovery["gate_passed"]:
        print("GATE FAILED: journey references endpoints not in the API spec. Stopping.")
        return 1

    print("\n=== Agent 3: risk-workload ===")
    risk = risk_workload()
    print(json.dumps(risk, indent=2))

    print("\n=== Agent 5: observability ===")
    obs = asyncio.run(observability(args.base_url))
    print(json.dumps(obs, indent=2))
    if not obs["gate_passed"]:
        print(f"GATE FAILED: {args.base_url}/metrics unreachable. Stopping.")
        return 1

    print("\n=== Agent 6: execution ===")
    exec_result = asyncio.run(execution(args.base_url, args.count))
    print(json.dumps(exec_result, indent=2))

    print("\n=== Agent 7: performance-analyst ===")
    analysis = performance_analyst(risk, exec_result)
    print(json.dumps(analysis, indent=2))

    print("\n=== HUMAN APPROVAL GATE: Agent 8 (tuning) does not run automatically ===")
    if analysis.get("insufficient_evidence"):
        print("Insufficient evidence for a tuning proposal. Pipeline stops here — RETEST.")
        return 1

    print(f"Finding: {analysis['finding']} (confidence: {analysis['confidence']})")
    print(
        "A tuning proposal requires a human to review this evidence and decide "
        "whether to proceed. This script deliberately does not propose or apply "
        "a change on its own — see agents/tuning/AGENT.md."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
