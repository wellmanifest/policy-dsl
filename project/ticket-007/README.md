# Ticket 007: Pin sales catalog to subactor/offer HOME digest

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-16

## Goal and scope

Fail-closed ADOPT of commercial amounts from `subactor/offer` HOME into the
policy-dsl sales projection. Add `offer-home.lock.json`, CI fixture,
`compare-offer-home`, and remove amount literals from the structural catalog
expectation table. Keep `examples/sales/subactor-pricing-section.html` as a
facade example (no HTML edits; already OTP-aligned).

## Acceptance criteria

- [x] AC-01: Lock pins `subactor-cloud` v1 digest; fixture bytes match.
- [x] AC-02: `compare-offer-home` rejects digest and amount mirror drift.
- [x] AC-03: `validate-catalog` runs HOME compare against the locked fixture.
- [x] AC-04: Unit tests pass; `dsl-manifest.json` digests refreshed.
- [x] AC-05: Pricing HTML left unchanged as non-SSOT facade.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue the finish-006-then-pin plan authorizes this ticket.
