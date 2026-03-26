#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import datetime
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from formation_layer import build_task_frame

TRI_SIGIL = "☧🦅🜇"
APP_DIR = os.path.expanduser("~/talnir_debugger")


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


@dataclass
class PathOption:
    id: str
    key: str
    title: str
    summary: str
    rationale: str
    score: int
    instruction: str


def family_to_path(family: str, frame: Dict[str, Any]) -> Dict[str, str]:
    objective = frame["objective"]
    asset = frame["asset"]

    mapping = {
        "de-escalate": {
            "title": "De-escalate and stabilize",
            "summary": "Lead with clarity, calm, and immediate stabilization.",
            "rationale": f"Best when preserving {asset} depends on reducing friction before solving deeper issues.",
            "instruction": f"Respond by reducing tension first, then move toward resolution while preserving {asset}.",
        },
        "diagnose": {
            "title": "Diagnose and solve",
            "summary": "Lead with root-cause isolation and the fastest practical fix.",
            "rationale": f"Best when the objective is to {objective} through structured diagnosis.",
            "instruction": "Respond as a problem-solver. Define the issue, isolate likely causes, and recommend the most direct next step.",
        },
        "contain_risk": {
            "title": "Contain risk first",
            "summary": "Lead by preventing damage, reducing downside, and enforcing safeguards.",
            "rationale": f"Best when failure to protect {asset} could worsen the situation quickly.",
            "instruction": "Respond conservatively. Prioritize stop conditions, damage reduction, and safe continuation boundaries.",
        },
        "optimize_value": {
            "title": "Optimize for business value",
            "summary": "Lead with leverage, efficiency, and decision impact.",
            "rationale": f"Best when the goal is to {objective} with minimum waste.",
            "instruction": "Respond like an operator. Prioritize leverage, speed, cost control, and the highest-value next move.",
        },
        "stabilize_frame": {
            "title": "Stabilize framing first",
            "summary": "Lead by clarifying the problem formation before selecting a continuation.",
            "rationale": "Best when the candidate set itself may be unstable or misframed.",
            "instruction": "Respond by clarifying the task frame first: what the task is, what matters, what is at risk, and what the real unknown is.",
        },
        "defer": {
            "title": "Defer and preserve flexibility",
            "summary": "Delay commitment while preserving optionality.",
            "rationale": f"Best when acting now may weaken {asset} or waste resources.",
            "instruction": "Respond by preserving options, avoiding lock-in, and waiting for a better decision point.",
        },
    }

    return mapping.get(
        family,
        {
            "title": "General continuation",
            "summary": "Proceed with the most coherent next step.",
            "rationale": "Fallback continuation.",
            "instruction": "Respond coherently and directly.",
        },
    )


def score_family(family: str, frame: Dict[str, Any]) -> int:
    domain = frame["domain"]
    risks = " ".join(frame["risks"]).lower()
    constraints = " ".join(frame["constraints"]).lower()

    score = 50

    if family == "diagnose":
        if domain in ["ai_systems", "customer_support", "general"]:
            score += 18
        if "misdiagnosis" in risks or "drift" in risks:
            score += 10

    elif family == "de-escalate":
        if domain == "customer_support":
            score += 22
        if "emotional volatility" in risks:
            score += 10

    elif family == "contain_risk":
        if domain in ["risk_control", "ai_systems"]:
            score += 16
        if "avoid" in constraints or "harm" in risks or "damage" in risks:
            score += 12

    elif family == "optimize_value":
        if domain == "business":
            score += 22

    elif family == "stabilize_frame":
        if domain == "ai_systems":
            score += 20
        if "do not confuse formation with selection" in constraints:
            score += 15
        if "misframed continuation set" in risks or "unstable formation" in risks:
            score += 10

    elif family == "defer":
        if domain in ["business", "risk_control"]:
            score += 8

    return score


def generate_paths(frame: Dict[str, Any]) -> List[PathOption]:
    paths: List[PathOption] = []
    ids = ["A", "B", "C", "D", "E", "F"]

    for i, family in enumerate(frame["strategy_families"]):
        meta = family_to_path(family, frame)
        paths.append(
            PathOption(
                id=ids[i],
                key=family,
                title=meta["title"],
                summary=meta["summary"],
                rationale=meta["rationale"],
                score=score_family(family, frame),
                instruction=meta["instruction"],
            )
        )

    paths.sort(key=lambda p: p.score, reverse=True)
    return paths


def recommendation(paths: List[PathOption]) -> Dict[str, str]:
    top = paths[0]
    return {
        "id": top.id,
        "title": top.title,
        "reason": f"Talnir recommends '{top.title}' because it best fits the stabilized formation frame.",
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
        "de-escalate": "de-escalate",
        "empathy": "de-escalate",
        "diagnose": "diagnose",
        "solve": "diagnose",
        "risk": "contain_risk",
        "contain": "contain_risk",
        "business": "optimize_value",
        "value": "optimize_value",
        "frame": "stabilize_frame",
        "stabilize frame": "stabilize_frame",
        "defer": "defer",
        "wait": "defer",
    }

    target_family = None
    for k, v in alias.items():
        if k in lowered:
            target_family = v
            break

    if target_family:
        for p in paths:
            if p.key == target_family:
                return p.id

    return ""


def synthesize_output(frame: Dict[str, Any], chosen: PathOption) -> str:
    task = frame["task"]
    objective = frame["objective"]
    asset = frame["asset"]

    if chosen.key == "de-escalate":
        return (
            f"This task should be approached by stabilizing the interaction first. "
            f"For '{task}', the immediate priority is to reduce friction, preserve {asset}, "
            f"and then move toward resolution without escalation."
        )

    if chosen.key == "diagnose":
        return (
            f"This task should be approached diagnostically. "
            f"For '{task}', define the issue clearly, isolate the most likely failure point, "
            f"and take the smallest useful step that advances the objective: {objective}."
        )

    if chosen.key == "contain_risk":
        return (
            f"This task should be approached through downside containment. "
            f"For '{task}', stop what could worsen the situation, verify the highest-risk variable, "
            f"and only continue once the damage boundary is under control."
        )

    if chosen.key == "optimize_value":
        return (
            f"This task should be approached through leverage. "
            f"For '{task}', prioritize the highest-value next move, reduce waste, "
            f"and act only where effort most improves the objective: {objective}."
        )

    if chosen.key == "stabilize_frame":
        return (
            f"This task should be approached by stabilizing formation before continuation choice. "
            f"For '{task}', first clarify domain, objective, asset, constraints, risks, and uncertainties "
            f"so the candidate path set is reliable before selection."
        )

    return (
        f"This task should be approached conservatively. "
        f"For '{task}', preserve flexibility and avoid commitment until the frame is clearer."
    )


def realigned_forward_plan(frame: Dict[str, Any], chosen: PathOption) -> List[str]:
    task = frame["task"]
    objective = frame["objective"]
    asset = frame["asset"]
    risks = ", ".join(frame["risks"][:3])
    constraints = ", ".join(frame["constraints"][:3])

    if chosen.key == "stabilize_frame":
        return [
            f"Restate the task in one clean line: {task}.",
            f"Define the objective explicitly: {objective}.",
            f"Name the protected asset: {asset}.",
            f"List the dominant risks: {risks}.",
            f"List the governing constraints: {constraints}.",
            "Only generate or choose continuations after the frame is stable.",
        ]

    if chosen.key == "diagnose":
        return [
            f"Define the core problem in one line: {task}.",
            "Identify the most likely failure or drift point first.",
            "Test the smallest useful hypothesis before broad changes.",
            f"Use the result to narrow the path toward: {objective}.",
            "Do not branch into unrelated possibilities too early.",
        ]

    if chosen.key == "contain_risk":
        return [
            f"Identify what could worsen first in: {task}.",
            f"Protect the primary asset: {asset}.",
            "Stop or avoid the action that increases downside.",
            "Verify the highest-risk variable before proceeding.",
            "Resume only after the main risk is reduced.",
        ]

    if chosen.key == "de-escalate":
        return [
            f"Restate the issue calmly: {task}.",
            f"Preserve {asset} by reducing friction first.",
            "Acknowledge the concern or instability explicitly.",
            "Give the next concrete step in simple language.",
            "Confirm how progress or resolution will be tracked.",
        ]

    if chosen.key == "optimize_value":
        return [
            f"Define the outcome that matters most in: {task}.",
            f"Choose the highest-leverage move toward: {objective}.",
            "Avoid low-return effort or unnecessary branching.",
            "Confirm the first move changed the situation meaningfully.",
            "Reassess only after the first high-value action completes.",
        ]

    return [
        f"Preserve optionality around: {task}.",
        f"Protect {asset} while delaying unnecessary commitment.",
        "Reduce uncertainty before re-entering the decision.",
    ]


def print_frame(frame: Dict[str, Any]) -> None:
    print("\n" + "=" * 72)
    print("FORMATION FRAME")
    print("=" * 72)
    print(f"Task:\n  {frame['task']}\n")
    print(f"Domain:\n  {frame['domain']}\n")
    print(f"Objective:\n  {frame['objective']}\n")
    print(f"Asset:\n  {frame['asset']}\n")

    print("Risks:")
    for item in frame["risks"]:
        print(f"  - {item}")
    print()

    print("Uncertainties:")
    for item in frame["uncertainties"]:
        print(f"  - {item}")
    print()

    print("Constraints:")
    for item in frame["constraints"]:
        print(f"  - {item}")
    print()

    print("Strategy families:")
    for item in frame["strategy_families"]:
        print(f"  - {item}")
    print("=" * 72)


def print_paths(paths: List[PathOption], rec: Dict[str, str]) -> None:
    print("\n" + "=" * 72)
    print("TALNIR PROPOSED PATHS")
    print("=" * 72)
    for p in paths:
        marker = "★ " if p.id == rec["id"] else "  "
        print(f"{marker}[{p.id}] {p.title} (score: {p.score})")
        print(f"    Summary: {p.summary}")
        print(f"    Rationale: {p.rationale}")
        print()
    print(f"Recommended: [{rec['id']}] {rec['title']}")
    print(f"Reason: {rec['reason']}")
    print("=" * 72)


def print_session(result: Dict[str, Any]) -> None:
    print("\n" + "=" * 72)
    print("TALNIR DEBUG SESSION")
    print("=" * 72)
    print(f"Chosen path:\n  [{result['chosen_path']['id']}] {result['chosen_path']['title']}")
    print(f"Realignment:\n  {result['realignment_note']}\n")

    print("Final aligned output:")
    print(f"  {result['final_output']}\n")

    print("Forward plan:")
    for i, step in enumerate(result["forward_plan"], 1):
        print(f"  {i}. {step}")
    print()

    print("Trace:")
    print(f"  Formation stabilized: {result['formation_stabilized']}")
    print(f"  Paths generated: {len(result['paths'])}")
    print(f"  Alignment enforced: {result['alignment_enforced']}")
    print("=" * 72 + "\n")


def save_last_session(result: Dict[str, Any], app_dir: str) -> None:
    os.makedirs(app_dir, exist_ok=True)
    out = os.path.join(app_dir, "last_talnir_session.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved session: {out}\n")


def main() -> None:
    print("\nTalnir Reasoning Debugger")
    print(conspark())
    print("Formation -> paths -> choice -> realignment.\n")

    task = input("Enter task:\n> ").strip()
    frame = build_task_frame(task)
    paths = generate_paths(frame)
    rec = recommendation(paths)

    print_frame(frame)
    print_paths(paths, rec)

    print("\nChoose a path by letter or by word.")
    print("Examples: A / B / C / D / solve / empathy / risk / business / frame\n")

    chosen_raw = input("Choose path:\n> ").strip()
    chosen_id = interpret_choice(chosen_raw, paths)
    if not chosen_id:
        raise ValueError("Invalid path choice. Use a valid letter or words like solve, empathy, risk, business, or frame.")

    chosen = next(p for p in paths if p.id == chosen_id)

    result = {
        "session_marker": conspark(),
        "timestamp": utc_now(),
        "frame": frame,
        "paths": [asdict(p) for p in paths],
        "recommendation": rec,
        "chosen_path": asdict(chosen),
        "realignment_note": f"Talnir realigned to '{chosen.title}' and constrained the output to that continuation.",
        "final_output": synthesize_output(frame, chosen),
        "forward_plan": realigned_forward_plan(frame, chosen),
        "formation_stabilized": True,
        "alignment_enforced": True,
    }

    print_session(result)
    save_last_session(result, APP_DIR)


if __name__ == "__main__":
    main()
