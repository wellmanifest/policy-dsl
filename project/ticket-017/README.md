# Ticket 017: Fail closed on unselected dsl fences in Markdown carriers

- **ID**: ticket-017
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Session execution authorization**: user requested correcting wellmanifest standards that contain errors or do not express logic in DSL (2026-09-13)
- **Created**: 2026-09-13

## Goal and scope

Section 3.2 selected only `dsl` fences that start with a known statement and
silently ignored every other `dsl` fence after the header. Normative-looking
text therefore disappeared without a diagnostic. Observed on
`wellmanifest/new-project@8d86cd6`: the `FUNKCJA DONE` fence in
`CONTRIBUTING.md` (`DONE WHEN ... REPORT MUST_INCLUDE [...]`) is not Policy DSL
and is dropped, so the completion contract is not part of the parsed policy.

The selector also treated any concrete `DOCUMENT` header as the Policy DSL
header. Domain documents such as `twin-lifecycle/docs/ARCHITECTURE.md` and
`merge/docs/ARCHITECTURE.md` declare `SCHEMA "wellmanifest.<domain>/v1"` and
were misclassified, producing `unknown top-level statement` at line 5.

This ticket makes the selector classify every `dsl` fence:

1. `DOCUMENT <...>` placeholder metadata: illustration, ignored;
2. concrete `DOCUMENT` with a foreign `SCHEMA`, or a second concrete header:
   independent document, ignored;
3. registered record kind (`DECISION`, used by new-project decision records):
   ignored;
4. policy statement or binding: selected after the header, rejected before it;
5. anything else: `POLICY-SYNTAX-001`.

## Acceptance criteria

- [x] AC-01: self-test and both valid Markdown carriers pass.
- [x] AC-02: `examples/invalid/unclassified-dsl-fence.md` is rejected with
  `POLICY-SYNTAX-001` at line 19.
- [x] AC-03: unit suite: 45 tests, one pre-existing host-dependent error
  (`test_compare_www_plans_accepts_live_www_when_present`, also failing on the
  accepted base `48e95c8` because it reads the live `www` checkout).
- [x] AC-04: manifest digest test passes with the new artifacts bound.
- [x] AC-05: `./project/governance-check.sh` passes on the published head.

## Publication evidence

- Pull request: `wellmanifest/policy-dsl#22`
- Approved and merged head: `90558cbdd9442596359e52f7c580cd978de551b4`
  (intent commit `285cf36` precedes implementation commit `90558cb`)
- Merge commit: `d723271`
- Validator approval: review `5191533907` by `ifuri-validator-agent[bot]`,
  `governance / enforce` run `34771522839`.

The host-dependent error listed in AC-03 is not an independent pre-existing
failure: the sales profile pins the archived `subactor-cloud` v1 offer while
the HOME and the live portal use v2. It is tracked in `wellmanifest/policy-dsl#23`.

## Compatibility and follow-ups

- `wellmanifest/new-project` vendors checker revision `daaf7b7` and is not
  affected until it updates `governance/policy-dsl.lock.json`. Its
  `CONTRIBUTING.md` must first replace the `DONE WHEN` fence with Policy DSL
  rules; that repository currently has an active governance writer.
- Pre-existing, out of scope: `dsl-manifest.json` still fails the current
  `wellmanifest/dsl` gate because `llm.mode=output` requires a bidirectional
  `dsl-input-output` decision boundary with a request schema.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-claude.md](ai-claude.md)
