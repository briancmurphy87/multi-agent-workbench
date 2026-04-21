
# multi-agent-workbench

A compact multi-agent RAG workbench for experimenting with:

* planner / retriever / responder / critic / supervisor workflows
* explicit execution traces and artifacts
* dataset-driven evaluation (LLM-as-judge style)
* interchangeable orchestration layers (plain Python vs LangGraph)

---

## Summary

This repo is a minimal but complete example of:

> how to build, observe, and evaluate a multi-agent LLM system — and evolve it from simple orchestration to graph-based execution without breaking behavior.

## Why this repo exists

Most “AI agent” demos are:

* opaque (no traceability)
* untestable (no eval harness)
* brittle (no retry or supervision loop)

This repo is a minimal but **fully observable + testable** system that shows:

* how to structure a multi-agent workflow
* how to debug it via artifacts
* how to evaluate it systematically
* how to swap orchestration layers without rewriting logic

---

## Architecture

The system is built around a shared state object (`WorkbenchState`) and five agents:

* **Planner** → decides execution strategy
* **Retriever** → selects relevant document chunks
* **Responder** → drafts an answer
* **Critic** → evaluates grounding / citations
* **Supervisor** → decides: accept, retry, or finalize

Key properties:

* all agents operate on shared mutable state
* every step emits structured trace events
* artifacts are persisted per run
* retry is **supervisor-driven**, not heuristic

---

### 1. SimpleWorkflow (baseline)

* explicit Python control flow
* easy to reason about
* ideal for debugging and iteration

### 2. LangGraphWorkflow

* graph-based execution model
* explicit branching and retry loops
* same agents, state, artifacts, and eval harness

Both workflows produce identical outputs and pass the same tests.

---

## Quickstart

```bash
python -m pip install -e ".[dev]"
```

Run an example:

```bash
OPENAI_MODEL=stub-model python -m multi_agent_workbench.cli ask \
  --query "retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?"
```

Then inspect:

```bash
runs/<run_id>/
```

Artifacts:

* `trace.json`
* `retrieved_chunks.json`
* `final_answer.md`
* `artifacts.json`

---

## Example run (end-to-end)

### Query

```
retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?
```

### Planner decision
From:
```
state.artifacts["planner"]
```

Content:
```json
{
  "mode": "retrieve",
  "needs_retrieval": true,
  "needs_tools": false,
  "answer_strategy": "synthesize_across_docs",
  "rationale": "The query requires synthesizing changes across architecture and release notes, and extracting operational caveats from the runbook."
}
```

### Retrieved evidence (top chunks)

Output snippet of form `[{doc_id}]` followed by first ~1-2 lines
```
[release_notes-0]
Northstar v2.4 introduced a streaming ingestion path...
reduced latency to under 90 seconds...

[runbook-0]
If stream processor lag exceeds 5 minutes, operators should divert traffic...
Memory pressure is the leading indicator of backpressure...

[architecture-0]
Northstar historically used a batch-first ingestion design...
```

### Critic verdict
From:
```
state.critic_verdict
```
Content: 
```
retry_with_citations
```
Meaning: The first draft answer lacked sufficient grounding.

### Supervisor decision
From:
```
state.artifacts["supervisor"]
```
Content:
```json
{
  "action": "retry_responder",
  "rationale": "Critic requested a revised answer with better citation support."
}
```

### Final answer
From:
```
final_answer.md
```
Content: 
```
Northstar moved from a batch-first ingestion design to adding a streaming path for high-priority traffic, reducing latency to under 90 seconds [release_notes-0].

The runbook notes that if stream processor lag exceeds 5 minutes, operators should divert traffic to the batch fallback path, and memory pressure is a key indicator of backpressure [runbook-0].
```

## What this demonstrates

* planner routes correctly to retrieval
* retriever surfaces relevant cross-document evidence
* responder synthesizes an answer
* critic detects missing citations
* supervisor triggers retry
* retry produces improved grounded output

---

## Evaluation summary

Run:

```bash
python -m multi_agent_workbench.cli eval
```

Writes output to:

```
evals/summaries/summary.json
```

Example metrics:

* planner accuracy
* retrieval correctness
* supervisor action accuracy
* retry execution correctness

This turns the system into something you can **measure, not just demo**.

Snippet of output content:
```json
{
  "num_cases": 4,
  "avg_keyword_hit_rate": 0.3958333333333333,
  "retrieval_accuracy": 0.75,
  "planner_mode_accuracy": 0.75,
  "planner_tools_accuracy": 1.0,
  "planner_retrieval_accuracy": 0.75,
  "supervisor_action_accuracy": 1.0,
  "insufficient_evidence_accuracy": 1.0,
  "retry_execution_accuracy": 1.0,
  "results": [
    {
      "case_id": "northstar_change_summary",
      "query": "What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?",
      "planner_decision": {
        "mode": "retrieve",
        "needs_retrieval": true,
        "needs_tools": false,
        "answer_strategy": "synthesize_across_docs",
        "rationale": "The query asks for synthesis across multiple documents."
      },
...
    {
      "case_id": "northstar_runbook_only",
      "query": "What operational caveats does the Northstar runbook mention for v2.4?",
      "planner_decision": {
        "mode": "retrieve",
        "needs_retrieval": true,
        "needs_tools": false,
        "answer_strategy": "synthesize_across_docs",
        "rationale": "The query asks for synthesis across multiple documents."
      },
      "supervisor_decision": {
        "action": "accept",
        "rationale": "Critic accepted the answer and a draft is present.",
        "retry_instruction": null
      },
      "critic_verdict": "accept",
      "retrieved_count": 5,
      "retry_count": 0,
      "final_answer": "STUB_RESPONSE\n\nSystem prompt: You are a careful research assistant. Answer only from provided evidence. If evidence is insufficient, say so. Include c...\nUser prompt: Question:\nWhat operational caveats does the Northstar runbook mention for v2.4?\n\nEvidence:\n[runbook-0] # Runbook\n\nOperational caveats for Northstar v2.4:\n\n- If stream processor lag exceeds 5 minutes, operators should divert high-priority tr...",
      "score": {
        "keyword_hit_rate": 0.25,
        "retrieval_used_correctly": true,
        "produced_answer": true,
        "planner_mode_correct": true,
        "planner_tools_correct": true,
        "planner_retrieval_correct": true,
        "supervisor_action_correct": true,
        "insufficient_evidence_handled_correctly": true,
        "retry_executed_correctly": true
      }
    }
  ]
}
```
---

## Real corpora (beyond the toy example)

The repo includes a small fictional corpus (**Northstar**) for deterministic tests.

The same system can be run against real-world documentation, such as:

* SQLite docs (recommended first target)
* Kubernetes docs
* RFCs (e.g. HTTP / RFC 9110)
* Python documentation

Example real queries:

* “What changed in SQLite JSON support across recent releases?”
* “What operational caveats are mentioned for WAL mode?”
* “How does Kubernetes describe Deployment vs StatefulSet tradeoffs?”

---

## Project structure

```
agents/           → planner, retriever, responder, critic, supervisor
workflows/        → SimpleWorkflow + LangGraphWorkflow
state/            → shared state model
retrieval/        → corpus + chunking
evals/            → dataset + scoring
observability/    → traces + artifact writers
llm/              → stub + OpenAI client
```

---

## What’s interesting here (for engineers)

* explicit state machine vs graph orchestration comparison
* supervisor-driven retry loop (bounded, testable)
* artifact-first debugging (not prompt guessing)
* eval harness integrated into development loop
* easy extension point for tools, memory, or multi-step planning

---

## Next extensions

* real-world corpus ingestion (SQLite / RFCs)
* tool-use agent (search, calculator, API calls)
* multi-hop planning (planner chaining steps)
* caching + cost tracking
* UI for trace visualization

---

