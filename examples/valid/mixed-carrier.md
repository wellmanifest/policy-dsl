# Mixed carrier

A domain document with its own schema is an independent document, even when it
appears before the Policy DSL header.

```dsl
DOCUMENT TWIN_LIFECYCLE
VERSION 1
LANGUAGE EN
MODE STRICT
SCHEMA "wellmanifest.twin-lifecycle/v1"
```

```dsl
DOCUMENT CONTRIBUTING
VERSION 1
LANGUAGE EN
MODE PROCEDURAL
```

A registered decision record is an independent record, not a policy fragment.

```dsl
DECISION D-001-0001
TICKET ticket-001
VERDICT APPROVE AUTHORITY DETERMINISTIC
ASSERT VERDICT_AUTHORITY != "ADVISORY"
```

```dsl
STATE EDIT
STATE DONE

RULE C-DONE-001 TYPE REQUIRED
WHEN COMPLETION_CLAIMED
DO REQUIRE TESTS_PASSED
ASSERT REPORT_INCLUDES_TEST_STATUS = TRUE
NEXT DONE
```
