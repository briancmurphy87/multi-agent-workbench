# Runbook

Operational caveats for Northstar v2.4:

- If stream processor lag exceeds 5 minutes, operators should divert high-priority traffic to the batch fallback path.
- During replay operations, mixed use of streaming and batch paths can produce confusing timing unless trace ids are used consistently.
- Memory pressure is the leading indicator of stream backpressure.
- The warehouse loader remains the source of truth for data completeness checks.