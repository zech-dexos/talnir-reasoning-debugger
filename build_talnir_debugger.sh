#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/talnir_debugger"
mkdir -p "$APP_DIR"

cat > "$APP_DIR/talnir_debugger.py" <<'PYEOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

TRI_SIGIL = "☧🦅🜇"


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def conspark() -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"[R:TOS{TRI_SIGIL}|TS:{ts}]"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    return text[0].upper() + text[1:]


def ensure_sentence(text: str) -> str:
    text = clean_text(text)
    if not text:
        return ""
    if text[-1] not in ".!?":
        text += "."
    return text


@dataclass
class PathOption:
    id: str
    title: str
    summary: str
    rationale: str
    score: int
    instruction: str


def detect_signals(task: str) -> Dict[str, float]:
    t = task.lower()

    def hits(words: List[str]) -> int:
        return sum(1 for w in words if w in t)

    return {
        "customer": min(hits(["customer", "client", "refund", "support", "complaint", "angry", "frustrated"]) / 2.0, 1.0),
        "technical": min(hits(["bug", "error", "crash", "debug", "system", "runtime", "model", "pipeline", "latency"]) / 2.0, 1.0),
        "business": min(hits(["cost", "budget", "revenue", "team", "priority", "roadmap", "stakeholder", "lease", "buy"]) / 2.0, 1.0),
        "risk": min(hits(["risk", "harm", "damage", "unsafe", "critical", "severe", "urgent"]) / 2.0, 1.0),
        "emotion": min(hits(["angry", "frustrated", "upset", "worried", "concerned"]) / 2.0, 1.0),
        "decision": min(hits(["choose", "decision", "which", "path", "option", "direction"]) / 2.0, 1.0),
    }


def generate_paths(task: str) -> List[PathOption]:
    s = detect_signals(task)

    empathic = 50 + int(20 * s["customer"] + 15 * s["emotion"] - 5 * s["technical"])
    solution = 50 + int(15 * s["technical"] + 10 * s["customer"] + 10 * s["decision"])
    risk_control = 50 + int(20 * s["risk"] + 10 * s["technical"])
    business = 50 + int(20 * s["business"] + 10 * s["decision"])

    paths = [
        PathOption(
            id="A",
            title="De-escalate and stabilize",
            summary="Lead with clarity, empathy, and immediate stabilization.",
            rationale="Best when trust, tension, or emotional volatility are part of the task.",
            score=empathic,
            instruction="Respond in a calm, empathetic, stabilizing way. Acknowledge concerns first, reduce friction, then move toward resolution.",
        ),
        PathOption(
            id="B",
            title="Diagnose and solve",
            summary="Lead with root cause isolation and the fastest practical fix.",
            rationale="Best when the task is technical, operational, or needs a direct solution path.",
            score=solution,
            instruction="Respond as a problem-solver. Isolate the issue, identify likely causes, recommend the most direct next steps, and keep the answer practical.",
        ),
        PathOption(
            id="C",
            title="Contain risk first",
            summary="Lead by preventing damage, reducing downside, and enforcing safeguards.",
            rationale="Best when being wrong has high cost or the situation could worsen quickly.",
            score=risk_control,
            instruction="Respond conservatively. Prioritize safety, risk containment, stop conditions, and damage reduction before optimization.",
        ),
        PathOption(
            id="D",
            title="Optimize for business value",
            summary="Lead with leverage, resource efficiency, and decision impact.",
            rationale="Best when the task is strategic, budget-sensitive, or tied to value creation.",
            score=business,
            instruction="Respond like an operator. Prioritize leverage, speed, cost control, and the highest-value next move.",
        ),
    ]

    paths.sort(key=lambda p: p.score, reverse=True)
    return paths


def recommendation(paths: List[PathOption]) -> Dict[str, str]:
    top = paths[0]
    return {
        "id": top.id,
        "title": top.title,
        "reason": f"Talnir recommends '{top.title}' because it best fits the task signal pattern.",
    }


def interpret_choice(raw: str, paths: List[PathOption]) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    upper = text.upper()
    ids = [p.id for p in paths]
    if upper in ids:
        return upper

    lowered = text.lower()
    alias = {
        "de-escalate": "A",
        "stabilize": "A",
        "empathy": "A",
        "solve": "B",
        "diagnose": "B",
        "technical": "B",
        "risk": "C",
        "contain": "C",
        "safe": "C",
        "business": "D",
        "value": "D",
        "operator": "D",
    }
    for k, v in alias.items():
        if k in lowered:
            return v
    return ""


def synthesize_output(task: str, chosen: PathOption) -> str:
    task_clean = clean_text(task)

    if chosen.id == "A":
        return (
            f"I understand the pressure around this: {task_clean}. "
            f"The first priority is to reduce tension and create stability. "
            f"Start by acknowledging the concern clearly, then state the next concrete step, "
            f"then confirm how resolution will be tracked so trust is preserved."
        )

    if chosen.id == "B":
        return (
            f"For this task — {task_clean} — the strongest move is to diagnose before broad changes. "
            f"Define the problem in one line, isolate the most likely cause, test the smallest meaningful fix, "
            f"and only then expand effort. This keeps the response practical and debuggable."
        )

    if chosen.id == "C":
        return (
            f"For this situation — {task_clean} — contain downside first. "
            f"Stop anything that could worsen the state, verify the highest-risk variable, "
            f"and do not optimize until the damage boundary is under control."
        )

    return (
        f"For this task — {task_clean} — optimize for leverage. "
        f"Focus on the highest-value next move, avoid low-return effort, "
        f"and choose the path that improves speed, clarity, and resource efficiency fastest."
    )


def realigned_forward_plan(task: str, chosen: PathOption) -> List[str]:
    base = clean_text(task)

    if chosen.id == "A":
        return [
            f"Restate the problem calmly: {base}.",
            "Acknowledge the human concern or friction explicitly.",
            "Give the next concrete step in simple language.",
            "State how progress or resolution will be confirmed.",
            "Do not escalate tone or complexity unless needed.",
        ]

    if chosen.id == "B":
        return [
            f"Define the core problem in one line: {base}.",
            "List the most likely cause or failure point first.",
            "Recommend the smallest useful test or corrective step.",
            "Use the result to narrow the next move.",
            "Do not branch into unrelated possibilities too early.",
        ]

    if chosen.id == "C":
        return [
            f"Identify what could get worse first in: {base}.",
            "Stop or avoid the action that increases downside.",
            "Check the highest-risk variable before proceeding.",
            "Resume only after the main risk is reduced.",
            "Document the stop condition and the safe next move.",
        ]

    return [
        f"Define the outcome that matters most in: {base}.",
        "Choose the smallest action with the highest leverage.",
        "Avoid effort that does not improve speed, clarity, or value.",
        "Confirm the action changed the situation meaningfully.",
        "Reassess only after the first high-value move is complete.",
    ]


def run_session(task: str, chosen_input: str) -> Dict[str, Any]:
    task = clean_text(task)
    paths = generate_paths(task)
    rec = recommendation(paths)
    chosen_id = interpret_choice(chosen_input, paths)
    if not chosen_id:
        raise ValueError("Invalid path choice. Use A/B/C/D or words like solve, risk, empathy, or business.")

    chosen = next(p for p in paths if p.id == chosen_id)

    return {
        "session_marker": conspark(),
        "timestamp": utc_now(),
        "task": task,
        "paths": [asdict(p) for p in paths],
        "recommendation": rec,
        "chosen_path": asdict(chosen),
        "realignment_note": f"Talnir realigned to '{chosen.title}' and constrained the output to that continuation.",
        "final_output": synthesize_output(task, chosen),
        "forward_plan": realigned_forward_plan(task, chosen),
        "alignment_enforced": True,
    }


def print_session(result: Dict[str, Any]) -> None:
    print("\n" + "=" * 72)
    print("TALNIR DEBUG SESSION")
    print("=" * 72)
    print(f"Task:\n  {result['task']}\n")

    print("Proposed paths:")
    for p in result["paths"]:
        marker = "★ " if p["id"] == result["recommendation"]["id"] else "  "
        print(f"{marker}[{p['id']}] {p['title']} (score: {p['score']})")
        print(f"    Summary: {p['summary']}")
        print(f"    Rationale: {p['rationale']}")
        print()

    print(f"Recommendation:\n  [{result['recommendation']['id']}] {result['recommendation']['title']}")
    print(f"Reason:\n  {result['recommendation']['reason']}\n")

    print(f"Chosen path:\n  [{result['chosen_path']['id']}] {result['chosen_path']['title']}")
    print(f"Realignment:\n  {result['realignment_note']}\n")

    print("Final aligned output:")
    print(f"  {result['final_output']}\n")

    print("Forward plan:")
    for i, step in enumerate(result["forward_plan"], 1):
        print(f"  {i}. {step}")
    print()

    print("Trace:")
    print(f"  Paths generated: {len(result['paths'])}")
    print(f"  Alignment enforced: {result['alignment_enforced']}")
    print("=" * 72 + "\n")


def save_last_session(result: Dict[str, Any], app_dir: str) -> None:
    out = f"{app_dir}/last_talnir_session.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved session: {out}\n")


def main() -> None:
    print("\nTalnir Reasoning Debugger")
    print(conspark())
    print("Show candidate reasoning paths, choose one, realign output.\n")

    task = input("Enter task:\n> ").strip()
    print("\nChoose a path style after paths are shown.")
    print("Examples: A / B / C / D / solve / empathy / risk / business\n")

    paths = generate_paths(task)
    rec = recommendation(paths)

    print("=" * 72)
    print("TALNIR PROPOSED PATHS")
    print("=" * 72)
    for p in paths:
        marker = "★ " if p.id == rec["id"] else "  "
        print(f"{marker}[{p.id}] {p.title} (score: {p.score})")
        print(f"    {p.summary}")
        print(f"    Why: {p.rationale}")
        print()
    print(f"Recommended: [{rec['id']}] {rec['title']}")
    print(f"Reason: {rec['reason']}")
    print("=" * 72)

    chosen = input("\nChoose path:\n> ").strip()
    result = run_session(task, chosen)
    print_session(result)
    save_last_session(result, "$APP_DIR")


if __name__ == "__main__":
    main()
PYEOF

chmod +x "$APP_DIR/talnir_debugger.py"

cat > "$APP_DIR/README.txt" <<'TXTEOF'
Talnir Reasoning Debugger

What it is:
A visible demo artifact for Talnir as a reasoning-path debugger.

What it shows:
- one task
- multiple candidate continuations
- explicit path choice
- realigned final output
- traceable forward plan

Run:
python3 ~/talnir_debugger/talnir_debugger.py

Suggested demo tasks:
1. Write a response to a frustrated customer asking for a refund
2. Explain how to debug model drift in an agent pipeline
3. Decide whether to lease a tool to a company or sell it outright
TXTEOF

echo
echo "Build complete."
echo "Run it with:"
echo "python3 ~/talnir_debugger/talnir_debugger.py"
echo
