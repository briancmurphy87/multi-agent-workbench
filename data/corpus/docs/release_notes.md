# Release Notes - v2.4

Northstar v2.4 introduced a streaming ingestion path for high-priority event classes.

Changes:
- added a stream processor between ingest gateway and normalizer
- reduced typical end-to-end latency for priority traffic from 15 minutes to under 90 seconds
- introduced conversation-style trace ids that propagate across ingest gateway, processor, and loader logs
- added a fallback path to batch mode when the stream processor is unavailable

Known limitations:
- low-priority traffic still follows the older batch path
- stream backpressure can increase memory usage during spikes