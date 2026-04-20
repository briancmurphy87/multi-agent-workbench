# multi-agent-workbench

A small, observable multi-agent system for retrieval, reasoning, tool use, and evaluation.

This repository began as a fork of `interview-prep-agent`, then was generalized into a domain-neutral sandbox for experimenting with multi-agent workflows over local document corpora.

# setup

run this from project root: 
```shell
python -m pip install -e ".[dev]"
```

## Current status

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


## v0 milestone plan

### Milestone 1: generalize the bones
- Do this first.
    - rename package and repo language
    - migrate `llm.py`
    - migrate/generalize state
    - migrate/generalize observability
    - create new CLI skeleton
- Deliverable:
    - repo runs with a generic query and dummy workflow

### Milestone 2: explicit multi-agent loop
- add planner
- add retriever
- add responder
- add critic
- wire them in `simple_loop.py`
- Deliverable:
    - one end-to-end multi-agent run over a local corpus

### Milestone 3: retrieval + artifacts
- ingest docs
- chunk docs
- search docs
- emit retrieved chunk artifacts
- emit trace artifacts
- Deliverable:
    - answer with cited chunks and trace output

### Milestone 4: eval harness
- add eval cases
- batch runner
- summary metrics
- Deliverable:
    - `evals/summaries/summary_*.json`

### Milestone 5: supervisor / retry logic
- add a retry path when critic flags poor grounding
- compare first answer vs revised answer
- Deliverable:
    - visible self-reflection / critique loop

### Milestone 6: LangGraph
- move simple loop into graph orchestration
- Deliverable:
    - repo now visibly uses a recognized multi-agent framework
