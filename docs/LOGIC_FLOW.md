# Logic flow

```text
read inert bytes
  -> parse complete statements
  -> build typed expression/action AST
  -> validate closed Policy IR
  -> resolve explicit Env DSL context
  -> evaluate descriptive rule applicability
  -> propose POA request/plan
  -> require independent authority for effects
```

Failures before the POA boundary are validation findings. They never trigger a
fallback to shell parsing, natural-language interpretation or model judgment.

