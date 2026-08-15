# TODO for RI-POLICY-IR-VALIDATE-003

## ticket: ticket-003
## repository: wellmanifest/policy-dsl
## intent digest: 2b72d8cd8a9d4cd094035c68a6d310d426ea947a4cda5cc629e664cae4467f5c
## authority: accepted remediation intent; todo2code and LLM output are advisory
## outcome: validate_ir enforces unique bindings, environment names and transitions, and rejects NEXT/transition endpoints absent from declared states
### non-goal 1: Do not change Policy IR schema major or close domain opcodes
### non-goal 2: Do not publish agent/report or refresh hub governance locks in this ticket
### constraint 1: Preserve inert Policy IR boundary
### constraint 2: Keep existing host hardware policies valid
### constraint 3: Stay inside ticket-003 allowedPaths
### must preserve 1: Inert Policy IR boundary
### must preserve 2: Host hardware policy fixtures
### must preserve 3: Open domain opcodes outside candidate profile
### forbidden assumption 1: Do not treat todo2code output as authority to expand allowedPaths
## required changes
- [ ] fix(remediation): action A-HARDEN-VALIDATE-IR must Add uniqueness and state-reference checks to validate_ir, update fixtures, tests, docs and digests | intent RI-POLICY-IR-VALIDATE-003 ticket ticket-003 digest 2b72d8cd8a9d4cd094035c68a6d310d426ea947a4cda5cc629e664cae4467f5c | findings F-DUP-BINDING-IR/PLANNED_NOT_IMPLEMENTED/P1, F-DUP-ENV-TRANSITION/PLANNED_NOT_IMPLEMENTED/P1, F-UNDECLARED-STATE/AMBIGUOUS_REQUIREMENT/P1 | paths `tests/policy_dsl_check.py`, `tests/test_policy_dsl.py`, `examples/valid/CONTRIBUTING.md`, `examples/invalid/duplicate-binding.policy`, `examples/invalid/duplicate-environment.policy`, `examples/invalid/duplicate-transition.policy`, `examples/invalid/undeclared-next-state.policy`, `spec/POLICY_DSL.md`, `docs/ERROR/POLICY-SEMANTIC-001.md`, `dsl-manifest.json` | dependencies none | acceptance AC-01 Unit tests cover and pass uniqueness and state-ref hardening, AC-03 Invalid fixtures reject with POLICY-SEMANTIC-001, AC-02 Self-test and CONTRIBUTING.md markdown validation pass with declared states | verification V-UNIT command command-json="python3 -m unittest discover -s tests -p 'test_*.py'" expected=exit 0 deterministic=true, V-SELF-TEST command command-json="python3 tests/policy_dsl_check.py self-test" expected=POLICY-CONFORMANCE-PASS deterministic=true, V-INVALID command command-json="python3 tests/policy_dsl_check.py validate examples/invalid/duplicate-binding.policy" expected=POLICY-SEMANTIC-001 non-zero exit deterministic=true when executed and failure must block the action | risk reversible_write authorization session_execution_authorization automation allowed preserves-user-data true | evidence result must pass.
- [ ] docs(remediation): action A-DISCOVERY must Render todo2code projections and record further gaps in DISCOVERY.md without expanding scope | intent RI-POLICY-IR-VALIDATE-003 ticket ticket-003 digest 2b72d8cd8a9d4cd094035c68a6d310d426ea947a4cda5cc629e664cae4467f5c | findings F-FOLLOWUP-DISCOVERY/AMBIGUOUS_REQUIREMENT/P2 | paths `project/ticket-003/DISCOVERY.md`, `project/ticket-003/REMEDIATION.task.md`, `project/ticket-003/REMEDIATION.todo.md` | dependencies A-HARDEN-VALIDATE-IR | acceptance AC-04 Remediation todo2code projections verified, discovery notes recorded | verification V-REMEDIATION command command-json="python3 .governance/remediation_intent.py verify-todo2code project/ticket-003/remediation-intent.dsl.json" expected=projections match byte-for-byte deterministic=true when executed and failure must block the action | risk read_only authorization not_applicable automation allowed preserves-user-data true | evidence result must pass.
