# Talnir Reasoning Debugger

**Same input, different chosen paths, different aligned outputs.**

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

- **visible**  
- **steerable**  
- **debuggable**  

---

## Example

**Input:**
