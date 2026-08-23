# Ticket 016: Adopt new-project standard 0.18.6

- **ID**: ticket-016
- **Owner**: agent:gemini under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-23

## Goal and scope

Adopt published `wellmanifest/new-project` 0.18.6 into `wellmanifest/policy-dsl` in one atomic transaction through `create_adoption_lock.py`.
Brings the host-agnostic contract (CLAUDE.md, GEMINI.md, Cursor rule, pre-commit hook, agent-hosts.json validator) and `governance / enforce` CI job.

## Acceptance criteria

- [x] AC-01: `python3 .governance/agent_host_check.py --root .` → `GOV-AGENT-HOST-PASS` after `./scripts/install-agent-hosts.sh`.
- [x] AC-02: `./project/governance-check.sh --actor agent` → `GOV-PASS`, all managed digests match lock.
- [x] AC-03: `new-project-governance.yml` CI passes green.

## Publication evidence

- Pull request: `wellmanifest/policy-dsl#20`
- Frozen and approved head: `477bd63835d4add52246ae690a870f77dd092bd4`
- Merge commit: `abbb05ae9ccd4cafd4429d7e5778674dfa58267d`
- Validator approval: review `5002758412`, run `32663343774`.

## Participants

- Human participant: authorized via active session.
- Agent participant: [ai-gemini.md](ai-gemini.md)
