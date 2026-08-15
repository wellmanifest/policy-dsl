# Słownik domenowy agentów i cyfrowych bliźniaków

Status: rekomendowany profil terminologiczny

## Decyzja nazewnicza

Kanoniczną nazwą jednostki pracy wykonywanej przez agenta jest **operacja
agenta** (`AGENT_OPERATION`). W warstwie handlowej i interfejsie należy używać
formy „operacje agenta”, a nie „akcje”.

„Akcja” pozostaje techniczną nazwą kompatybilności w Policy IR v1 (`actions`,
`kind: action`). Oznacza tam deklaratywną dyrektywę polityki, a nie jednostkę
rozliczeniową produktu. Nie wolno używać jednego licznika do obu znaczeń.

## Kanoniczna taksonomia

| Pojęcie | Identyfikator | Znaczenie |
| --- | --- | --- |
| Zdarzenie | `EVENT` | Fakt wejściowy zaobserwowany albo wyemitowany w środowisku. Zdarzenie zachodzi; agent go nie „wykonuje”. |
| Zadanie | `TASK` | Cel lub element pracy powierzony agentowi albo grupie agentów. |
| Wykonanie zadania | `TASK_RUN` | Jedna ograniczona próba realizacji zadania lub procesu; może zawierać wiele operacji. |
| Operacja agenta | `AGENT_OPERATION` | Pojedyncza, rozliczana jednostka pracy agenta, np. analiza, decyzja, wywołanie narzędzia, walidacja lub zapis wyniku. |
| Efekt | `EFFECT` | Zewnętrznie obserwowalna zmiana stanu, która wymaga odrębnej autoryzacji. |
| Dyrektywa polityki | `POLICY_DIRECTIVE` | Inertny opis wymogu, zakazu, walidacji lub raportu w Policy DSL. |

Relacja pojęć:

```text
EVENT -> TASK -> TASK_RUN -> AGENT_OPERATION* -> EFFECT?
                         ^
                         |
                  POLICY_DIRECTIVE
```

Zdarzenie może utworzyć zadanie. Wykonanie realizuje zadanie i zawiera zero lub
więcej operacji agenta. Operacja nie musi tworzyć efektu zewnętrznego.
Każdy efekt przechodzi przez niezależną granicę autoryzacji.

## Nazwy produktowe

Rekomendowane nazwy publiczne:

- `Actions Plus` -> **Operations Plus**;
- „akcje agenta” -> **operacje agenta**;
- „pakiet akcji” -> **pakiet operacji**;
- „limit akcji” -> **limit operacji agenta**.

Identyfikatory techniczne mogą pozostać przejściowo bez zmian, jeżeli są już
częścią API, bazy danych lub rozliczeń. Warstwa kompatybilności powinna jednak
mapować je na jednoznaczne kody publiczne:

| Identyfikator zastany | Kod publiczny | Znaczenie |
| --- | --- | --- |
| `saas-start` | `basic` | Plan bazowy |
| `saas-business` | `operations-plus` | Dodatek operacji |
| `prepaid-actions` | `twin-plus` | Dodatek aktywnego bliźniaka |
| `actions_included` | `agent_operations_included` | Liczba operacji w pakiecie |

Nowy kod zapisuje wyłącznie nazwy kanoniczne. Odczyt aliasów zastanych MAY być
utrzymany przez jeden okres migracyjny.

## Etykieta Twin Plus

Wartość `agent_operations_included: 0` jest prawidłowa, ale tekst „Brak” jest
niejednoznaczny: może sugerować brak możliwości wykonywania operacji. Zalecana etykieta to:

```text
0 operacji w pakiecie — dokupujesz przez Operations Plus
```

Krótsza wersja do wiersza podsumowania:

```text
1 aktywny bliźniak • 0 operacji w pakiecie
```

## Nazwy alternatywne i ich zakres

`AGENT_OPERATION` jest nazwą rekomendowaną dla API, telemetrii i rozliczeń.
Inne określenia mogą być użyte wyłącznie w węższym znaczeniu:

| Określenie | Zalecenie | Powód |
| --- | --- | --- |
| **czynność agenta** | Dopuszczalne w prostym tekście UI | Naturalne po polsku, ale słabsze jako stabilny identyfikator techniczny. |
| **krok agenta** (`AGENT_STEP`) | Tylko dla etapu przebiegu | Krok może grupować kilka operacji albo nie być rozliczany. |
| **wykonanie zadania** (`TASK_RUN`) | Dla całej próby realizacji zadania | Jedno wykonanie zwykle zawiera wiele operacji i retry. |
| **jednostka pracy agenta** | Dobra definicja opisowa | Precyzyjna, lecz zbyt długa jako nazwa produktu i pola API. |
| **działanie agenta** | Dopuszczalne w narracji | Nadal zbyt bliskie wieloznacznemu „action”; nie używać jako kodu licznika. |
| **zdarzenie** (`EVENT`) | Nie używać jako synonimu pracy | Zdarzenie jest faktem wejściowym lub wynikiem, a nie wykonywaną jednostką. |
| **zadanie** (`TASK`) | Nie używać jako synonimu operacji | Zadanie opisuje cel; jego realizacja może wymagać wielu operacji. |

W konsekwencji nazwy pól powinny wskazywać poziom abstrakcji, na przykład:

```text
TASK_ID
TASK_RUN_ID
AGENT_OPERATION_ID
AGENT_OPERATIONS_INCLUDED
AGENT_OPERATIONS_USED
AGENT_OPERATIONS_REMAINING
```
