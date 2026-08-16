# Ticket 009: LC-031 durable compare-www-plans fixture

- **ID**: ticket-009
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-16

## Goal and scope

Add a durable `compare-www-plans` CI fixture and lock under `profiles/sales`
aligned to `offer://subactor/offer/subactor-cloud/v1`. Unit tests must pass
without a live `www-sub-actor` checkout. Do not create a second price SSOT.

## Acceptance criteria

- [x] AC-01: `examples/sales/fixtures/www-plans.facade.json` +
  `profiles/sales/www-plans.lock.json` exist and pin the offer URI.
- [x] AC-02: Unit tests accept the locked fixture and reject entitlement drift.
- [x] AC-03: Docs / conformance command use the fixture path; digests refreshed.
- [x] AC-04: Live www compare remains optional when the checkout is present.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to finish remaining LC tickets (kontynuuj / LC-031) authorizes
this ticket through publication via the protected delivery process.
