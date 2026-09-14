---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-020
---
# Participant: claude (AI agent)

## Understanding

The v2 contracts exist in code and fixtures but not in the published schemas.

## Execution plan

1. Commit this bounded intent.
2. Replace the three sales schemas with v2 versions and add the conformance test.
3. Refresh manifest digests and run all gates.

## Actual changes

- `schemas/sales-offer-catalog.schema.json`, `sales-request.schema.json`, `sales-decision.schema.json`: v2 contracts with versioned `$id`.
- `tests/test_sales_profile.py`: dependency-free schema subset validator and conformance test.
- `dsl-manifest.json`: refreshed digests.

## Blockers

- None.
