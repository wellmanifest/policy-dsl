# Ticket 018: Adopt subactor-cloud v2 in the sales profile and fail closed on non-current HOME pins

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Session execution authorization**: user requested implementation of wellmanifest/policy-dsl#23 and recorded the product decisions below (2026-09-14)
- **Created**: 2026-09-14
- **Issue**: wellmanifest/policy-dsl#23

## Goal and scope

`profiles/sales/offer-home.lock.json` pinned `subactor/offer`
`catalogs/subactor-cloud/v1/offer.json`, archived in HOME since `a01860e`.
The current catalog is v2 (`6f38fbe`). `compare-offer-home` compared only
against the pinned bytes, and the profile carried a stale second copy of prices,
names, entitlements, twin data and Polish copy.

## Product decisions (user, 2026-09-14)

1. Pro and Max have `active_twins_included: 0` by design; the offer no longer
   informs users about digital twins.
2. Public codes become `pro` and `max`.
3. `NOCC100` remains eligible for Basic only.
4. The sales profile stops holding Polish labels.
5. The Twin Plus presentation rule is removed.

Derived (not a separate decision): with twin information removed, the decision
reports HOME `unit` (`actions_monthly`) as the metering period instead of the
v1 `PER_TWIN_MONTH`/`ACCOUNT_MONTH` scope.

## Acceptance criteria

- [x] AC-01: full unit suite passes, including live portal facade and live HOME checks (51 tests).
- [x] AC-02: `compare-offer-home --home-root` passes for the v2 pin and rejects a superseded pin.
- [x] AC-03: decision matrix and consumer export are regenerated as v2.
- [x] AC-04: `./project/governance-check.sh` passes on the published head.

## Publication evidence

- Pull request: `wellmanifest/policy-dsl#25`; required checks `governance / enforce`
  and `governance / remote lifecycle` pass (the latter after removing the contained
  orphan branch `ticket/017-close`).
- Validator dry run `subactor/validator-agent` run `34817387553` on head `08e65d2`:
  `DRY RUN: would explicitly merge`.
- The following real dispatch was refused with `BLOCKED_DIRECT_PR_DUPLICATE_EPOCH`
  because the dry run consumed the dispatch epoch for that head; this record moves
  the head so the protected validator can run once without dry run.

- Approved and merged head: `9263c5437404ee90070ccf3cca7bafa83133df47`
  (review `5194996501` by `ifuri-validator-agent[bot]`, validator run `34817881627`).
- Merge commit: `5551a57b6ef1ff7ce9a33798262e8e9af6aae4c1`.

## Known limitation

`dsl-manifest.json` still fails the current `wellmanifest/dsl` gate on
`llm.decisionProtocol` (pre-existing, `llm.mode=output` needs a bidirectional
boundary); this ticket does not change the LLM section.

## Dependent follow-ups

- JSON Schemas `schemas/sales-*.schema.json` for catalog/decision/request v2.
- Documentation: `README.md`, `profiles/sales/README.md`, `profiles/sales/ADOPTION_PL.md`,
  `docs/SALES_POLICY_PROFILE.md`, `docs/DOMAIN_VOCABULARY*.md`, `examples/sales/README.md`.
- Consumer: `subactor/www-sub-actor` `config/commercial-ssot.lock.json` still names
  `subactor.sales/catalog/v1`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-claude.md](ai-claude.md)
