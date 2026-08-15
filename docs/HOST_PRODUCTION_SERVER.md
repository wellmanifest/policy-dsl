---
{
  "schema": "subactor.host-spec-markdown/v1",
  "id": "host.production-server",
  "version": 1,
  "status": "current",
  "updated": "2026-08-15",
  "policy": "subactor.host/production-server/v1",
  "policy_path": "examples/hosting/subactor-production-server.policy"
}
---

# Specyfikacja: serwer produkcyjny Subactor

Normatywne reguły są w Policy DSL
[`examples/hosting/subactor-production-server.policy`](../examples/hosting/subactor-production-server.policy)
(`wellmanifest.policy/v1`). Ten dokument jest czytelny dla człowieka i operatora
zakupów VPS.

## Werdykt architektoniczny

| Warstwa | Gdzie |
| --- | --- |
| Pełna Platforma (Control, Planfile, Bridge, Vault, observability) | **Ten VPS / bare metal** z Docker Compose |
| WWW / DNS / TLS / poczta / reverse proxy | Plesk **edge** (opcjonalnie) |
| Shared Plesk + Docker Extension jako runtime Platformy | **Zakazane** przez politykę |

## Parametry (MUST / SHOULD)

| Parametr | Minimum (MUST) | Rekomendowane (SHOULD) |
| --- | --- | --- |
| vCPU | 4 | **8** |
| RAM | **16 GiB** | **32 GiB** |
| Dysk danych | 100 GiB SSD/NVMe | **200–500 GiB NVMe** |
| Arch | `amd64` lub `arm64` | `amd64` |
| Silnik | Docker Engine + Compose v2 (preferowane) albo Podman po smoke | Docker |
| Sieć | publiczne 80/443 **albo** LB na high ports | 80/443 na hoście |
| OS | Ubuntu 22.04/24.04 LTS (typowa ścieżka) | to samo |

Poniżej minimum → `HOST_FIT=REJECT`, `FORBID DEPLOY_PLATFORM`.

Minimum bez recommended → `HOST_FIT=MINIMUM`: wolno Platformę i portal, **bez**
ciężkiego digital-twin / lokalnych wag LLM.

Recommended → `HOST_FIT=RECOMMENDED`: `ALLOW DEPLOY_FULL_ECOSYSTEM`.

## Obowiązki operacyjne

Polityka wymaga (dyrektywy `REQUIRE`):

- backup wolumenów (`*-data`, Postgres portalu, `acme-data`);
- monitoring miejsca na dysku;
- pinned `components.lock` / SHA (nie `main` wielu repo naraz);
- audyt `.env` (nie kopiować posture z PC deweloperskiego).

Zakazy:

- `FORBID HOST_ON_SHARED_PLESK_DOCKER`
- `FORBID BIND_CONTROL_PORT_8181_PUBLIC` (Control tylko przez jawny router, np.
  `control.sub.actor`)
- przy Podman rootless: nie wiązać 80/443 bez LB / high ports

## Plesk jako edge

Gdy `PLESK_EDGE=TRUE`:

- `ALLOW` DNS, TLS, mail, WWW, reverse proxy;
- `FORBID RUN_COMPOSE_STACK_INSIDE_PLESK`;
- `REQUIRE SEPARATE_DOCKER_HOST`.

## Mapowanie na deploy

Zgodnie z `www-sub-actor/docs/deployment.md`:

```env
SUBACTOR_DEPLOYMENT_TOPOLOGY=production
CONTROL_DEPLOYMENT_POSTURE=execute_bounded
FOUNDER_PORTAL_URL=https://control.sub.actor/founder
FOUNDER_PUBLIC_PORTAL_URL=https://control.sub.actor/founder
FOUNDER_PUBLIC_LINKS_REQUIRED=1
```

## Dowód live (orientacyjny footprint)

Na hoście z ~20 kontenerami Platformy obserwowano m.in. Planfile ≈ 2 GiB,
ClickHouse ≈ 0.7 GiB, Bridge/ops ≈ 0.3 GiB — stąd floor 16 GiB i cel 32 GiB.
