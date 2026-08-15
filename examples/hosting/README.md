# Profil hostów Subactor (Policy DSL)

Inertne dokumenty `wellmanifest.policy/v1` opisujące **czy host nadaje się**
do danej roli. Parsowanie i ewaluacja nie uruchamiają deploya — efekt wymaga
osobnego POA / grantu Foundera.

## Dokumenty

| Plik | Polityka | Rola |
| --- | --- | --- |
| [`subactor-production-server.policy`](subactor-production-server.policy) | `subactor.host/production-server/v1` | VPS / bare metal — pełna Platforma |
| [`subactor-rpi5.policy`](subactor-rpi5.policy) | `subactor.host/rpi5/v1` | Raspberry Pi 5 — portal / lab edge |

Opisy ludzkie:

- [`../../docs/HOST_PRODUCTION_SERVER.md`](../../docs/HOST_PRODUCTION_SERVER.md)
- [`../../docs/HOST_RPI5.md`](../../docs/HOST_RPI5.md)

Źródła wymagań: `www-sub-actor/docs/deployment.md`, live footprint Platformy,
`knowledge://subactor/incidents.plf-592.public-founder-ingress/v3`.

## Kontekst wejściowy (symbole)

Profil oczekuje jawnego kontekstu ewaluacji (nie czyta `/proc` sam):

| Symbol | Typ | Znaczenie |
| --- | --- | --- |
| `HOST_KIND` | string | `PRODUCTION_SERVER` albo `RPI5` |
| `ROLE` | string | np. `PLATFORM_RUNTIME`, `PORTAL_EDGE`, `LAB_SMOKE` |
| `RAM_GIB` | integer | RAM hosta w GiB |
| `VCPU` | integer | widoczne vCPU |
| `DISK_GIB` | integer | pojemność wolumenu danych |
| `CPU_ARCH` | string | `amd64` / `arm64` |
| `STORAGE_KIND` | string | `nvme` / `ssd` / `microsd` |
| `CONTAINER_ENGINE` | string | `docker` / `podman` |
| `HOST_OS` | string | tylko RPi: `raspberry_pi_os_64` / `ubuntu_arm64` |
| `PUBLIC_HTTP` / `PUBLIC_HTTPS` | boolean | otwarte 80/443 |
| `ROOTLESS` | boolean | Podman rootless |
| `PLESK_EDGE` | boolean | Plesk tylko jako DNS/TLS/mail/proxy |

## Wynik (dyrektywy)

Typowe `RECORD HOST_FIT`:

- `RECOMMENDED` / `MINIMUM` / `PORTAL_EDGE` / `LAB` — dopuszczalne w zakresie
- `DEGRADED` — wymaga LB / high ports / monitoringu
- `REJECT` — zakaz deployu danej roli

`ALLOW` / `FORBID` to **dyrektywy polityki**, nie token autoryzacji runtime.

## Walidacja

```bash
python3 tests/policy_dsl_check.py validate examples/hosting/subactor-production-server.policy
python3 tests/policy_dsl_check.py validate examples/hosting/subactor-rpi5.policy
python3 -m unittest tests.test_host_hardware_policy
```
