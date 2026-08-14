# Policy DSL Standard 1

Status: experimental normative specification

Canonical identifier: `wellmanifest.policy/v1`

Compatibility alias: `policy-sh@1`

Canonical media type: `application/vnd.wellmanifest.policy`

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT and MAY are
normative when written in uppercase.

## 1. Identity and versioning

Policy DSL is an inert language for repository and process policy. The
language major is `1`; it changes only when syntax or semantics become
incompatible. `VERSION` inside a document is the revision of that consuming
document or profile. Therefore `CONTRIBUTING VERSION 13`, `policy-sh@1` and
`wellmanifest.policy/v1` are compatible identities at different layers, not
three competing revisions of one contract.

The historical `policy-sh@1` name remains a compatibility alias for runtimes.
It MUST NOT imply that Policy DSL is shell, that actions are commands, or that
parsing grants permission to execute them.

## 2. Processing model

A conforming consumer performs these stages in order:

1. read UTF-8 text without execution;
2. parse the complete grammar in `policy-dsl.ebnf`;
3. normalize all expressions and actions to Policy IR;
4. validate the closed `policy-ir.schema.json` contract;
5. evaluate descriptive conditions from an explicit input context;
6. send any proposed effect to an independently governed POA process.

Policy text and Policy IR are declarative data. Neither is an authority token.
Unknown syntax, fields, operators, action shapes and unresolved symbols MUST be
rejected. A consumer MUST NOT use `eval`, a shell parser or host-language
expression semantics as a substitute for this pipeline.

## 3. Documents and rules

Every document declares `DOCUMENT`, integer `VERSION` and `MODE`; `LANGUAGE`,
`PURPOSE` and `POLICY` are optional metadata. A rule has a stable identifier,
one `WHEN` expression, zero or more typed `DO`, `FORBID` and `ASSERT` clauses,
and optional `NEXT` targets. `TYPE REQUIRED` is the default. `TYPE FORBIDDEN`
describes a blocking policy rule and does not turn its payload into executable
code.

An action consists of an uppercase opcode, an optional typed payload and an
optional typed guard. Adjacent payload expressions form a `sequence` node;
their source is never stored as an opaque command string. An implementation
MAY map domain opcodes to capabilities only after separate authorization.
Legacy predicate-style conditions with adjacent terms are normalized to the
same typed `sequence` node; consumers MUST resolve that predicate explicitly
and MUST reject it when no domain binding exists.

`STATE` and `TRANSITION A -> B WHEN ...` describe a state graph. Declaring a
transition does not authorize the transition. A consumer MUST independently
verify its input, policy, current state and authority.

### 3.1 Markdown carrier

A Markdown carrier such as `CONTRIBUTING.md` MAY distribute one policy
document across fenced code blocks. The selector is deterministic:

1. select the first `dsl` fence whose first statement is a concrete
   `DOCUMENT <symbol>` header;
2. ignore illustrative fences containing placeholder metadata and independent
   embedded document types;
3. after the header, select a `dsl` fence only when its first statement begins
   with `RULE`, `STATE`, `TRANSITION`, `ENV_FILE`, `VARIABLE`, `SECRET` or
   `ASSERT`, or is a top-level `symbol = expression` / `symbol IN list` binding;
4. concatenate selected fences in source order and parse the complete result.

Other Markdown, `bash` fences and independent DSL documents MUST NOT be
interpreted as Policy DSL. Once a fence is selected, every statement in it is
normative and a parse failure MUST NOT be silently skipped.

## 4. Expressions

The portable scalar types are string, integer, number and boolean. Symbols and
`{PLACEHOLDER}` values are references resolved by the consumer's explicit
context. There is no ambient lookup and no implicit scalar coercion.

Operators, from highest to lowest precedence, are:

| Precedence | Operators | Meaning |
| --- | --- | --- |
| 7 | unary `NOT`, unary `-` | boolean negation, numeric negation |
| 6 | `*`, `/`, `%` | arithmetic |
| 5 | `+`, `-` | arithmetic |
| 4 | `<`, `<=`, `>`, `>=` | ordered comparison |
| 3 | `=`, `!=` | equality |
| 2 | `IN` | membership |
| 1 | `AND`, `OR` | short-circuit boolean operations |

Parentheses override precedence. Lists preserve order. A parser MUST produce
the typed recursive nodes defined by Policy IR and MUST NOT preserve an
expression only as unparsed text.

## 5. Environment composition

`ENV_FILE`, `VARIABLE` and `SECRET` declarations are a compatibility surface
for existing `wellmanifest.new-project.contributing` documents. A Policy DSL
parser records them as typed environment bindings but MUST NOT interpret them
as shell declarations.

New portable constant sets SHOULD use `wellmanifest.env` and its normative
ABNF, layering and evaluator. Integration follows this boundary:

```text
Env DSL files --validate/evaluate--> inert typed context
                                           |
Policy DSL --parse--> Policy IR -----------+--> condition evaluation
                                                    |
                                                    v
                                      POA request/plan boundary
```

Secrets MUST remain outside Env DSL and Policy DSL values. A `SECRET`
compatibility declaration identifies a required name and redaction duty; its
value is supplied through a separately governed secret provider.

## 6. LLM generation and POA

`policy-dsl-candidate.v1.gbnf` is a generation projection, not the canonical
text grammar. A model MAY generate only output accepted by both that GBNF and
the closed Policy IR Schema. Its action vocabulary is limited to `REQUIRE`,
`ALLOW`, `REPORT`, `VALIDATE` and `RECORD`. The grammar cannot emit arbitrary
fields, execution envelopes, credentials, approval evidence or shell actions.

The model has `propose-only` authority. A generated candidate MUST be parsed,
schema-validated, checked against policy and then bound to the POA request and
plan contracts. Only a protected POA controller may turn an approved plan into
an execution envelope. MCP MAY transport schemas, candidates and diagnostics,
but MCP transport never widens model authority and is not part of Policy DSL
semantics.

For interactive generation, a server SHOULD expose:

- the exact Policy IR Schema and candidate GBNF;
- a validation operation returning stable diagnostics;
- a parse/normalize operation returning Policy IR;
- POA inspect/plan operations separately from any command operation.

## 7. Conformance and alternative runtimes

An implementation conforms when it accepts every `conformance.valid` fixture,
rejects every `conformance.invalid` fixture with a stable code, and produces
structurally equal Policy IR after canonical JSON serialization. Implementers
in Python, TypeScript, Rust or another language use the same EBNF, closed
Schema, fixtures and manifest digests. Parser libraries such as Lark, TatSu,
textX, pest, nom, Ohm, nearley or ANTLR are implementation choices; none may
change the language contract.

The reference Python checker has no runtime dependencies. It validates and
normalizes Policy DSL; it deliberately has no executor.

## 8. Diagnostics

- `POLICY-SYNTAX-001`: bytes, tokens or statement order violate the grammar;
- `POLICY-SEMANTIC-001`: identity, uniqueness, references or typed structure
  violate Policy DSL semantics;
- `POLICY-SECURITY-001`: executable interpolation, shell syntax, secret value
  or candidate authority field crosses the inert boundary.

Tools MAY add locations and details but MUST NOT change a code's meaning
within Policy DSL major version 1.
