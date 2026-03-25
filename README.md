# Talnir Reasoning Debugger

Talnir exposes possible reasoning paths, lets you choose one, and forces the model to stay aligned to that decision.

## What it does

Given a single task, Talnir:

1. generates multiple candidate reasoning paths
2. recommends one path based on task signals
3. allows explicit path selection
4. realigns the output to the chosen continuation
5. shows a trace of the selected path and aligned result

## Why it matters

Most model workflows hide continuation logic behind one opaque answer.

Talnir makes continuation:

- visible
- steerable
- debuggable

## Demo behavior

Same input, different chosen paths, different aligned outputs.

This makes reasoning control explicit instead of relying on prompt guesswork.

## Example paths

- De-escalate and stabilize
- Diagnose and solve
- Contain risk first
- Optimize for business value

## Run

```bash
python3 ~/talnir_debugger/talnir_debugger.py
