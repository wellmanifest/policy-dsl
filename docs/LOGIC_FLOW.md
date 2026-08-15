# Logic flow

```text
read inert bytes
  -> parse complete statements
  -> build typed expression/directive AST (`action` is the IR compatibility name)
  -> validate closed Policy IR
  -> resolve explicit Env DSL or application context
  -> evaluate descriptive rule applicability
  -> optionally reduce profile-safe proposals to an inert decision
  -> backend revalidates protected commercial or POA context
  -> propose POA request/plan
  -> require independent authority for effects
```

Failures before the protected authority boundary are validation findings. They
never trigger a fallback to shell parsing, natural-language interpretation,
client-side trust, last-writer-wins conflict resolution or model judgment.

In the Subactor sales profile, the same inert decision drives backend promo
eligibility plus frontend and legacy presentation. Only the backend may bind
that decision to checkout, prices, tax and account entitlements.
