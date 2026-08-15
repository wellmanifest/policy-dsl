# Digital-twin domain vocabulary

Status: non-normative application guidance for Policy DSL v1 consumers.

## Naming decision

Use **agent operation** (`AGENT_OPERATION`, Polish: **operacja agenta**) as the
product and metering term that replaces the ambiguous user-facing word
"action". Keep events, tasks, runs and policy effects as separate concepts.

| Canonical term | Polish UI term | Meaning | Metered by default |
| --- | --- | --- | --- |
| `EVENT` | zdarzenie | An immutable fact observed in the twin or an integrated system. It may trigger work but is not work itself. | No |
| `TASK` | zadanie | A requested business outcome assigned to an agent or workflow. | No |
| `TASK_RUN` | wykonanie zadania | One bounded attempt to complete a task. A retry is a new run only when the task contract says so. | No |
| `AGENT_OPERATION` | operacja agenta | One atomic unit accepted by the metering ledger while an agent diagnoses, plans, invokes an integration, transforms data or validates a result. | Yes |
| `POLICY_DIRECTIVE` | dyrektywa polityki | An inert typed requirement, prohibition, record, report or possible effect proposal. In Policy IR v1 it is represented by the compatibility object named `action`. | No |
| `EFFECT` | skutek | An externally authorized state change performed after the POA boundary. | Product-specific |

A typical relationship is:

```text
EVENT -> TASK -> TASK_RUN -> 0..N AGENT_OPERATION -> optional EFFECT
                         ^
                         |
                 POLICY_DIRECTIVE
```

An event can be stored without starting a task. A task run can end without an
external effect. An agent operation can be diagnostic or validating and thus
produce no state change.

## Policy DSL compatibility

The Policy DSL v1 JSON field `actions` and the IR node kind `action` remain
unchanged. They are compatibility names for inert policy directives and MUST
NOT be interpreted as billable agent operations. Renaming those fields
inside major version 1 would break existing schema consumers without solving
the product vocabulary problem.

New product and API contracts SHOULD use:

```text
metering_unit = AGENT_OPERATION
agent_operations_included
agent_operations_used
agent_operations_remaining
```

Existing fields such as `actions_included` MAY be accepted as read aliases
during migration. New responses and analytics dimensions SHOULD emit the
canonical `agent_operations_*` names after a versioned API boundary is
available.

## Metering contract

Before charging for an `AGENT_OPERATION`, a product contract must define:

1. the start and terminal states of an operation;
2. whether failed operations and technical retries are counted;
3. the idempotency key preventing duplicate ledger entries;
4. whether one integration call, one tool invocation or one whole workflow step
   is the atomic unit;
5. how reversals and billing disputes are represented without deleting history.

Do not use `EVENT` as a billing synonym. Do not use `TASK_RUN` unless one billed
unit really equals one complete task attempt. Avoid "credits" when the unit is
one-to-one, because credits hide the underlying measurement.

## Product naming

Recommended display names:

- `Actions Plus` -> **Operations Plus**;
- "akcje agenta" -> **operacje agenta**;
- "pakiet akcji" -> **pakiet operacji**;
- a plan with zero included operations -> **0 operacji w pakiecie — dokupujesz przez Operations Plus**;
  keep the machine-readable entitlement `agent_operations_included: 0` and do
  not use the ambiguous label "Brak".

Compatibility plan identifiers such as `saas-business` and `prepaid-actions`
can remain unchanged until a separately versioned commerce migration is ready.
Presentation names and metering field names do not require an immediate SKU or
URL change.
