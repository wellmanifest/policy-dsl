# Subactor sales examples

CI fixtures and the consumer export for the sales profile in `profiles/sales/`.

- `fixtures/subactor-cloud-v2.offer.json` is a byte-identical copy of the pinned
  `subactor/offer` HOME catalog (`catalogs/subactor-cloud/v2/offer.json` at the
  revision recorded in `profiles/sales/offer-home.lock.json`). The sales profile
  reads names, operation entitlements, amounts and currencies from this copy and
  holds no second version of them.
- `fixtures/www-plans.facade.json` is a thin projection of the portal
  `plans.json` fields checked by `compare-www-plans` (operations, name, amounts,
  currency), pinned by `profiles/sales/www-plans.lock.json` to
  `offer://subactor/offer/subactor-cloud/v2`.
- `decisions/matrix.v2.json` is the frozen consumer export of
  `subactor.sales/decision/v2`. It is not payment authorization.

Validate with:

```bash
python3 profiles/sales/reference_engine.py compare-offer-home
python3 profiles/sales/reference_engine.py compare-offer-home --home-root /path/to/subactor/offer
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans examples/sales/fixtures/www-plans.facade.json
python3 profiles/sales/reference_engine.py export-decisions \
  --check examples/sales/decisions/matrix.v2.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

When the product offer changes, update the HOME catalog in `subactor/offer`
first, then the fixture, lock digest, decision matrix and consumer export
together. Refresh the facade fixture when the portal changes.
