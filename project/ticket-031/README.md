# Ticket 031: Require DEFAULT literals and publish matching parser artifact digests

- **ID**: ticket-031
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-24

## Goal and scope

Fix producer parser behavior reported in wellmanifest/new-project#534 finding1. This integration ticket owns the parser, its tests, and the matching two artifact digests in dsl-manifest.json.

SESSION_EXECUTION_AUTHORIZATION: user requests autonomous backlog fixes, tests and protected publication across ~/github/*/*. Independent exact-head review remains required.

Explicit predecessor handoff: uncommitted ticket-030 has no remaining implementation delta and its source-controller lease is released. Material patch and original metadata are preserved externally in policy-default-20261024/application-handoff-snapshot.json.

## Acceptance criteria

- [ ] AC-01: Bare and whitespace-only DEFAULT fail with POLICY-SYNTAX-001; explicit literal and REQUIRED IR semantics are preserved.
- [ ] AC-02: Published artifact digests match source and all conformance/governance checks pass before protected publication.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.

<!-- ticket-radar:start -->
## Ticket Radar

Assessment unavailable: managed ticket storage bridge declined the radar assessment.
Advisory only; no execution or merge approval.
<!-- ticket-radar:end -->
