# Subactor sales policy profile

Status: reference application profile for Policy DSL v1. The canonical Polish
profile documentation is in `profiles/sales/README.md` and
`profiles/sales/ADOPTION_PL.md`.

## Purpose

The profile replaces three independently maintained promotion conditions with
one closed decision contract. The catalog owns offer identities, entitlements
and metering copy; Policy DSL owns qualification, sanitation and presentation
guards. The evaluator combines them without charging a card, changing a
subscription or granting a checkout effect.

```text
raw plan id + raw promo code
            |
            v
profiles/sales/subactor-sales.policy
profiles/sales/offer-catalog.json
            |
            v
subactor.sales/decision/v1
      |          |          |
   backend    frontend   legacy PHP
   validates  renders    renders
      |
      v
protected checkout/payment boundary
```

The backend remains authoritative. Frontend and legacy consumers may render the
same decision, but client-side evaluation never grants promotion eligibility.

## Current compatibility model

| Public display | Compatibility plan id | Public code | Active twins | Included agent operations | `NOCC100` |
| --- | --- | --- | ---: | ---: | --- |
| Basic | `saas-start` | `basic` | 1 | 1,000 | Eligible; card bypass |
| Operations Plus | `saas-business` | `operations-plus` | 0 | 10,000 | Sanitized and hidden |
| Twin Plus | `prepaid-actions` | `twin-plus` | 1 | 0 | Sanitized and hidden |
| On-premise | `on-premise` | `on-premise` | Contract | Contract | Sanitized and hidden |

Legacy identifiers remain accepted. Canonical writes use
`agent_operations_included`, `Operations Plus` and the public plan codes. The
read aliases `actions_included` and `Actions Plus` exist only for migration.

## Decision files

- `profiles/sales/subactor-sales.policy` — Policy DSL rules;
- `profiles/sales/offer-catalog.json` — closed catalog and compatibility map;
- `schemas/sales-request.schema.json` — closed request contract;
- `schemas/sales-offer-catalog.schema.json` — closed catalog contract;
- `schemas/sales-decision.schema.json` — closed inert decision contract;
- `profiles/sales/reference_engine.py` — dependency-free evaluator;
- `profiles/sales/decision-matrix.json` — golden regression matrix;
- `examples/sales/subactor-pricing-section.html` — corrected UI projection.

## Adapter rules

The backend applies a promotion only when
`promotion.eligibility = "ELIGIBLE"`, after rechecking current plan, policy,
price, account and payment context. Frontend and legacy PHP render
`promotion.normalized_code` and `promotion.presentation` from the same
contract. A non-eligible code is always returned as an empty string and
`HIDDEN`.

For Twin Plus, `metering.included = 0` means that the add-on contributes an
active twin but no operation quota. The UI label is "0 operacji w pakiecie — dokupujesz przez Operations Plus",
not "Brak".

## Validation

```bash
python3 tests/policy_dsl_check.py validate profiles/sales/subactor-sales.policy
python3 profiles/sales/reference_engine.py validate-catalog
python3 profiles/sales/reference_engine.py matrix \
  --check profiles/sales/decision-matrix.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

The decision is descriptive data, not payment authorization or approval
evidence.
