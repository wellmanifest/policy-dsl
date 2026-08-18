# ADOPT: SubLLM credential strategies

HOME: `wellmanifest/policy-dsl` profile `llm-credential`  
Runtime HOME: `subactor/subllm` (`shape: runtime_service`)  
Also ADOPT: `wellmanifest/env-dsl` example `subllm-credential-strategies.env`

## Binding

1. Keep `strategy-catalog.json` and the Env DSL example aligned on env names,
   providers, transports and allowlists.
2. `subllm` Python catalogs (`policy.py`, `subllm.toml`) must not invent a
   parallel OpenRouter wire id for Cursor-only models such as `gpt-5.6-sol`.
3. Secrets stay outside Env DSL / Policy DSL values; only `SECRET` name
   declarations and runtime vault / `.env` carry credentials.

## How to force a model given a key source

| Goal | Required key | Mechanism |
| --- | --- | --- |
| Force Cursor Sol | `CURSOR_API_KEY` | Route lists `cursor` + `gpt-5.6-sol`; leave `SUBLLM_PROVIDER_ORDER` empty or put `cursor` first |
| Force Cursor Grok 4.6 | `CURSOR_API_KEY` | Second cursor candidate (`grok-4.6`); same SDK transport; never OpenRouter |
| Force Z.AI GLM | `ZAI_API_KEY` | Prefer `zai` in order / priorities; model `glm-5.2` |
| Force OpenRouter model | `OPENROUTER_API_KEY` | Prefer `openrouter`; use an allowlisted OpenRouter model only |

Cursor fallback order: `gpt-5.6-sol` then `grok-4.6`.

Missing the key for the selected strategy fails closed.
