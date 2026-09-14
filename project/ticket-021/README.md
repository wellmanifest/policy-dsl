# Ticket 021: Document the sales profile v2 model and HOME offer adoption

- **ID**: ticket-021
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Session execution authorization**: user requested implementation of wellmanifest/policy-dsl#23 follow-ups and autonomous continuation (2026-09-14)
- **Created**: 2026-09-14
- **Depends on**: ticket-018 (PR #25), ticket-020 (PR #27)

## Goal and scope

The evaluator (ticket-018) and schemas (ticket-020) implement the sales
profile v2, but the documentation still described the v1 model: mirrored
prices, Operations Plus and Twin Plus, twin counts, Polish labels held by this
pack, `decision/v1` and the removed pricing HTML example.

This ticket rewrites `docs/SALES_POLICY_PROFILE.md`, `profiles/sales/README.md`,
`profiles/sales/ADOPTION_PL.md` (including a v1 → v2 migration table) and
`examples/sales/README.md`, updates the product naming sections of
`docs/DOMAIN_VOCABULARY.md` and `docs/DOMAIN_VOCABULARY_PL.md`, and refreshes
the manifest digests. The root `README.md` sales paragraph belongs to the
`governance` workstream and is left for a separate change.

## Acceptance criteria

- [x] AC-01: full unit suite passes, including manifest digest bindings (52 tests).
- [ ] AC-02: `./project/governance-check.sh` passes on the published head.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
