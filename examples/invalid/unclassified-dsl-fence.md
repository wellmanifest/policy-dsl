# Unclassified dsl fence

A completion function written in a `dsl` fence looks normative, but it is not
Policy DSL. A conforming carrier rejects it instead of silently dropping it.

```dsl
DOCUMENT CONTRIBUTING
VERSION 1
LANGUAGE EN
MODE PROCEDURAL
```

```dsl
RULE C-DONE-001 TYPE REQUIRED
WHEN COMPLETION_CLAIMED
DO REQUIRE TESTS_PASSED
```

```dsl
DONE WHEN
  USER_SCOPE_COMPLETED
  AND TEST_STATUS_REPORTED
```
