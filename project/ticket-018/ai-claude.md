---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-018
---
# Participant: claude (AI agent)

## Understanding

The sales profile must ADOPT the current HOME offer instead of mirroring an
archived one, and it must not remain a second source of prices, names,
entitlements or copy.

## Execution plan

1. Commit this bounded intent.
2. Implement catalog/decision v2 reading HOME data from the locked v2 fixture,
   remove the Twin Plus rule, add the HOME-root current-version check.
3. Regenerate matrices, update tests and manifest digests; run all gates.

## Actual changes

- `reference_engine.py`: catalog/decision v2, HOME data from the locked v2 offer,
  `load_home_offer`, `compare-offer-home --home-root`, portal comparison against HOME.
- `subactor-sales.policy` VERSION 2 without the Twin Plus rule.
- Catalog v2, offer-home lock v2 (`6f38fbe`), v2 HOME fixture, portal facade projection
  from `www-sub-actor@183bb87`, regenerated decision matrix and `matrix.v2.json`.
- Removed the v1 fixture, `matrix.v1.json` and the v1 pricing HTML example.
- Tests rewritten for v2; manifest digests refreshed.

## Publication

- Merged through PR #25 as `5551a57` after Validator approval of head `9263c54`.

## Blockers

- None.
