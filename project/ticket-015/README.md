# Ticket 015: Repair DSL manifest bindings for llm-credential profile

- **ID**: ticket-015
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-16

## Goal and scope

Repair the metadata drift introduced by the two local llm-credential profile
commits. The profile semantics stay unchanged: only current SHA-256 bindings
and artifact roles accepted by `wellmanifest.dsl/manifest/v1` are in scope.

## Acceptance criteria

- [x] AC-01: `dsl_check validate dsl-manifest.json` passes.
- [x] AC-02: the policy-dsl unit suite passes, including manifest digest tests.
- [x] AC-03: no unrelated parser or runtime behavior changes.
- [x] AC-04: the intent commit precedes both profile implementation commits.

## Authorization

The human continuation instruction on 2026-08-16 explicitly requested
continuing repairs. This ticket narrows that authorization to the broken
manifest metadata already identified in the validation sweep.

## Publication blocker

Two local profile experiments (`638e7f7`, `1a00393`) are available for
reapplication after this plan-only commit. Publication must preserve this
intent-first ordering.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-cursor.md](ai-cursor.md)
