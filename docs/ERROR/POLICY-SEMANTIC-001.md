# POLICY-SEMANTIC-001

## Meaning

Policy text is syntactically recognizable but violates the closed Policy DSL
v1 identity, uniqueness or typed Policy IR contract.

## Cause

Typical causes are duplicate rule, state or binding names; an unsupported
scalar type; an invalid default value; or an unknown or missing Policy IR
field.

## Resolution

Restore unique stable identifiers and values allowed by
`schemas/policy-ir.schema.json`. Rerun the reference checker with `ir
<path> --check-schema` and do not add consumer-specific fields to Policy IR.
