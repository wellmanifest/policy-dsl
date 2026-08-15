---
{
  "schema": "subactor.host-spec-markdown/v1",
  "id": "host.rpi5",
  "version": 1,
  "status": "current",
  "updated": "2026-08-15",
  "policy": "subactor.host/rpi5/v1",
  "policy_path": "examples/hosting/subactor-rpi5.policy"
}
---

# Specyfikacja: Raspberry Pi 5 (Subactor)

Normatywne reguły są w Policy DSL
[`examples/hosting/subactor-rpi5.policy`](../examples/hosting/subactor-rpi5.policy)
(`wellmanifest.policy/v1`). Ten dokument jest czytelny dla człowieka.

## Werdykt architektoniczny

RPi 5 jest **edge / lab**, nie hostem pełnej Platformy produkcyjnej.

| Rola | Dozwolone | Zabronione |
| --- | --- | --- |
| `LAB_SMOKE` | smoke portalu ARM64, test obrazu | publiczny SaaS origin, pełny ekosystem |
| `PORTAL_EDGE` | portal `www-sub-actor`, statyczny edge | produkcyjny Compose Platformy, Planfile heavy, lokalne LLM |
| Platforma produkcyjna | — | zawsze `FORBID` na tym profilu |

Pełny runtime → osobny dokument
[`HOST_PRODUCTION_SERVER.md`](HOST_PRODUCTION_SERVER.md).

## Parametry

| Parametr | Minimum | Produkcyjny edge portalu |
| --- | --- | --- |
| Model | Raspberry Pi 5 | to samo |
| Arch | **arm64** (MUST) | arm64 |
| RAM | **8 GiB** | 8 GiB |
| OS | Raspberry Pi OS 64-bit **lub** Ubuntu ARM64 | to samo |
| Dysk danych | 64 GiB (lab) | **≥ 128 GiB NVMe/SSD** |
| microSD | tylko lab / boot test | **zakaz** jako primary data portalu |
| Silnik | Docker lub Podman | Docker preferowany |

## Reguły kluczowe (skrót)

- `RPI-FORBID-FULL-PLATFORM` — zawsze bez full ecosystem / production Platform.
- `RPI-REJECT-MICROSD-DATA` — microSD + `PORTAL_EDGE` → `REJECT`.
- `RPI-PORTAL-EDGE` — wymaga NVMe/SSD, backup, pin lock oraz
  `SEPARATE_PRODUCTION_SERVER_FOR_PLATFORM`.
- `RPI-LAB-SMOKE` — dopuszcza microSD wyłącznie w labie; bez publicznego SaaS.

## Typowy układ

```text
Internet → (opcjonalnie Plesk TLS)
         → RPi 5: portal / statyczny edge
         → VPS: Platforma (Control, Planfile, …)
```

## Źródło

`www-sub-actor/docs/deployment.md` §1 (RPi 5, 8 GB RAM, SSD, nie microSD do
produkcyjnej bazy).
