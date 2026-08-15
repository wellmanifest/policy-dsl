# Changelog — ticket-003

- Hardened `validate_ir` for duplicate bindings, environment names, transition
  edges, and undeclared `NEXT`/`TRANSITION` states.
- Fixed `examples/valid/CONTRIBUTING.md` to declare matching `STATE` symbols.
- Added invalid fixtures and unit tests; refreshed `dsl-manifest.json` digests.
- Recorded remediation intent + todo2code projections and `DISCOVERY.md`
  follow-ups (agent/report publish, governance lock refresh, opcode profile,
  ENV_FILE uniqueness, checker complexity split).
