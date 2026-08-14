# Architecture

```text
Policy DSL text
      |
      v
deterministic parser ---> stable diagnostics
      |
      v
closed Policy IR Schema <--- GBNF-safe LLM candidate
      |
      v
descriptive evaluator ---> POA controller ---> separately authorized effect
```

The standard owns syntax, normalized IR and conformance. A runtime owns parsing
and descriptive evaluation. A POA controller owns effect and approval policy.
No arrow from model output or Policy IR bypasses that controller.

