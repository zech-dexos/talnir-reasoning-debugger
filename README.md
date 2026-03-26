# Talnir Reasoning Debugger

**Same input, different chosen paths, different aligned outputs.**

Talnir is a formation-aware reasoning debugger that stabilizes task framing, exposes candidate continuations, enables explicit path selection, and aligns outputs to the chosen reasoning path.

---

## What it does

Given a single task, Talnir:

1. stabilizes the task into an explicit formation frame  
2. generates multiple candidate reasoning paths from that frame  
3. recommends one path based on task signals  
4. allows explicit path selection  
5. realigns the output to the chosen continuation  
6. shows a trace of the selected path and aligned result  

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

Talnir separates **formation stability** from **continuation selection**, making model behavior more reliable and easier to control.

---

## Formation Layer

Before generating paths, Talnir stabilizes the task into a structured frame:

- domain  
- objective  
- asset  
- risks  
- uncertainties  
- constraints  
- strategy families  

This ensures that continuation paths are generated from a consistent and interpretable problem space rather than raw prompt signals.

---

## Example

**Input:**
Write a response to an angry customer who says our product is broken and useless

**Formation frame (simplified):**
- domain: customer_support  
- objective: preserve trust while resolving issue  
- asset: customer relationship  
- risks: escalation, loss of trust, misdiagnosis  

**Paths:**
- A -> De-escalate and stabilize  
- B -> Diagnose and solve  
- C -> Contain risk  
- D -> Optimize for business value  

**Choice:**
empathy

**Result:**
Output is aligned to a de-escalation strategy.

Run again with:
solve

Output shifts to a diagnostic / technical response.

---

## Run

```bash
python3 talnir_debugger.py
