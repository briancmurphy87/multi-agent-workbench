# summary

sandbox for experimenting with multi-agent systems

forked from this repo: 
https://github.com/briancmurphy87/interview-prep-agent

at this commit: 
https://github.com/briancmurphy87/interview-prep-agent/commit/b7a82c60d344e001a03ebbda2c92d35249a6cd10

# v0

- turning the architecture into a real starter scaffold 
- choosing a small demo corpus/query 
    - so the repo has an immediate, believable first run.

## Goal
- Get to one end-to-end run over 3–5 local docs with:
    - planner agent
    - retriever agent
    - responder agent
    - critic agent
    - simple orchestration loop
    - retrieval traces
    - per-run artifacts
- The repo should read as a general multi-agent systems project, 
  - not a resume-specific app.

## Suggested first example
- Use a small neutral corpus about a fictional open-source project called **Northstar**.
- This avoids "enterprise theater" while still creating realistic retrieval and tool-use behavior.

### Local docs for v0
Create these 5 docs under `data/corpus/docs/`:
1. `overview.md`
2. `architecture.md`
3. `roadmap.md`
4. `release_notes.md`
5. `runbook.md`

### Example end-to-end query
```plain text
What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?
```
Why this is a good v0 query:
- requires retrieval across multiple docs
- requires synthesis, not just lookup
- can be judged for grounding
- creates room for critic/retry behavior
- feels natural for a general agent workbench

```shell
python -m src.multi_agent_workbench.cli ask \
  --query "What changed in Northstar's ingestion pipeline between the current architecture and the latest release, and are there any operational caveats mentioned in the runbook?"
```

#### Expected behavior
- planner decides retrieval is needed
- retriever pulls chunks from `architecture.md`, `release_notes.md`, and `runbook.md`
- responder synthesizes answer with citations
- critic checks citations
- artifacts are written under `runs/<run_id>/`

#### Realized Output
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


## Suggested v0 milestone plan

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
