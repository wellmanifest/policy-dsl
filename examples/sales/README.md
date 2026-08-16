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
python3 profiles/sales/reference_engine.py matrix \
  --check profiles/sales/decision-matrix.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

The `fixtures/subactor-cloud-v1.offer.json` file is a byte-identical CI copy of
the pinned `subactor/offer` HOME catalog. Update the lock digest, fixture and
sales projection together when the product offer changes.
