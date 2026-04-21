<!-- TOC -->
* [multi-agent-workbench](#multi-agent-workbench)
* [setup](#setup)
* [Current status (v0)](#current-status-v0)
    * [First example corpus](#first-example-corpus)
    * [Example Query](#example-query)
      * [Running from Command Line](#running-from-command-line)
        * [You Should See](#you-should-see)
        * [Realized Output](#realized-output)
    * [Run artifacts](#run-artifacts)
  * [v0 milestone plan](#v0-milestone-plan)
    * [Milestone 1: generalize the bones](#milestone-1-generalize-the-bones)
    * [Milestone 2: explicit multi-agent loop](#milestone-2-explicit-multi-agent-loop)
    * [Milestone 3: retrieval + artifacts](#milestone-3-retrieval--artifacts)
    * [Milestone 4: eval harness](#milestone-4-eval-harness)
    * [Milestone 5: supervisor / retry logic](#milestone-5-supervisor--retry-logic)
    * [Milestone 6: LangGraph](#milestone-6-langgraph)
<!-- TOC -->


# multi-agent-workbench

- A compact multi-agent RAG workbench 
- for experimenting with planner/retriever/responder/critic/supervisor workflows over a local corpus with: 
  - explicit traces
  - artifacts
  - evals


This repository began as a fork of `interview-prep-agent`, then was generalized into a domain-neutral sandbox for experimenting with multi-agent workflows over local document corpora.

# setup

run this from project root: 
```shell
python -m pip install -e ".[dev]"
```

# Example run (multi-agent workflow)

This example shows how the system processes a query end-to-end using:

- planner → decides execution strategy
- retriever → fetches relevant document chunks
- responder → drafts an answer
- critic → evaluates grounding and citations
- supervisor → decides whether to accept, retry, or finalize

## Step 1: Run a real example
```shell
OPENAI_MODEL=stub-model python -m multi_agent_workbench.cli ask \
  --query "Retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?"
```

Then open:
```shell
runs/<run_id>/
```

And grab:
- `trace.json`
- `retrieved_chunks.json`
- `final_answer.md`
- `artifacts.json`

## Step 2: Extract the pieces

From artifacts, you want to manually pull:

### Query

```
Retry-demo: what changed in Northstar's ingestion pipeline and what operational caveats are mentioned in the runbook?
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
- planner correctly routes the query to retrieval
- retriever gathers evidence across multiple documents
- responder synthesizes a grounded answer
- critic detects missing citations in the first draft
- supervisor triggers a retry with stricter instructions
- final answer is improved and properly grounded


## Evaluation summary

trimmed version of contents generated at `evals/summaries/summary.json`:

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

# Current status (v0)

v0 focuses on one end-to-end workflow over a small local corpus:
- planner agent
- retriever agent
- responder agent
- critic agent
- simple orchestration loop
- retrieval traces
- per-run artifacts

The goal is to make agent runs easy to inspect, debug, and evaluate.


### First example corpus
The initial demo corpus is a fictional open-source data platform called **Northstar**.

Documents live under `data/corpus/docs/`:
1. `overview.md`
2. `architecture.md`
3. `roadmap.md`
4. `release_notes.md`
5. `runbook.md`

### Example Query

```plain text
What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?
```

This is a good first query because it requires:
- retrieval across multiple documents
- synthesis rather than simple lookup
- grounded answer generation
- critic validation
- per-run tracing


#### Running from Command Line
```shell
python -m multi_agent_workbench.cli ask \
  --query "What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?"
```
##### You Should See
- planner decides retrieval is needed
- retriever pulls chunks from `architecture.md`, `release_notes.md`, and `runbook.md`
- responder synthesizes answer with citations
- critic checks citations
- artifacts are written under `runs/<run_id>/`

##### Realized Output
```plain text
STUB_RESPONSE

System prompt: You are a careful research assistant. Answer only from provided evidence. If evidence is insufficient, say so. Include c...
User prompt: Question:
What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?

Evidence:
[overview-0] # Northstar Overview

Northstar is an ...

Artifacts written to: runs/048e07f6-2f98-477a-be0e-f4e7b7bc9b19
```

### Run artifacts
Each run writes artifacts to:
```plain text
runs/<run_id>/
```
Current outputs include:
- `final_answer.md`
- `trace.json`
- `retrieved_chunks.json`
- `artifacts.json`

