# Adopcja: host hardware Policy DSL (Subactor)

## HOME / ADOPT

- **HOME**: `wellmanifest` (`policy-dsl`, `shape=domain_pack`)
- **ADOPT** w Subactor: `wellmanifest/policy-dsl`
- Runtime deploy pozostaje w `subactor` / `www-sub-actor` (nie HOME wellmanifest)

## Dokumenty

| Rola | Policy | Spec ludzka |
| --- | --- | --- |
| VPS / bare metal Platforma | `examples/hosting/subactor-production-server.policy` | `docs/HOST_PRODUCTION_SERVER.md` |
| Raspberry Pi 5 edge/lab | `examples/hosting/subactor-rpi5.policy` | `docs/HOST_RPI5.md` |

## Jak używać w Subactor

1. Traktuj Policy DSL jako **kwalifikację hosta** przed `deploy-all.sh` /
   `deploy-stack.sh` — nie jako grant apply.
2. W `www-sub-actor/docs/deployment.md` trzymaj procedurę operacyjną; parametry
   MUST/SHOULD synchronicznie z tymi profilami (16/32 GiB serwer, RPi = edge).
3. Plesk = DNS/TLS/mail/proxy; Compose Platformy = osobny Docker host
   (`FORBID RUN_COMPOSE_STACK_INSIDE_PLESK`).

## Walidacja

```bash
python3 tests/policy_dsl_check.py validate examples/hosting/subactor-production-server.policy
python3 tests/policy_dsl_check.py validate examples/hosting/subactor-rpi5.policy
```
