# Agent log — composer / ticket-002

## SESSION_EXECUTION_AUTHORIZATION

User request (2026-08-15): zbadać i stworzyć w języku Policy DSL specyfikacje
serwera i RPi w osobnych dokumentach na bazie repozytorium `policy-dsl`,
z wejściem z `www-sub-actor/docs/deployment.md`.

## Placement

- `home`: wellmanifest
- `shape`: domain_pack
- `adopt`: wellmanifest/policy-dsl

## Done

- Branch `ticket/003-host-hardware-policy` (ticket folder `ticket-002`).
- Policies under `examples/hosting/` + docs `docs/HOST_*.md` + tests + manifest.
- `python3 -m unittest discover -s tests -p 'test_*.py'` → OK.
