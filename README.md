# multi-agent-workbench

A compact multi-agent RAG workbench for experimenting with:

* planner / retriever / responder / critic / supervisor workflows
* explicit execution traces and artifacts
* dataset-driven evaluation (LLM-as-judge style)
* interchangeable orchestration layers (plain Python vs LangGraph)

---

## Summary

This repo is a minimal but complete example of:

> how to build, observe, evaluate, and iteratively improve a multi-agent LLM system — and evolve it from simple orchestration to graph-based execution without breaking behavior.

The project began with a deterministic fictional corpus (“Northstar”) and was later extended to operate against a real-world SQLite documentation corpus.

---

## Why this repo exists

Most “AI agent” demos are:

* opaque (no traceability)
* untestable (no eval harness)
* brittle (no retry or supervision loop)

This repo is a minimal but **fully observable + testable** system that demonstrates:

* structured multi-agent orchestration
* retrieval-augmented generation (RAG)
* supervisor-driven retry loops
* explicit execution traces and artifacts
* dataset-driven evaluation
* iterative improvement through eval feedback

---

## Architecture

The system is built around a shared mutable state object (`WorkbenchState`) and five agents:

* **Planner** → decides execution strategy
* **Retriever** → selects relevant document chunks
* **Responder** → drafts an answer
* **Critic** → evaluates grounding / citations
* **Supervisor** → decides: accept, retry, or finalize

Key properties:

* all agents operate on shared state
* every step emits structured trace events
* artifacts are persisted per run
* retry is **supervisor-driven**, not heuristic
* insufficient-evidence handling is explicitly evaluated

---

## Workflow backends

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

Install:

```bash
python -m pip install -e ".[dev]"
```

Run an example query:

```bash
OPENAI_MODEL=stub-model python -m multi_agent_workbench.cli ask \
  --query "retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?"
```

Inspect run artifacts:

```bash
runs/<run_id>/
```

Artifacts include:

* `trace.json`
* `retrieved_chunks.json`
* `final_answer.md`
* `artifacts.json`

---

## Example run (end-to-end)

### Query

```text
retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?
```

### Planner decision

From:

```python
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

```text
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

```text
retry_with_citations
```

Meaning: the first draft answer lacked sufficient grounding.

### Supervisor decision

From:

```python
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

```text
Northstar moved from a batch-first ingestion design to adding a streaming path for high-priority traffic, reducing latency to under 90 seconds [release_notes-0].

The runbook notes that if stream processor lag exceeds 5 minutes, operators should divert traffic to the batch fallback path, and memory pressure is a key indicator of backpressure [runbook-0].
```

---

## What this demonstrates

* planner routes correctly to retrieval
* retriever surfaces relevant cross-document evidence
* responder synthesizes an answer
* critic detects insufficient grounding
* supervisor triggers retry
* retry produces improved grounded output

---

## Real-world corpus: SQLite documentation

After validating the workflow on a deterministic fictional corpus, the system was extended to run against a real documentation corpus built from selected SQLite docs.

Corpus location:

```text
data/corpus/sqlite/
```

Included topics:

* SQLite architecture
* WAL mode
* file locking and concurrency
* transactions
* limits
* recent release changes

Example real-world queries:

```text
What caveats does SQLite document for WAL mode?
```

```text
How does SQLite describe concurrency behavior across WAL mode and locking?
```

```text
What are the tradeoffs between WAL mode and traditional rollback journaling?
```

```text
Which engineer originally approved WAL mode for release in SQLite?
```

The final query above is intentionally unanswerable from the corpus and is used to validate insufficient-evidence handling.

---

## SQLite evaluation suite

Run SQLite evals:

```bash
OPENAI_MODEL=stub-model python -m multi_agent_workbench.cli eval \
  --cases-dir evals/cases_sqlite \
  --corpus-dir data/corpus/sqlite \
  --outputs-dir evals/outputs_sqlite \
  --summaries-dir evals/summaries_sqlite
```

Latest summary:

```json
{
  "num_cases": 5,
  "retrieval_accuracy": 1.0,
  "planner_mode_accuracy": 1.0,
  "planner_tools_accuracy": 1.0,
  "planner_retrieval_accuracy": 1.0,
  "supervisor_action_accuracy": 1.0,
  "insufficient_evidence_accuracy": 1.0,
  "retry_execution_accuracy": 1.0
}
```

This demonstrates:

* planner routing generalized from toy docs to real technical documentation
* retrieval surfaced SQLite evidence across WAL, locking, transactions, and release notes
* critic/supervisor loop handled both grounded answers and insufficient-evidence cases
* eval metrics were used to diagnose and fix planner-routing, citation-detection, and insufficient-evidence behavior

---

## Eval-driven iteration

The SQLite corpus exposed several realistic failure modes:

1. Planner initially routed SQLite questions as direct-answer queries instead of retrieval queries.
2. The critic initially accepted stub answers because bracketed chunk IDs in echoed evidence were mistaken for citations.
3. Insufficient-evidence answers were initially mishandled because explicit refusal language was treated as uncited output.

Each issue was fixed through targeted changes and rerun against the same eval suite until the workflow produced correct planner, retrieval, retry, supervisor, and insufficient-evidence behavior.

This iterative eval/debug/fix loop was a core design goal of the project.

---

## Project structure

```text
agents/           → planner, retriever, responder, critic, supervisor
workflows/        → SimpleWorkflow + LangGraphWorkflow
state/            → shared state model
retrieval/        → corpus + chunking
evals/            → datasets + scoring
observability/    → traces + artifact writers
llm/              → stub + OpenAI client
```

---

## What’s interesting here (for engineers)

* explicit imperative vs graph orchestration comparison
* supervisor-driven retry loop (bounded and testable)
* artifact-first debugging (not prompt guessing)
* eval harness integrated into development loop
* real-corpus iteration and failure analysis
* extensible architecture for additional agents, tools, or corpora

---

## Next extensions

* semantic eval scoring beyond keyword matching
* tool-use agent (search, calculator, API calls)
* multi-hop planning
* embedding-backed retrieval
* cost and latency tracking
* trace visualization UI

---
