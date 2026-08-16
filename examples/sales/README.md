# Subactor pricing copy example

This directory contains the pricing-section projection aligned with the
canonical sales profile in `profiles/sales/`.

The updated HTML:

- uses `AGENT_OPERATION` / "operacja agenta" terminology;
- displays the plan name `Operations Plus` while retaining the compatibility
  `data-plan="saas-business"` identifier;
- keeps `NOCC100` only on the Basic (`saas-start`) card;
- removes the promotion hint from Operations Plus;
- replaces the Twin Plus label "Brak" with "0 operacji w pakiecie";
- retains `data-plan="prepaid-actions"` until a separate SKU migration.

Validate the profile and pricing projection with:

```bash
python3 profiles/sales/reference_engine.py compare-offer-home
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans examples/sales/fixtures/www-plans.facade.json
python3 profiles/sales/reference_engine.py matrix \
  --check profiles/sales/decision-matrix.json
python3 profiles/sales/reference_engine.py export-decisions \
  --check examples/sales/decisions/matrix.v1.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

The `fixtures/subactor-cloud-v1.offer.json` file is a byte-identical CI copy of
the pinned `subactor/offer` HOME catalog. Update the lock digest, fixture and
sales projection together when the product offer changes.

The `fixtures/www-plans.facade.json` file is a thin CI projection of portal
`plans.json` fields that `compare-www-plans` checks (entitlements, name aliases,
mirrored amounts). It is pinned by `profiles/sales/www-plans.lock.json` and
aligned to the same `offer://subactor/offer/subactor-cloud/v1` pin. Refresh the
fixture when the sales catalog or www facade commercial fields change; do not
treat this pack as a second price HOME.

The `decisions/matrix.v1.json` file is the frozen consumer export of
`subactor.sales/decision/v1` (`export-decisions --check`). It is not payment
authorization. Refresh it with `export-decisions --out` when `decide()` changes.
