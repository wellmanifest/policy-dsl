# POLICY-SECURITY-001

## Risk

Policy input crosses the inert-data boundary by containing shell syntax,
executable interpolation, secret material or an LLM candidate field/opcode
that could claim runtime authority.

## Detection

Run the reference checker against the complete source or candidate. The
checker rejects shell constructs in selected Policy DSL and restricts model
candidates to the proposal-only action vocabulary.

## Remediation

Replace executable syntax with typed Policy DSL symbols and expressions. Keep
secret values in a separate governed secret provider, and send proposed
effects through an independently authorized POA controller. Never weaken the
parser or execute rejected input.

## Verification

Rerun validation and confirm that no `POLICY-SECURITY-001` finding remains.
Then verify independently that the consuming runtime does not use `eval`, a
shell parser or model output as authority.
