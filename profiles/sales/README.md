# Profil reguł sprzedażowych Subactor

Status: eksperymentalny profil domenowy Policy DSL v1 (`SUBACTOR_SALES`, wersja 2)

## Cel

Profil przenosi kwalifikację promocji, sanitizację kodu i jego prezentację do
jednego deterministycznego kontraktu. Backend, frontend i warstwa legacy nie
powinny implementować osobnych wariantów tej samej reguły.

Źródłami profilu są:

- `subactor-sales.policy` — deklaratywne reguły kwalifikacji i sanitizacji promocji;
- `offer-catalog.json` — wyłącznie pola należące do profilu: identyfikator planu,
  kod publiczny, zastane kody publiczne (tylko do odczytu), wymóg karty
  i kwalifikujące kody promocyjne;
- `offer-home.lock.json` — przypięty, **aktualny** katalog `subactor/offer`
  (rewizja i digest). Nazwy planów, ceny, waluty i limity operacji pochodzą
  wyłącznie z tego katalogu;
- `reference_engine.py` — inertny evaluator decyzji, bez płatności i bez efektów;
- `decision-matrix.json` — oczekiwane wyniki dla aktualnych planów;
- `ADOPTION_PL.md` — migracja backendu, frontendu i legacy PHP.

Profil nie przechowuje polskich etykiet ani informacji o bliźniakach. Oferta
nie komunikuje już bliźniaków; teksty interfejsu należą do `subactor/offer`
i `subactor/brand`.

## Aktualna reguła NOCC100

Kod `NOCC100` jest kwalifikowany wyłącznie dla planu `saas-start` (kod
publiczny `basic`).

| Plan | NOCC100 | Kod po normalizacji | Prezentacja |
| --- | --- | --- | --- |
| `saas-start` / Basic | `ELIGIBLE` | `NOCC100` | `VISIBLE` |
| `saas-business` / Pro | `INELIGIBLE` | pusty | `HIDDEN` |
| `prepaid-actions` / Max | `INELIGIBLE` | pusty | `HIDDEN` |
| `on-premise` | `INELIGIBLE` | pusty | `HIDDEN` |

Wejście i wyjście są zamknięte przez `schemas/sales-request.schema.json`
(`subactor.sales/request/v2`) oraz `schemas/sales-decision.schema.json`
(`subactor.sales/decision/v2`). Policy DSL zwraca decyzję o kwalifikacji. Nie
obciąża karty, nie modyfikuje subskrypcji i nie uruchamia promocji. Backend
płatności pozostaje jedyną warstwą mogącą zastosować efekt po sprawdzeniu decyzji.

## Kody planów

| Plan | Kod publiczny | Zastany kod (tylko odczyt) |
| --- | --- | --- |
| `saas-start` | `basic` | — |
| `saas-business` | `pro` | `operations-plus` |
| `prepaid-actions` | `max` | `twin-plus` |
| `on-premise` | `on-premise` | — |

Decyzja zawsze zwraca aktualny kod publiczny, nazwę z HOME
(`offer.display_name`), typ handlowy (`offer.commercial_type`), liczbę operacji
i okres rozliczenia (`metering`) oraz powiązanie z katalogiem HOME
(`home.offer_ref`, `home.digest`).

## Semantyka zakazu promocji

Reguła dla planu innego niż Basic ma `TYPE REQUIRED` i emituje
`FORBID APPLY_PROMOTION`, a nie `TYPE FORBIDDEN` dla całego żądania sprzedaży.
Oznacza to:

- kod jest czyszczony i ukrywany;
- promocja nie może zostać zastosowana;
- wybrany plan i zwykły checkout pozostają dostępne;
- decyzja nadal nie jest tokenem autoryzacji płatności.

## Przepływ

```text
surowe plan_id + promo_code
          |
          v
Sales Decision Profile
  - normalizacja kodu
  - katalog profilu + zablokowany katalog HOME
  - Policy DSL
          |
          v
subactor.sales/decision/v2
     |          |          |
  backend    frontend   legacy PHP
  waliduje   renderuje   renderuje
     |
     v
chroniona granica checkout/płatności
```

Obowiązki adapterów:

- backend MUST zastosować promocję tylko dla `eligibility = ELIGIBLE`;
- frontend MUST wysyłać surowy kod do wspólnego evaluatora i renderować
  `normalized_code` oraz `presentation`; nie może mieć własnej listy planów;
- legacy PHP MUST wywoływać ten sam kontrakt albo adapter wygenerowany z tej
  samej polityki i katalogu; `decision-matrix.json` jest fixturem regresyjnym,
  nie źródłem autoryzacji;
- wszystkie warstwy MUST logować `reason`, wersję dokumentu polityki
  i `home.digest`.

## Uruchomienie

```bash
python3 profiles/sales/reference_engine.py decide --plan-id pro --promo-code NOCC100
python3 profiles/sales/reference_engine.py matrix --check profiles/sales/decision-matrix.json
python3 profiles/sales/reference_engine.py compare-offer-home --home-root /path/to/subactor/offer
python3 profiles/sales/reference_engine.py compare-www-plans \
  --plans /path/to/www-sub-actor/src/php_app/config/plans.json
```

`compare-offer-home --home-root` odrzuca przypięty katalog, który nie jest
jedyną aktualną wersją oferty. Zmiana cen, nazw lub limitów zaczyna się
w `subactor/offer`; ten profil tylko przepina lock i odświeża macierz.
