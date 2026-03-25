# Talnir Reasoning Debugger

Same input, different chosen paths, different aligned outputs.

Talnir exposes possible reasoning paths, lets you choose one, and forces the model to stay aligned to that decision.

---

## What it does

Given a single task, Talnir:

1. generates multiple candidate reasoning paths
2. recommends one path based on task signals
3. allows explicit path selection
4. realigns the output to the chosen continuation
5. shows a trace of the selected path and aligned result

---

## Why it matters

Most LLM workflows produce a single opaque answer.

This makes reasoning:
- hidden
- hard to control
- difficult to debug

Talnir makes reasoning:
- visible
- steerable
- debuggable

---

## Example

Input:
Write a response to an angry customer

Paths:
A -> De-escalate and stabilize
B -> Diagnose and solve
C -> Contain risk
D -> Optimize for business value

Choice:
empathy

Result:
Output is aligned to a de-escalation strategy.

Run again with:
solve

Output shifts to a diagnostic / technical response.

---

## Run

python3 talnir_debugger.py

---

## Core claim

Talnir is a reasoning debugger for continuation control in LLM systems.
