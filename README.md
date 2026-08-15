# wellmanifest/policy-dsl

Governed standard and reference conformance implementation for the declarative
Policy DSL used by `wellmanifest/new-project` contributor policy documents and
inert application-policy profiles.

The language describes rules, conditions, obligations, prohibitions,
assertions and state transitions. It is inert policy data: parsing, deciding or
reducing a profile never executes a shell command, performs checkout or grants
effect authority.

## Digital-twin terminology

Policy IR v1 keeps the compatibility node name `action` for an inert policy
directive, which may describe a possible effect proposal. Product metering
should use **agent operation** (`AGENT_OPERATION`, Polish: **operacja agenta**)
and keep events, tasks and task runs distinct.
See [`docs/DOMAIN_VOCABULARY.md`](docs/DOMAIN_VOCABULARY.md).

## Subactor sales profile

The reference sales profile centralizes `NOCC100` eligibility and the current
Basic, Operations Plus and Twin Plus entitlement model without changing legacy
plan identifiers:

```bash
python3 profiles/sales/reference_engine.py decide --plan-id saas-start --promo-code NOCC100
python3 -m unittest discover -s tests -p 'test_*.py'
```

See [`docs/SALES_POLICY_PROFILE.md`](docs/SALES_POLICY_PROFILE.md) and
[`profiles/sales/subactor-sales.policy`](profiles/sales/subactor-sales.policy).

The original repository bootstrap and Policy DSL v1 implementation are tracked
by `project/ticket-001`.
