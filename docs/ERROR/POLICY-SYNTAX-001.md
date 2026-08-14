# POLICY-SYNTAX-001

## Meaning

Policy text contains bytes, tokens, delimiters, statement order or a Markdown
carrier shape that Policy DSL v1 cannot parse deterministically.

## Cause

The document may contain an unknown statement, unbalanced expression, invalid
metadata order, unfinished `dsl` fence, or policy syntax in a non-policy code
fence.

## Resolution

Use the grammar in `spec/policy-dsl.ebnf`. In Markdown, place the concrete
document header and every normative fragment in selected `dsl` fences, then
run `python3 tests/policy_dsl_check.py validate-markdown <path>`. For a
standalone policy file, run the `validate` command instead.
