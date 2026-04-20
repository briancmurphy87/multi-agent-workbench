# Northstar Architecture

Northstar's ingestion pipeline historically used a batch-first design. Events were first written to object storage, then normalized by a scheduled transformer job every 15 minutes.

This design was simple but introduced delay before events became queryable. Replay operations were reliable, but operators had limited visibility into per-stage lag.

The current architecture includes three main stages:
1. ingest gateway
2. normalizer
3. warehouse loader