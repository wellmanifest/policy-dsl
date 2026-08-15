# Profil reguł sprzedażowych Subactor

Status: eksperymentalny profil domenowy Policy DSL v1

## Cel

Profil przenosi kwalifikację promocji, sanitizację kodu, prezentację kodu i
etykiety pakietów do jednego deterministycznego kontraktu. Backend, frontend i
warstwa legacy nie powinny implementować osobnych wariantów tej samej reguły.

Źródłami profilu są:

- `subactor-sales.policy` — deklaratywne reguły kwalifikacji, sanitizacji i
  niejednoznacznej prezentacji;
- `offer-catalog.json` — kanoniczny katalog planów, uprawnień i słownik operacji
  agenta;
- `reference_engine.py` — inertny evaluator decyzji, bez płatności i bez efektów;
- `decision-matrix.json` — oczekiwane wyniki dla aktualnych planów;
- `ADOPTION_PL.md` — migracja backendu, frontendu i legacy PHP.

## Aktualna reguła NOCC100

Kod `NOCC100` jest kwalifikowany wyłącznie dla planu o zastanym identyfikatorze
`saas-start` i publicznym kodzie `basic`.

| Plan | NOCC100 | Kod po normalizacji | Prezentacja |
| --- | --- | --- | --- |
| `saas-start` / Basic | `ELIGIBLE` | `NOCC100` | `VISIBLE` |
| `saas-business` / Operations Plus | `INELIGIBLE` | pusty | `HIDDEN` |
| `prepaid-actions` / Twin Plus | `INELIGIBLE` | pusty | `HIDDEN` |
| `on-premise` | `INELIGIBLE` | pusty | `HIDDEN` |

Wejście i wyjście są zamknięte przez `schemas/sales-request.schema.json` oraz
`schemas/sales-decision.schema.json`. Policy DSL zwraca decyzję o kwalifikacji.
Nie obciąża karty, nie modyfikuje
subskrypcji i nie uruchamia promocji. Backend płatności pozostaje jedyną
warstwą mogącą zastosować efekt po sprawdzeniu decyzji.

## Odwzorowanie aktualnej implementacji

Profil zachowuje obecną semantykę trzech warstw, ale usuwa trzy niezależne
źródła reguły:

| Obecne miejsce | Odpowiednik w decyzji profilu |
| --- | --- |
| `PromoEngine::apply(...)` i warunek planu | `promotion.eligibility`, `normalized_code` oraz dyrektywa `FORBID APPLY_PROMOTION` |
| sanitizacja kodu w frontendzie | `promotion.normalized_code` i `promotion.presentation` |
| czyszczenie `?promo=NOCC100` w legacy PHP | ten sam `normalized_code = ""` i `presentation = "HIDDEN"` |
| opis pakietów i liczników w UI | `offer-catalog.json` oraz `metering` w decyzji |

Backend pozostaje autorytatywny. Frontend i legacy nie powinny ponownie
obliczać kwalifikacji na podstawie identyfikatora planu.

## Semantyka zakazu promocji

Reguła dla planu innego niż Basic ma `TYPE REQUIRED` i emituje
`FORBID APPLY_PROMOTION`, a nie `TYPE FORBIDDEN` dla całego żądania sprzedaży.
Oznacza to:

- kod jest czyszczony i ukrywany;
- promocja nie może zostać zastosowana;
- wybrany plan i zwykły checkout pozostają dostępne;
- decyzja nadal nie jest tokenem autoryzacji płatności.

## Jedna decyzja i rozdzielone odpowiedzialności

Katalog jest źródłem danych o ofercie i limitach. Polityka jest źródłem reguł
kwalifikacji i zakazów. Evaluator odrzuca rozjazd ich zamkniętych kontraktów i
emituje jeden wynik dla wszystkich adapterów.

Docelowy przepływ:

```text
surowe plan_id + promo_code
          |
          v
Sales Decision Profile
  - normalizacja
  - katalog planów
  - Policy DSL
          |
          v
subactor.sales/decision/v1
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
  nie źródłem autoryzacji; legacy nie może powielać warunku `plan !=`;
- wszystkie warstwy MUST logować `reason` i wersję dokumentu polityki.

## Migracja nazewnictwa

Kanoniczna jednostka handlowa to `AGENT_OPERATION` — „operacja agenta”. Nazwa
`Actions Plus` pozostaje aliasem historycznym; nazwa publiczna profilu to
`Operations Plus`. Pole `actions_included` jest aliasem odczytu dla
`agent_operations_included`.

Twin Plus ma zero własnych operacji, ponieważ dodaje aktywnego bliźniaka.
Interfejs nie pokazuje „Brak”, tylko „0 operacji w pakiecie — dokupujesz
przez Operations Plus”.

## Uruchomienie

```bash
python3 profiles/sales/reference_engine.py decide \
  --plan-id saas-start \
  --promo-code NOCC100

python3 profiles/sales/reference_engine.py matrix
python3 profiles/sales/reference_engine.py matrix \
  --check profiles/sales/decision-matrix.json
```
