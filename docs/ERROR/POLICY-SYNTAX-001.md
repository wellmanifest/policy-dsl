# POLICY-SYNTAX-001

## Meaning

Policy text contains bytes, tokens, delimiters, statement order or a Markdown
carrier shape that Policy DSL v1 cannot parse deterministically.

## Cause

The document may contain an unknown statement, unbalanced expression, invalid
metadata order, unfinished `dsl` fence, or policy syntax in a non-policy code
fence. In a Markdown carrier, a `dsl` fence that is neither Policy DSL,
placeholder metadata, an independent `DOCUMENT` nor a registered record kind
(for example `DONE WHEN ...`) is rejected instead of being silently dropped, as
is a policy fragment placed before the `DOCUMENT` header.

## Resolution

Use the grammar in `spec/policy-dsl.ebnf`. In Markdown, place the concrete
document header and every normative fragment in selected `dsl` fences, then
run `python3 tests/policy_dsl_check.py validate-markdown <path>`. Rewrite an
unclassified fence as Policy DSL rules, or move a non-normative example to a
`text` fence. For a
standalone policy file, run the `validate` command instead.
