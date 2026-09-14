# Adopcja profilu sprzedażowego

## Cel zmiany

Warunek NOCC100 był powtórzony w backendzie, frontendzie i legacy PHP.
Wszystkie trzy warstwy konsumują jedną decyzję `subactor.sales/decision/v2`.
Tylko backend płatności może zastosować efekt.

## Kontrakt wejściowy

```json
{
  "schema": "subactor.sales/request/v2",
  "plan_id": "saas-start",
  "promo_code": "NOCC100"
}
```

`plan_id` może być identyfikatorem planu (`saas-start`, `saas-business`,
`prepaid-actions`, `on-premise`), kodem publicznym (`basic`, `pro`, `max`) albo
zastanym kodem publicznym tylko do odczytu (`operations-plus`, `twin-plus`).
Odpowiedź zawsze zawiera identyfikator planu i aktualny kod publiczny.

## Backend

Zastąp lokalny warunek kwalifikacji odczytem decyzji:

```text
decision = salesPolicy.decide(planId, rawPromoCode)

IF decision.promotion.eligibility != "ELIGIBLE"
  RETURN plan without promotion effect

RETURN paymentBackend.applyAuthorizedPromotion(
  plan,
  decision.promotion.normalized_code
)
```

Backend MUST ponownie sprawdzić wersję polityki, `home.digest` i plan przed
efektem płatniczym. Decyzja nie jest tokenem autoryzacji.

## Frontend

Frontend nie sanitizuje kodu zależnie od planu. Przesyła surową wartość
i renderuje wyłącznie odpowiedź:

```text
promoInput.value = decision.promotion.normalized_code
promoBadge.visible = decision.promotion.presentation == "VISIBLE"
promoMessage = localize(decision.promotion.reason)
```

Dla Pro, Max i on-premise kod NOCC100 wraca jako pusty i `HIDDEN`. Na kartach
tych ofert nie może być statycznego komunikatu o NOCC100.

## Legacy PHP

Preferowana integracja to ten sam endpoint lub ta sama biblioteka decyzyjna.
Jeżeli legacy nie może jej wywołać, pipeline wydania MAY wygenerować zamknięty
adapter na podstawie tej samej polityki, katalogu i zablokowanego katalogu HOME.
Konsumenci porównują z zamrożonym eksportem
`examples/sales/decisions/matrix.v2.json` albo wołają
`reference_engine.py decide` / `export-decisions --check`.

## Teksty interfejsu i bliźniaki

Profil nie przechowuje tekstów interfejsu. Nazwy planów, liczby operacji i ceny
pochodzą z `subactor/offer`, a słownictwo z `subactor/brand`. Oferta nie
komunikuje bliźniaków, dlatego decyzja nie zawiera pól o bliźniakach, a UI nie
powinien ich wyświetlać.

## Migracja z v1

| v1 | v2 |
| --- | --- |
| `subactor.sales/decision/v1` | `subactor.sales/decision/v2` |
| `offer.kind`, `offer.entitlement_kind`, `offer.active_twins_included` | usunięte; `offer.commercial_type` z HOME |
| `metering.scope`, `metering.source`, `metering.label_pl` | usunięte; `metering.period` z HOME |
| — | `home.offer_ref`, `home.digest` |
| kody `operations-plus`, `twin-plus` | `pro`, `max` (stare kody tylko do odczytu) |
| reguła `SALES-TWIN-PLUS-PRESENTATION` | usunięta |

## SSOT i zapobieganie driftowi portalu

Ceny, nazwy i limity HOME w `subactor/offer`. Portal `www-sub-actor` trzyma
`src/php_app/config/plans.json` jako fasadę. Przed merge:

```bash
python3 profiles/sales/reference_engine.py compare-offer-home --home-root /path/to/subactor/offer
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans examples/sales/fixtures/www-plans.facade.json
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans /path/to/www-sub-actor/src/php_app/config/plans.json
```

Kolejność zmiany oferty: najpierw nowa wersja katalogu w `subactor/offer`,
potem przepięcie `offer-home.lock.json`, fixture i macierzy tutaj, potem fasada
portalu. Przypięcie do zarchiwizowanego katalogu kończy się błędem i nie wolno
go obchodzić edycją kwot lub nazw w tym repozytorium.

## Relacja do subactor/offer i subactor/brand

Ten profil **ADOPT** identyfikatory planów i reguły promo/kwalifikacji. Nie
twórz tu drugiej tabeli cen, nazw ani słownika marki.
