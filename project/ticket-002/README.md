# Ticket 002: Subactor host hardware Policy DSL (server + RPi)

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Utworzyć **osobne** dokumenty `wellmanifest.policy/v1` ze specyfikacją hosta
produkcyjnego (VPS) oraz Raspberry Pi 5, na bazie
`www-sub-actor/docs/deployment.md` i obserwacji Platformy. Polityka jest
inertna: nie wdraża stacku, tylko kwalifikuje host.

## Acceptance criteria

- [x] AC-01: `examples/hosting/subactor-production-server.policy` waliduje się
      przez `policy_dsl_check.py` i deklaruje `subactor.host/production-server/v1`.
- [x] AC-02: `examples/hosting/subactor-rpi5.policy` waliduje się osobno jako
      `subactor.host/rpi5/v1` i zabrania pełnej Platformy produkcyjnej.
- [x] AC-03: Dokumenty ludzkie `docs/HOST_PRODUCTION_SERVER.md` oraz
      `docs/HOST_RPI5.md` opisują parametry MUST/SHOULD i relację do Plesk edge.
- [x] AC-04: Testy jednostkowe + wpisy w `dsl-manifest.json` conformance.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)
