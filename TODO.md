# Project roadmap

- [x] [`ticket-001`](project/ticket-001/README.md) — establish the governed
  repository and define Policy DSL v1, its closed Policy IR, constrained LLM
  grammar, reference parser and cross-implementation conformance suite.
- [x] Define the `AGENT_OPERATION` digital-twin vocabulary and an inert Subactor
  sales decision profile for NOCC100, plan aliases and Twin Plus metering copy.
- [x] Adopt published `wellmanifest/new-project` **v0.18.1** immutable
  governance locks ([`ticket-004`](project/ticket-004/README.md)).
- [ ] Align `wellmanifest/dsl` `standardsLock` / artifact digests and pin
  `wellmanifest/wellm` once a final published release declares a Policy DSL
  contract dependency.
- [ ] Replace duplicated Subactor backend, frontend and legacy PHP promotion
  guards with one `subactor.sales/decision/v1` adapter contract.
- [ ] Remove writes of legacy `actions_included` and legacy public name
  `Actions Plus` after the announced compatibility period.
