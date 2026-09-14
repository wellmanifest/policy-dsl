# Subactor sales policy profile

Status: reference application profile for Policy DSL v1 (`SUBACTOR_SALES`
document version 2). The canonical Polish profile documentation is in
`profiles/sales/README.md` and `profiles/sales/ADOPTION_PL.md`.

## Purpose

The profile replaces independently maintained promotion conditions with one
closed decision contract. **Plan names, list prices, currencies and operation
entitlements HOME in `subactor/offer`.** **Public naming vocabulary HOMEs in
`subactor/brand`.** This pack owns only promotion qualification, code
sanitization and card requirements. The evaluator reads HOME data from a
digest-locked copy of the current offer catalog; it never charges a card,
changes a subscription or grants a checkout effect.

```text
subactor/offer (current catalog, pinned by digest)   subactor/brand (vocabulary)
            \                                              /
             v                                            v
raw plan id + raw promo code
            |
            v
profiles/sales/subactor-sales.policy   ← promotion rules (VERSION 2)
profiles/sales/offer-catalog.json      ← sales-owned fields only (catalog/v2)
profiles/sales/offer-home.lock.json    ← HOME revision + digest, must be current
            |
            v
subactor.sales/decision/v2
      |          |          |
   backend    frontend   legacy PHP
   validates  renders    renders
      |
      v
protected checkout/payment boundary
```

The backend remains authoritative. Frontend and legacy consumers may render the
same decision, but client-side evaluation never grants promotion eligibility.

## Current model (HOME `subactor-cloud` v2)

| Display name (HOME) | Plan id | Public code | Legacy public code | Included agent operations (HOME) | `NOCC100` |
| --- | --- | --- | --- | ---: | --- |
| Basic | `saas-start` | `basic` | — | 1,000 / month | Eligible; card bypass |
| Pro | `saas-business` | `pro` | `operations-plus` | 5,000 / month | Sanitized and hidden |
| Max | `prepaid-actions` | `max` | `twin-plus` | 20,000 / month | Sanitized and hidden |
| On-premise | `on-premise` | `on-premise` | — | Contract | Sanitized and hidden |

The offer no longer communicates digital twins, so decisions carry no twin
fields. Legacy public codes are accepted as read-only inputs; decisions always
return the current public code. Prices are intentionally absent from this table:
read them from `subactor/offer`.

## Decision files

- `profiles/sales/subactor-sales.policy` — Policy DSL promotion rules;
- `profiles/sales/offer-catalog.json` — sales-owned plan fields (`subactor.sales/catalog/v2`);
- `profiles/sales/offer-home.lock.json` — pinned HOME catalog (`offer-home-lock/v2`);
- `schemas/sales-request.schema.json` — closed request contract (`request/v2`);
- `schemas/sales-offer-catalog.schema.json` — closed catalog contract (`catalog/v2`);
- `schemas/sales-decision.schema.json` — closed inert decision contract (`decision/v2`);
- `profiles/sales/reference_engine.py` — dependency-free evaluator;
- `profiles/sales/decision-matrix.json` — golden regression matrix;
- `examples/sales/decisions/matrix.v2.json` — frozen consumer `decision/v2` export;
- `examples/sales/fixtures/subactor-cloud-v2.offer.json` — byte copy of the pinned HOME catalog.

## Adapter rules

The backend applies a promotion only when
`promotion.eligibility = "ELIGIBLE"`, after rechecking current plan, policy,
price, account and payment context. Frontend and legacy PHP render
`promotion.normalized_code` and `promotion.presentation` from the same
contract. A non-eligible code is always returned as an empty string and
`HIDDEN`.

Display names, operation counts and copy come from `subactor/offer` and
`subactor/brand`, never from this pack. `decision.offer.display_name` and
`decision.metering` are read-only echoes of the locked HOME catalog, identified
by `decision.home.offer_ref` and `decision.home.digest`.

## Validation

```bash
python3 tests/policy_dsl_check.py validate profiles/sales/subactor-sales.policy
python3 profiles/sales/reference_engine.py validate-catalog
python3 profiles/sales/reference_engine.py compare-offer-home \
  --home-root /path/to/subactor/offer
python3 profiles/sales/reference_engine.py matrix \
  --check profiles/sales/decision-matrix.json
python3 profiles/sales/reference_engine.py export-decisions \
  --check examples/sales/decisions/matrix.v2.json
python3 profiles/sales/reference_engine.py decide --plan-id saas-start --promo-code NOCC100
python3 -m unittest discover -s tests -p 'test_*.py'
```

`compare-offer-home` fails when the pinned catalog is not `current`; with
`--home-root` it also fails when the pin is not the offer's only current
version. The decision is descriptive data, not payment authorization or
approval evidence.

## Changing the offer

1. Change prices, names or entitlements in `subactor/offer` and publish a new
   catalog version there.
2. Copy the new catalog bytes to `examples/sales/fixtures/`, update
   `profiles/sales/offer-home.lock.json` (path, version, revision, digest) and
   regenerate the decision matrix and consumer export.
3. Refresh the portal facade fixture from `www-sub-actor`.

A pin to an archived or superseded catalog fails closed; it must not be
"fixed" by editing amounts or names in this repository.
