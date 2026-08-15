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
      +--> core descriptive evaluator ---> POA controller ---> authorized effect
      |
      +--> application profile reducer ---> inert domain decision
                                               |
                                               +--> backend validation
                                               +--> frontend projection
                                               +--> legacy projection
```

The standard owns syntax, normalized IR and conformance. A runtime owns parsing
and descriptive evaluation. An application profile may define domain symbols
and inert decision fields but cannot widen authority. A POA or protected
commerce controller owns effects and approval policy. No arrow from model
output, Policy IR, a profile decision, frontend code or legacy code bypasses
that controller.
