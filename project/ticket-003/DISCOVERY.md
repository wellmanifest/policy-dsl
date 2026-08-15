# Discovery — further standards gaps (advisory)

Authority: ticket-003 remediation intent + deterministic checkers.
todo2code / code2llm / redup / vallm / governance drift scan are **advisory**.
They do **not** expand `allowedPaths` or authorize new workstreams.

## Closed in this ticket

- `validate_ir` duplicate binding / environment name / transition edge
- `NEXT` / `TRANSITION` → declared `STATE`
- `CONTRIBUTING.md` declares `STATE PLAN|VALIDATION|PUBLICATION`
- Invalid fixtures + unit tests + digest refresh

## Follow-ups (out of scope here)

| ID | Gap | Suggested home | Priority |
| --- | --- | --- | --- |
| D-01 | Publish `wellmanifest.agent/report/v1` to hub (`new-project`); schema exists only on `ticket/077-agent-report-identity` | `wellmanifest/new-project` publication auth after 077 | P0 |
| D-02 | Refresh `policy-dsl` `.governance` lock: hub has `domainContracts` (ticket-085); fork missing it; `$id` `.com` vs `.dev` | policy-dsl TODO “immutable locks” | P1 |
| D-03 | Document / optional schema profile for **IR vs candidate opcodes** (open domain vs GBNF `REQUIRE|ALLOW|REPORT|VALIDATE|RECORD`) | policy-dsl next FEATURE | P2 |
| D-04 | JSON Schema cannot express unique `rules[].id` / `bindings[].name`; consider `unevaluated*` notes or keep checker-only | policy-dsl docs/schema note | P3 |
| D-05 | `ENV_FILE` path uniqueness not enforced (VARIABLE/SECRET names now are) | policy-dsl patch | P3 |
| D-06 | `vallm`: `validate_ir` CC=76 / 132 lines after harden — split uniqueness helpers (no behavior change) | policy-dsl refactor | P2 |
| D-07 | `placement` still optional on old tickets; define when required for new SERVICE/FEATURE | new-project rule-enforcement | P1 |
| D-08 | Multiple report schemas (`agent/report`, workspace-lifecycle, branch-lifecycle) need a naming map | new-project + agent pack | P2 |

## Tool evidence

- remediation: `validate` + `render-todo2code` + `verify-todo2code` PASS
- `redup scan .`: 0 duplicate groups in scanned sources
- `vallm batch tests/policy_dsl_check.py`: complexity review only (D-06); tree-sitter download noise ignored
- `code2llm` on single-file `--fast`: no useful graph (tool/env limitation); ignored for authority
- governance drift vs `../new-project/governance`: `manifest.schema.json`, `diagnostics.schema.json`, `remediation-intent.schema.json`
- hub `agent-report.schema.json`: **ABSENT**

## Non-actions

- No schema major / opcode enum close
- No hub governance write from this ticket
- No agent/report publication
