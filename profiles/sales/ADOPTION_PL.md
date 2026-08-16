# Adopcja profilu sprzedażowego

## Cel zmiany

Obecny warunek NOCC100 jest powtórzony w backendzie, frontendzie i legacy PHP.
Docelowo wszystkie trzy warstwy konsumują jedną decyzję
`subactor.sales/decision/v1`. Tylko backend płatności może zastosować efekt.

## Kontrakt wejściowy

```json
{
  "schema": "subactor.sales/request/v1",
  "plan_id": "saas-start",
  "promo_code": "NOCC100"
}
```

`plan_id` może być zastanym identyfikatorem (`saas-start`, `saas-business`,
`prepaid-actions`, `on-premise`) albo kodem publicznym (`basic`,
`operations-plus`, `twin-plus`). Odpowiedź zawsze zawiera zastany identyfikator
i kod publiczny, dzięki czemu migracja nie wymaga jednorazowej zmiany bazy.

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

Backend MUST ponownie sprawdzić wersję polityki i plan przed efektem płatniczym.
Decyzja nie jest tokenem autoryzacji.

## Frontend

Frontend nie sanitizuje kodu zależnie od planu. Przesyła surową wartość i
renderuje wyłącznie odpowiedź:

```text
promoInput.value = decision.promotion.normalized_code
promoBadge.visible = decision.promotion.presentation == "VISIBLE"
promoMessage = localize(decision.promotion.reason)
```

Dla Operations Plus, Twin Plus i on-premise kod NOCC100 wraca jako pusty i
`HIDDEN`. Na kartach tych ofert nie może być statycznego komunikatu o NOCC100.

## Legacy PHP

Preferowana integracja to ten sam endpoint lub ta sama biblioteka decyzyjna.
Jeżeli legacy nie może jej wywołać, pipeline wydania MAY wygenerować zamknięty
adapter na podstawie tego samego katalogu i polityki. `decision-matrix.json`
służy jako fixture regresyjny producenta, a nie jako samodzielny token autoryzacji.
Konsumenci porównują z zamrożonym eksportem
`examples/sales/decisions/matrix.v1.json` (`subactor.sales/decision/v1`)
albo wołają `reference_engine.py decide` / `export-decisions --check`.
Wygenerowany adapter musi być związany z wersją polityki i digestem; ręcznie
utrzymywany `if ($plan !== 'saas-start')` pozostaje tylko na czas migracji.

## Teksty interfejsu

| Miejsce | Tekst kanoniczny |
| --- | --- |
| Nazwa dodatku `saas-business` | `Operations Plus` |
| Basic | `1 000 operacji agenta odnawianych co miesiąc` |
| Operations Plus | `1 000 operacji agenta odnawianych co miesiąc` |
| Twin Plus — podsumowanie | `1 aktywny bliźniak • 0 operacji w pakiecie` |
| Twin Plus — szczegół | `0 operacji w pakiecie — dokupujesz przez Operations Plus` |
| Pole kompatybilności | odczyt `actions_included`, zapis `agent_operations_included` |

## Kolejność wdrożenia

1. Uruchom evaluator w trybie obserwacyjnym i porównuj jego decyzję z trzema
   istniejącymi implementacjami.
2. Zablokuj wydanie przy rozbieżności macierzy dla czterech aktualnych planów.
3. Przełącz backend na decyzję jako źródło kwalifikacji.
4. Przełącz frontend i legacy na renderowanie tej samej odpowiedzi.
5. Usuń statyczny komunikat NOCC100 z Operations Plus i etykietę „Brak” z Twin
   Plus.
6. Po okresie kompatybilności przestań zapisywać nazwy `Actions Plus` i
   `actions_included`.


## SSOT i zapobieganie driftowi portalu

**List prices HOME w `subactor/offer`.** Katalog (`offer-catalog.json`) jest
projekcją ADOPT dla:

- `agent_operations_included` / `actions_included`,
- `active_twins_included`,
- lustrzanych `amount_monthly_minor` / `amount_annual_minor` / `currency`
  (musi być zsynchronizowany z `subactor/offer`, nie jest publicznym arkuszem),
- nazw kanonicznych i aliasów (`Actions Plus` → `Operations Plus`).

Portal `www-sub-actor` trzyma `src/php_app/config/plans.json` jako fasadę.
Przed merge:

```bash
python3 profiles/sales/reference_engine.py validate-catalog
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans examples/sales/fixtures/www-plans.facade.json
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans /path/to/www-sub-actor/src/php_app/config/plans.json
```

Fixture CI: `examples/sales/fixtures/www-plans.facade.json` +
`profiles/sales/www-plans.lock.json` (ten sam pin
`offer://subactor/offer/subactor-cloud/v1`).

Zmiana cen albo pakietów najpierw w `subactor/offer`, potem synchronizacja
lustra katalogu i macierzy tutaj, potem fasada portalu. FEATURE ticket nie może
samodzielnie przepisać `plans.json` ani złotych testów oferty bez bumpa oferty
i katalogu.


## Relacja do subactor/offer i subactor/brand

List prices i publiczne arkusze planów HOME w `subactor/offer`
(`subactor.offer/catalog/v1`). Słownik nazw i tokenów marki HOME w
`subactor/brand`. Ten profil **ADOPT** identyfikatory planów i reguły
promo/kwalifikacji. Nie twórz drugiej kanonicznej tabeli cen ani słownika
marki tutaj — przy zmianie oferty najpierw bump katalogu w `offer` (i słownika
w `brand` jeśli zmieniają się nazwy), potem zsynchronizuj
`offer-catalog.json` / macierz, potem fasadę portalu.

