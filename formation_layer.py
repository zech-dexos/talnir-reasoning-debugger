#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Dict, List, Any


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    return text


def detect_domain(task: str) -> str:
    t = task.lower()

    if any(x in t for x in ["customer", "client", "refund", "support", "complaint", "angry", "frustrated"]):
        return "customer_support"
    if any(x in t for x in ["model", "agent", "pipeline", "drift", "llm", "debug", "reasoning"]):
        return "ai_systems"
    if any(x in t for x in ["budget", "revenue", "lease", "buy", "cost", "team", "stakeholder"]):
        return "business"
    if any(x in t for x in ["risk", "harm", "damage", "unsafe", "critical", "governance", "safety"]):
        return "risk_control"
    return "general"


def infer_objective(task: str, domain: str) -> str:
    if domain == "customer_support":
        return "respond effectively while preserving trust"
    if domain == "ai_systems":
        return "diagnose failure modes and improve controllability"
    if domain == "business":
        return "maximize value while minimizing waste"
    if domain == "risk_control":
        return "reduce downside before optimization"
    return "produce the best next action for the task"


def infer_asset(domain: str) -> str:
    if domain == "customer_support":
        return "customer trust"
    if domain == "ai_systems":
        return "system reliability"
    if domain == "business":
        return "business leverage"
    if domain == "risk_control":
        return "safe operating state"
    return "task outcome"


def infer_risks(task: str, domain: str) -> List[str]:
    risks: List[str] = []

    if domain == "customer_support":
        risks += ["tone escalation", "loss of trust", "misdiagnosis"]
    elif domain == "ai_systems":
        risks += ["reasoning drift", "misframed continuation set", "wasted debugging cycles"]
    elif domain == "business":
        risks += ["low-leverage execution", "avoidable cost", "bad prioritization"]
    elif domain == "risk_control":
        risks += ["unsafe continuation", "damage escalation", "missed stop condition"]
    else:
        risks += ["misframing", "wasted effort", "wrong next step"]

    t = task.lower()
    if "broken" in t:
        risks.append("unverified failure claim")
    if "drift" in t:
        risks.append("unstable formation")
    if "angry" in t or "frustrated" in t:
        risks.append("emotional volatility")

    return list(dict.fromkeys(risks))


def infer_uncertainties(domain: str) -> List[str]:
    if domain == "customer_support":
        return ["actual defect cause", "severity of issue", "best first response strategy"]
    if domain == "ai_systems":
        return ["where drift originates", "whether formation or selection is failing", "highest-value debugging step"]
    if domain == "business":
        return ["best leverage point", "true opportunity cost", "highest-value next move"]
    if domain == "risk_control":
        return ["highest-risk variable", "damage boundary", "safe continuation point"]
    return ["dominant unknown", "best framing", "best next move"]


def infer_constraints(domain: str) -> List[str]:
    if domain == "customer_support":
        return ["do not escalate", "do not overpromise", "preserve credibility"]
    if domain == "ai_systems":
        return ["keep path choice explicit", "do not confuse formation with selection", "preserve debuggability"]
    if domain == "business":
        return ["preserve resources", "avoid low-return effort", "keep decisions explainable"]
    if domain == "risk_control":
        return ["reduce downside first", "respect stop conditions", "avoid unnecessary harm"]
    return ["keep output coherent", "keep path choices explicit"]


def strategy_families(domain: str) -> List[str]:
    if domain == "customer_support":
        return ["de-escalate", "diagnose", "contain_risk", "optimize_value"]
    if domain == "ai_systems":
        return ["diagnose", "stabilize_frame", "contain_risk", "optimize_value"]
    if domain == "business":
        return ["optimize_value", "diagnose", "contain_risk", "defer"]
    if domain == "risk_control":
        return ["contain_risk", "diagnose", "de-escalate", "defer"]
    return ["diagnose", "contain_risk", "optimize_value", "de-escalate"]


def build_task_frame(task: str) -> Dict[str, Any]:
    task = clean_text(task)
    domain = detect_domain(task)

    return {
        "task": task,
        "domain": domain,
        "objective": infer_objective(task, domain),
        "asset": infer_asset(domain),
        "risks": infer_risks(task, domain),
        "uncertainties": infer_uncertainties(domain),
        "constraints": infer_constraints(domain),
        "strategy_families": strategy_families(domain),
    }
