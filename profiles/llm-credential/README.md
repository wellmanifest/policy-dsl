# SubLLM credential-strategy profile

Status: experimental Policy DSL v1 profile for `subactor/subllm`.

## Purpose

Map **credential source → provider → allowed models → strategy** without
pinning Cursor-only models onto OpenRouter wire ids.

| Credential env | Strategy / provider | Transport | Default model | Allowed models |
| --- | --- | --- | --- | --- |
| `CURSOR_API_KEY` | `cursor` | `cursor-sdk` | `gpt-5.6-sol` | `gpt-5.6-sol` |
| `ZAI_API_KEY` | `zai` | openai-compatible | `glm-5.2` | `glm-5.2` |
| `OPENROUTER_API_KEY` | `openrouter` | openai-compatible | `glm-5.2` | glm / grok / gemini-flash / deepseek / qwen |

`gpt-5.6-sol` is Cursor-only. OpenRouter must not claim `openai/gpt-5.6-sol`.

## Sources

- `subactor-llm-credential.policy` — fail-closed routing rules
- `strategy-catalog.json` — closed catalog projection for runtimes
- Env DSL twin: `wellmanifest/env-dsl` `examples/valid/subllm-credential-strategies.env`

## Runtime adopter

`subactor/subllm` ADOPTs this profile: Python catalogs and `resolve()` must
match the catalog. Missing credentials fail closed. Fallback order is
`SUBLLM_PROVIDER_ORDER` or the catalog defaults.

## Validate

```bash
python3 tests/policy_dsl_check.py validate profiles/llm-credential/subactor-llm-credential.policy
```
