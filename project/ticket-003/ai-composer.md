# Agent plan — ticket-003 (composer)

## SESSION_EXECUTION_AUTHORIZATION

User asked to execute Policy IR harden and use todo2code/other DSLs to discover
further fixes. Proceeded within `intent.json` without a second confirmation.

## Done

1. Closed integrated `ticket-002` (`DONE/DONE`) so integration workstream could
   allocate `ticket-003`.
2. Wrote remediation intent, rendered/verified todo2code projections.
3. Implemented `validate_ir` uniqueness + state refs; fixtures; tests; docs;
   digests.
4. Discovery via remediation DSL, redup, vallm, governance drift scan →
   `DISCOVERY.md` (D-01..D-08), no scope expansion.

## Validation

- `python3 -m unittest discover -s tests -p 'test_*.py'` PASS
- `python3 tests/policy_dsl_check.py self-test` → POLICY-CONFORMANCE-PASS
- Invalid fixtures → POLICY-SEMANTIC-001
- Host policies still validate
- `remediation_intent.py verify-todo2code` PASS
