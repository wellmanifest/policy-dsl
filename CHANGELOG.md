# Changelog

## Unreleased

### 0.2.0-dev

- Standardize digital-twin product metering on `AGENT_OPERATION` / "operacja
  agenta" while retaining Policy IR v1 `action` as an inert policy-directive
  compatibility name.
- Add the Subactor sales policy profile for `NOCC100`, Basic, Operations Plus,
  Twin Plus and the existing compatibility plan identifiers.
- Add a dependency-free descriptive sales decision evaluator and exact
  regression cases for Basic, `saas-business`, `prepaid-actions` and
  `on-premise`.
- Correct the pricing example: remove `NOCC100` from Operations Plus, rename
  Actions Plus to Operations Plus and replace the ambiguous Twin Plus "Brak"
  label with "0 operacji w pakiecie".
- Clarify that application profiles and client projections never grant checkout
  or effect authority.

### 0.1.0-dev

- Bootstrap the governed `wellmanifest/policy-dsl` standard repository.
