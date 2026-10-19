# Policy Compaction Architecture (`wellmanifest.policy/v1`)

<!-- docs:section:summary -->
## 1. Summary and Problem Diagnosis

Abstract policy documents (`CONTRIBUTING.md`, `POLICY.md`, `*.policy`, `*.lifecycle`) suffer from four structural bloat anti-patterns when rules are authored as flat, unfactored lists:

1. **`POLICY-COMPACT-001` (Prose-as-Symbol)**: Encoding whole prose sentences as underscore-joined symbols (`UNMERGED_IMPLEMENTATION_HEAD_RETAINS_ACTIVE_TICKET_AUTHORITY...`, >48 chars) instead of binding atomic domain symbols to `wellmanifest/oql` operation IDs or JSON Schema `$id`s.
2. **`POLICY-COMPACT-002` (Transition Fan-In Duplication)**: Repeating `STATE` and `TRANSITION <ORIGIN> -> <TARGET> WHEN <GUARD>` lines across 8–12 origin states that share the same target and guard.
3. **`POLICY-COMPACT-003` (Repeated Guard Prefix)**: Repeating an identical contextual prefix (`WHEN HOST_KIND = "PRODUCTION_SERVER" AND ...` or `WHEN GOVERNANCE_MANIFEST.docker.required = TRUE AND ...`) across 3–15 rules.
4. **`POLICY-COMPACT-004` (Cloned Directive Bundles)**: Copying 3–7 identical `DO`, `FORBID`, `ASSERT`, and `NEXT` directives across every rejection or acceptance rule.

<!-- docs:section:scope -->
## 2. Standard Synergy Across `wellmanifest/*`

Instead of inventing a new incompatible policy language, Policy Compaction reuses and composes existing `wellmanifest/*` standards while keeping `schemas/policy-ir.schema.json` (`wellmanifest.policy/ir/v1`) closed and unchanged:

| Standard | Role in Reducing Policy Bloat |
| :--- | :--- |
| **`wellmanifest/policy-dsl`** | Provides compile-time desugaring (`STATES`, `TRANSITION [...]`, `SCOPE WHEN`, `TEMPLATE` / `DO APPLY_TEMPLATE`) and static compaction auditing (`policy_dsl_check.py audit`). |
| **`wellmanifest/ssot` & `wellmanifest/reuse`** | Prohibits restating `POLICY.md` (`P-*`) invariants inside `CONTRIBUTING.md` (`C-*`); procedural rules reference normative invariants via `DO APPLY P-<DOMAIN>-<NNN>`. |
| **`wellmanifest/modularity`** | Enforces one exporter per domain module (`<= 8` public exports) and moves multi-attribute eligibility matrices out of `.policy` text into closed catalog JSON (`offer-catalog.json`, `strategy-catalog.json`). |
| **`wellmanifest/lifecycle`** | Owns canonical state graphs (`.lifecycle`) and transition authority (`actor_types`, `authority`), eliminating duplicated state-machine prose in Markdown carriers. |
| **`wellmanifest/env-dsl`** | Extracts environment constants and hardware thresholds out of `.policy` files into typed `.env.dsl` layers (`ENV_FILE` / `wellmanifest.env`). |
| **`wellmanifest/oql` & `wellmanifest/poa`** | Replaces 80-character prose symbols with typed CQRS/OQL operation references and POA proposal opcodes (`REQUIRE`, `ALLOW`, `REPORT`, `VALIDATE`, `RECORD`). |

<!-- docs:section:findings -->
## 3. Compile-Time Desugaring Constructs (`wellmanifest.policy/v1 -> ir/v1`)

All four compact constructs normalize deterministically in `PolicyParser` (`tests/policy_dsl_check.py`) to standard Policy IR v1 nodes:

### Before (31 lines, verbose flat policy)

```dsl
STATE START
STATE EDIT
STATE VALIDATION
STATE BLOCKED
STATE REJECTED
TRANSITION START -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
TRANSITION EDIT -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
TRANSITION VALIDATION -> BLOCKED WHEN EVIDENCE_MISSING = TRUE

RULE R-LOW-RAM TYPE REQUIRED
WHEN HOST_KIND = "PRODUCTION_SERVER" AND RAM_GIB < 8
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
DO RECORD REJECT_REASON "RAM_BELOW_MINIMUM"
NEXT REJECTED

RULE R-LOW-CPU TYPE REQUIRED
WHEN HOST_KIND = "PRODUCTION_SERVER" AND VCPU < 4
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
DO RECORD REJECT_REASON "VCPU_BELOW_MINIMUM"
NEXT REJECTED
```

### After (18 lines, 42% reduction, bit-for-bit identical Policy IR v1)

```dsl
STATES [START, EDIT, VALIDATION, BLOCKED, REJECTED]
TRANSITION [START, EDIT, VALIDATION] -> BLOCKED WHEN EVIDENCE_MISSING = TRUE

TEMPLATE REJECT_HOST
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
NEXT REJECTED
END

SCOPE WHEN HOST_KIND = "PRODUCTION_SERVER"
RULE R-LOW-RAM TYPE REQUIRED
WHEN RAM_GIB < 8
DO APPLY_TEMPLATE REJECT_HOST
DO RECORD REJECT_REASON "RAM_BELOW_MINIMUM"

RULE R-LOW-CPU TYPE REQUIRED
WHEN VCPU < 4
DO APPLY_TEMPLATE REJECT_HOST
DO RECORD REJECT_REASON "VCPU_BELOW_MINIMUM"
END
```

<!-- docs:section:actions -->
## 4. Automated Compaction Audit (`policy_dsl_check.py audit`)

Run the dependency-free static analyzer on any `.policy` or Markdown carrier:

```bash
python3 tests/policy_dsl_check.py audit examples/hosting/subactor-production-server.policy
python3 tests/policy_dsl_check.py audit ../new-project/CONTRIBUTING.md --markdown
```

Empirical audit results on active ecosystem carriers:
- `examples/hosting/subactor-production-server.policy`: **5 findings** (`11` rules sharing `HOST_KIND = "PRODUCTION_SERVER"`, `7` rules sharing the 3-directive reject bundle, `2` rules sharing the 7-directive fit bundle; **29 directive/guard lines saved**).
- `wellmanifest/new-project/CONTRIBUTING.md`: **5 findings** (`131` prose-encoded symbols `POLICY-COMPACT-001`, `10` fan-in transitions to `BLOCKED` `POLICY-COMPACT-002`, and `3` repeated guard groups `POLICY-COMPACT-003`).
