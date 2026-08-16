#!/usr/bin/env python3
"""Reference evaluator for the inert Subactor sales Policy DSL profile.

The evaluator returns a closed descriptive decision. It never applies a
promotion, charges a card, mutates a subscription, or executes a policy
directive. Effectful checkout code remains a separate authorization boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "profiles/sales/subactor-sales.policy"
CATALOG_PATH = ROOT / "profiles/sales/offer-catalog.json"
OFFER_HOME_LOCK_PATH = ROOT / "profiles/sales/offer-home.lock.json"
CHECKER_PATH = ROOT / "tests/policy_dsl_check.py"

POLICY_DOCUMENT = "SUBACTOR_SALES"
POLICY_VERSION = 1
METERING_UNIT = "AGENT_OPERATION"

ALLOW_VALUES = {"APPLY_PROMOTION"}
REQUIRE_VALUES = {"PROMOTION_SANITIZED"}
REPORT_VALUES = {"OPERATIONS_PURCHASED_SEPARATELY"}
FORBIDDEN_OPCODES = {
    "APPLY_PROMOTION",
    "DISPLAY_PROMOTION",
    "DISPLAY_OPERATION_LABEL",
}


class SalesPolicyError(ValueError):
    """Raised when the sales profile cannot produce a deterministic decision."""


def _load_policy_checker() -> Any:
    spec = importlib.util.spec_from_file_location("policy_dsl_check_sales", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise SalesPolicyError(f"cannot load Policy DSL checker from {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECK = _load_policy_checker()


def _exact_keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise SalesPolicyError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise SalesPolicyError(
            f"closed {label}: unknown={sorted(actual - expected)}, "
            f"missing={sorted(expected - actual)}"
        )


def _require_string(value: Any, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value:
        raise SalesPolicyError(f"{label} must be a non-empty string")


def _require_optional_non_negative_integer(value: Any, label: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SalesPolicyError(f"{label} must be a non-negative integer or null")


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the closed current offer catalog."""

    catalog_path = CATALOG_PATH if path is None else path
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"catalog is unreadable: {error}") from error

    _exact_keys(catalog, {"schema", "vocabulary", "compatibility", "plans"}, "catalog")
    if catalog["schema"] != "subactor.sales/catalog/v1":
        raise SalesPolicyError("incompatible sales catalog schema")

    vocabulary = catalog["vocabulary"]
    _exact_keys(
        vocabulary,
        {"unit_code", "label_pl_singular", "label_pl_plural", "definition_pl"},
        "catalog vocabulary",
    )
    if vocabulary["unit_code"] != METERING_UNIT:
        raise SalesPolicyError(f"sales catalog must use {METERING_UNIT}")
    if vocabulary["label_pl_singular"] != "operacja agenta":
        raise SalesPolicyError("catalog singular label must be 'operacja agenta'")
    if vocabulary["label_pl_plural"] != "operacje agenta":
        raise SalesPolicyError("catalog plural label must be 'operacje agenta'")
    _require_string(vocabulary["definition_pl"], "catalog vocabulary definition")

    compatibility = catalog["compatibility"]
    _exact_keys(compatibility, {"read_aliases", "write_policy"}, "catalog compatibility")
    if compatibility["write_policy"] != "CANONICAL_ONLY":
        raise SalesPolicyError("catalog must write canonical names only")
    if compatibility["read_aliases"] != {
        "actions_included": "agent_operations_included",
        "Actions Plus": "Operations Plus",
    }:
        raise SalesPolicyError("catalog compatibility aliases are incomplete")

    plan_keys = {
        "plan_id",
        "public_code",
        "kind",
        "entitlement_kind",
        "display_name",
        "legacy_display_names",
        "active_twins_included",
        "agent_operations_included",
        "operation_scope",
        "operations_source",
        "payment_card_required",
        "eligible_promo_codes",
        "seat_summary_pl",
        "operation_label_pl",
        "promo_hint_pl",
        "amount_monthly_minor",
        "amount_annual_minor",
        "currency",
    }
    plans = catalog["plans"]
    if not isinstance(plans, list) or not plans:
        raise SalesPolicyError("catalog plans must be a non-empty array")

    plan_ids: set[str] = set()
    public_codes: set[str] = set()
    for index, plan in enumerate(plans):
        _exact_keys(plan, plan_keys, f"plan[{index}]")
        plan_id = plan["plan_id"]
        public_code = plan["public_code"]
        if not isinstance(plan_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", plan_id):
            raise SalesPolicyError(f"invalid plan_id at plan[{index}]")
        if not isinstance(public_code, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", public_code):
            raise SalesPolicyError(f"invalid public_code at plan[{index}]")
        if plan_id in plan_ids or public_code in public_codes:
            raise SalesPolicyError("duplicate plan_id or public_code")
        plan_ids.add(plan_id)
        public_codes.add(public_code)

        if plan["kind"] not in {"BASE_PLAN", "OPERATIONS_ADDON", "TWIN_ADDON", "OFFLINE_OFFER"}:
            raise SalesPolicyError(f"invalid plan kind for {plan_id}")
        if plan["entitlement_kind"] not in {
            "DIGITAL_TWIN_WITH_OPERATIONS",
            "AGENT_OPERATIONS",
            "DIGITAL_TWIN",
            "CONTRACT",
        }:
            raise SalesPolicyError(f"invalid entitlement kind for {plan_id}")
        if plan["operation_scope"] not in {"PER_TWIN_MONTH", "ACCOUNT_MONTH", "NONE", "CONTRACT"}:
            raise SalesPolicyError(f"invalid operation scope for {plan_id}")
        if plan["operations_source"] not in {"INCLUDED", "ADD_ON", "SEPARATE_PACKAGE", "CONTRACT"}:
            raise SalesPolicyError(f"invalid operations source for {plan_id}")

        _require_string(plan["display_name"], f"display_name for {plan_id}")
        _require_string(plan["seat_summary_pl"], f"seat_summary_pl for {plan_id}")
        _require_string(plan["operation_label_pl"], f"operation_label_pl for {plan_id}")
        _require_string(plan["promo_hint_pl"], f"promo_hint_pl for {plan_id}", nullable=True)

        legacy_names = plan["legacy_display_names"]
        if (
            not isinstance(legacy_names, list)
            or len(legacy_names) != len(set(legacy_names))
            or any(not isinstance(name, str) or not name for name in legacy_names)
        ):
            raise SalesPolicyError(f"invalid legacy_display_names for {plan_id}")

        _require_optional_non_negative_integer(
            plan["active_twins_included"], f"active_twins_included for {plan_id}"
        )
        _require_optional_non_negative_integer(
            plan["agent_operations_included"], f"agent_operations_included for {plan_id}"
        )
        _require_optional_non_negative_integer(
            plan["amount_monthly_minor"], f"amount_monthly_minor for {plan_id}"
        )
        _require_optional_non_negative_integer(
            plan["amount_annual_minor"], f"amount_annual_minor for {plan_id}"
        )
        currency = plan["currency"]
        if currency is not None and (
            not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency)
        ):
            raise SalesPolicyError(f"invalid currency for {plan_id}")
        card_required = plan["payment_card_required"]
        if card_required is not None and not isinstance(card_required, bool):
            raise SalesPolicyError(f"invalid payment_card_required for {plan_id}")

        promo_codes = plan["eligible_promo_codes"]
        if not isinstance(promo_codes, list) or len(promo_codes) != len(set(promo_codes)):
            raise SalesPolicyError(f"invalid eligible_promo_codes for {plan_id}")
        if any(
            not isinstance(code, str)
            or not re.fullmatch(r"[A-Z0-9_-]+", code)
            or len(code) > 64
            for code in promo_codes
        ):
            raise SalesPolicyError(f"invalid promo code for {plan_id}")

    by_id = {plan["plan_id"]: plan for plan in plans}
    required_ids = {"saas-start", "saas-business", "prepaid-actions", "on-premise"}
    if set(by_id) != required_ids:
        raise SalesPolicyError(f"current profile requires plans {sorted(required_ids)}")

    expected = {
        "saas-start": {
            "public_code": "basic",
            "kind": "BASE_PLAN",
            "entitlement_kind": "DIGITAL_TWIN_WITH_OPERATIONS",
            "display_name": "Basic",
            "active_twins_included": 1,
            "agent_operations_included": 1000,
            "operation_scope": "PER_TWIN_MONTH",
            "operations_source": "INCLUDED",
            "payment_card_required": True,
            "eligible_promo_codes": ["NOCC100"],
        },
        "saas-business": {
            "public_code": "operations-plus",
            "kind": "OPERATIONS_ADDON",
            "entitlement_kind": "AGENT_OPERATIONS",
            "display_name": "Operations Plus",
            "active_twins_included": 0,
            "agent_operations_included": 1000,
            "operation_scope": "ACCOUNT_MONTH",
            "operations_source": "ADD_ON",
            "payment_card_required": True,
            "eligible_promo_codes": [],
        },
        "prepaid-actions": {
            "public_code": "twin-plus",
            "kind": "TWIN_ADDON",
            "entitlement_kind": "DIGITAL_TWIN",
            "display_name": "Twin Plus",
            "active_twins_included": 1,
            "agent_operations_included": 0,
            "operation_scope": "NONE",
            "operations_source": "SEPARATE_PACKAGE",
            "payment_card_required": True,
            "eligible_promo_codes": [],
        },
        "on-premise": {
            "public_code": "on-premise",
            "kind": "OFFLINE_OFFER",
            "entitlement_kind": "CONTRACT",
            "display_name": "On-premise",
            "active_twins_included": None,
            "agent_operations_included": None,
            "operation_scope": "CONTRACT",
            "operations_source": "CONTRACT",
            "payment_card_required": None,
            "eligible_promo_codes": [],
        },
    }
    for plan_id, fields in expected.items():
        for key, expected_value in fields.items():
            if by_id[plan_id][key] != expected_value:
                raise SalesPolicyError(
                    f"current catalog drift for {plan_id}.{key}: "
                    f"expected={expected_value!r}, actual={by_id[plan_id][key]!r}"
                )

    if "Actions Plus" not in by_id["saas-business"]["legacy_display_names"]:
        raise SalesPolicyError("Actions Plus must remain an explicit read-only migration alias")
    if "On-Premise" not in by_id["on-premise"]["legacy_display_names"]:
        raise SalesPolicyError("On-Premise must remain an explicit read-only migration alias")
    twin = by_id["prepaid-actions"]
    if "Brak" in twin["operation_label_pl"] or "Operations Plus" not in twin["operation_label_pl"]:
        raise SalesPolicyError("Twin Plus must explain its separate Operations Plus package")
    if "0 operacji" not in twin["seat_summary_pl"]:
        raise SalesPolicyError("Twin Plus summary must expose the exact zero-operation entitlement")
    if by_id["saas-business"]["promo_hint_pl"] is not None:
        raise SalesPolicyError("Operations Plus must not advertise NOCC100")
    return catalog


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _same_scalar_type(left: Any, right: Any) -> bool:
    return type(left) is type(right)


def _symbol_name(node: Mapping[str, Any]) -> str | None:
    if node.get("node") != "symbol":
        return None
    name = node.get("name")
    if not isinstance(name, str):
        return None
    return name[1:-1] if name.startswith("{") and name.endswith("}") else name


def evaluate_expression(node: Mapping[str, Any], scope: Mapping[str, Any]) -> Any:
    """Evaluate the closed Policy IR expression subset without coercion."""

    kind = node.get("node")
    if kind == "literal":
        return node.get("value")
    if kind == "symbol":
        name = _symbol_name(node)
        if name is None or name not in scope:
            raise SalesPolicyError(f"unresolved symbol: {name!r}")
        return scope[name]
    if kind == "list":
        return [evaluate_expression(item, scope) for item in node["items"]]
    if kind == "sequence":
        return [evaluate_expression(item, scope) for item in node["items"]]
    if kind == "unary":
        operand = evaluate_expression(node["operand"], scope)
        operator = node.get("operator")
        if operator == "NOT":
            if not isinstance(operand, bool):
                raise SalesPolicyError("NOT requires BOOLEAN")
            return not operand
        if operator == "-":
            if not _is_number(operand):
                raise SalesPolicyError("unary - requires NUMBER")
            result = -operand
            if not _is_number(result):
                raise SalesPolicyError("numeric result is not finite")
            return result
        raise SalesPolicyError(f"unknown unary operator: {operator!r}")
    if kind != "binary":
        raise SalesPolicyError(f"unsupported expression node: {kind!r}")

    operator = node.get("operator")
    if operator == "AND":
        left = evaluate_expression(node["left"], scope)
        if not isinstance(left, bool):
            raise SalesPolicyError("AND requires BOOLEAN operands")
        if not left:
            return False
        right = evaluate_expression(node["right"], scope)
        if not isinstance(right, bool):
            raise SalesPolicyError("AND requires BOOLEAN operands")
        return right
    if operator == "OR":
        left = evaluate_expression(node["left"], scope)
        if not isinstance(left, bool):
            raise SalesPolicyError("OR requires BOOLEAN operands")
        if left:
            return True
        right = evaluate_expression(node["right"], scope)
        if not isinstance(right, bool):
            raise SalesPolicyError("OR requires BOOLEAN operands")
        return right

    left = evaluate_expression(node["left"], scope)
    right = evaluate_expression(node["right"], scope)
    if operator == "=":
        return _same_scalar_type(left, right) and left == right
    if operator == "!=":
        return not (_same_scalar_type(left, right) and left == right)
    if operator == "IN":
        if not isinstance(right, list):
            raise SalesPolicyError("IN requires a LIST on the right")
        return any(_same_scalar_type(left, item) and left == item for item in right)
    if operator in {"<", "<=", ">", ">="}:
        if (
            not _same_scalar_type(left, right)
            or isinstance(left, bool)
            or not isinstance(left, (str, int, float))
            or (isinstance(left, (int, float)) and (not _is_number(left) or not _is_number(right)))
        ):
            raise SalesPolicyError(f"{operator} requires comparable values of one scalar type")
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        return left >= right
    if operator in {"+", "-", "*", "/", "%"}:
        if not _same_scalar_type(left, right) or not _is_number(left) or not _is_number(right):
            raise SalesPolicyError(f"{operator} requires numeric operands of one scalar type")
        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        else:
            if right == 0:
                raise SalesPolicyError("division by zero")
            result = left / right if operator == "/" else left % right
        if not _is_number(result):
            raise SalesPolicyError("numeric result is not finite")
        return result
    raise SalesPolicyError(f"unknown binary operator: {operator!r}")


def _normalize_promo_code(value: str | None) -> tuple[str, str | None, str]:
    if value is None:
        return "", None, ""
    if not isinstance(value, str):
        raise SalesPolicyError("promo_code must be a string or null")
    if len(value) > 128:
        raise SalesPolicyError("promo_code exceeds 128 characters")
    normalized = value.strip().upper()
    if not normalized:
        return "", None, value
    if not re.fullmatch(r"[A-Z0-9_-]{1,64}", normalized):
        return "__INVALID__", "INVALID_PROMO_FORMAT", value
    return normalized, None, value


def _resolve_plan(catalog: Mapping[str, Any], identifier: str) -> Mapping[str, Any]:
    if not isinstance(identifier, str) or not identifier:
        raise SalesPolicyError("plan_id must be a non-empty string")
    for plan in catalog["plans"]:
        if identifier in {plan["plan_id"], plan["public_code"]}:
            return plan
    raise SalesPolicyError(f"unknown plan_id: {identifier}")


def _resolve_bindings(ir: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    scope = dict(context)
    for binding in ir["bindings"]:
        name = binding["name"]
        if binding["operator"] != "=":
            raise SalesPolicyError(
                f"sales profile does not support binding operator {binding['operator']!r}"
            )
        if name in context:
            raise SalesPolicyError(f"context cannot override policy binding {name}")
        scope[name] = evaluate_expression(binding["value"], scope)
    return scope


def _descriptor(payload: Mapping[str, Any] | None, scope: Mapping[str, Any]) -> Any:
    if payload is None:
        return None
    name = _symbol_name(payload)
    if name is not None and name not in scope:
        return name
    value = evaluate_expression(payload, scope)
    if isinstance(value, (dict, list)):
        raise SalesPolicyError("descriptor must be scalar")
    return value


def _record_payload(payload: Mapping[str, Any] | None, scope: Mapping[str, Any]) -> tuple[str, Any]:
    if payload is None or payload.get("node") != "sequence":
        raise SalesPolicyError("RECORD requires: RECORD <UPPERCASE_KEY> <VALUE>")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise SalesPolicyError("RECORD requires exactly two payload items")
    key = _symbol_name(items[0])
    if key is None or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
        raise SalesPolicyError("RECORD key must be an uppercase symbol")
    value = evaluate_expression(items[1], scope)
    if isinstance(value, (dict, list)) or value is None:
        raise SalesPolicyError("RECORD value must be a non-null scalar")
    if isinstance(value, float) and not math.isfinite(value):
        raise SalesPolicyError("RECORD numeric value must be finite")
    return key, value


def _closed_descriptor(value: Any, allowed: set[str], opcode: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise SalesPolicyError(f"unsupported {opcode} descriptor: {value!r}")
    return value


def _evaluate_policy(ir: Mapping[str, Any], scope: Mapping[str, Any]) -> dict[str, Any]:
    records: dict[str, Any] = {"METERING_UNIT": scope["METERING_UNIT"]}
    allowed: list[str] = []
    required: list[str] = []
    reports: list[str] = []
    forbidden: list[dict[str, Any]] = []
    matched_rules: list[str] = []

    for rule in ir["rules"]:
        decision_scope = {**scope, **records}
        condition = evaluate_expression(rule["condition"], decision_scope)
        if not isinstance(condition, bool):
            raise SalesPolicyError(f"rule {rule['id']} condition did not return BOOLEAN")
        if not condition:
            continue
        matched_rules.append(rule["id"])

        for action in rule["actions"]:
            decision_scope = {**scope, **records}
            if action["guard"] is not None:
                guard = evaluate_expression(action["guard"], decision_scope)
                if not isinstance(guard, bool):
                    raise SalesPolicyError(f"action guard in {rule['id']} did not return BOOLEAN")
                if not guard:
                    continue
            opcode = action["opcode"]
            if opcode == "RECORD":
                key, value = _record_payload(action["payload"], decision_scope)
                if key in records and records[key] != value:
                    raise SalesPolicyError(f"conflicting RECORD values for {key}")
                records[key] = value
            elif opcode == "ALLOW":
                value = _closed_descriptor(_descriptor(action["payload"], decision_scope), ALLOW_VALUES, opcode)
                if value not in allowed:
                    allowed.append(value)
            elif opcode == "REQUIRE":
                value = _closed_descriptor(
                    _descriptor(action["payload"], decision_scope), REQUIRE_VALUES, opcode
                )
                if value not in required:
                    required.append(value)
            elif opcode == "REPORT":
                value = _closed_descriptor(_descriptor(action["payload"], decision_scope), REPORT_VALUES, opcode)
                if value not in reports:
                    reports.append(value)
            else:
                raise SalesPolicyError(f"unsupported sales profile opcode: {opcode}")

        for action in rule["forbidden"]:
            decision_scope = {**scope, **records}
            if action["guard"] is not None:
                guard = evaluate_expression(action["guard"], decision_scope)
                if not isinstance(guard, bool):
                    raise SalesPolicyError(f"forbidden guard in {rule['id']} did not return BOOLEAN")
                if not guard:
                    continue
            if action["opcode"] not in FORBIDDEN_OPCODES:
                raise SalesPolicyError(f"unsupported forbidden sales opcode: {action['opcode']}")
            payload = _descriptor(action["payload"], decision_scope)
            if not isinstance(payload, str):
                raise SalesPolicyError("forbidden sales descriptor must be a string")
            item = {"opcode": action["opcode"], "payload": payload}
            if item not in forbidden:
                forbidden.append(item)

        for assertion in rule["assertions"]:
            if evaluate_expression(assertion, {**scope, **records}) is not True:
                raise SalesPolicyError(f"assertion failed in rule {rule['id']}")

    for assertion in ir["assertions"]:
        if evaluate_expression(assertion, {**scope, **records}) is not True:
            raise SalesPolicyError("top-level assertion failed")

    return {
        "records": records,
        "matched_rules": matched_rules,
        "allowed": allowed,
        "required": required,
        "reports": reports,
        "forbidden": forbidden,
    }


def _verify_policy_records(records: Mapping[str, Any]) -> None:
    if records.get("METERING_UNIT") != METERING_UNIT:
        raise SalesPolicyError("sales policy metering unit is incompatible")
    for key in (
        "PROMOTION_ELIGIBILITY",
        "EFFECTIVE_PROMO",
        "PROMOTION_PRESENTATION",
        "PROMOTION_REASON",
    ):
        if key not in records:
            raise SalesPolicyError(f"sales policy did not record {key}")


def decide(plan_id: str, promo_code: str | None = "") -> dict[str, Any]:
    """Evaluate one inert sales decision for a legacy or public plan code."""

    catalog = load_catalog()
    plan = _resolve_plan(catalog, plan_id)
    normalized, normalization_error, raw_code = _normalize_promo_code(promo_code)

    try:
        ir = CHECK.parse(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, CHECK.PolicyError) as error:
        raise SalesPolicyError(f"sales policy is invalid: {error}") from error
    if ir["document"]["name"] != POLICY_DOCUMENT or ir["document"]["version"] != POLICY_VERSION:
        raise SalesPolicyError("sales policy document identity is incompatible")

    scope = _resolve_bindings(
        ir,
        {
            "SELECTED_PLAN": plan["plan_id"],
            "REQUESTED_PROMO": normalized,
        },
    )
    result = _evaluate_policy(ir, scope)
    records = result["records"]
    _verify_policy_records(records)

    decision: dict[str, Any] = {
        "schema": "subactor.sales/decision/v1",
        "input": {"plan_id": plan_id, "promo_code": raw_code},
        "offer": {
            "plan_id": plan["plan_id"],
            "public_code": plan["public_code"],
            "kind": plan["kind"],
            "entitlement_kind": plan["entitlement_kind"],
            "display_name": plan["display_name"],
            "active_twins_included": plan["active_twins_included"],
        },
        "promotion": {
            "normalized_code": records["EFFECTIVE_PROMO"],
            "eligibility": records["PROMOTION_ELIGIBILITY"],
            "presentation": records["PROMOTION_PRESENTATION"],
            "reason": records["PROMOTION_REASON"],
        },
        "payment": {
            "card_required": records.get("CARD_REQUIRED", plan["payment_card_required"]),
        },
        "metering": {
            "unit": records["METERING_UNIT"],
            "included": plan["agent_operations_included"],
            "scope": plan["operation_scope"],
            "source": plan["operations_source"],
            "label_pl": plan["operation_label_pl"],
        },
        "policy": {
            "document": ir["document"]["name"],
            "version": ir["document"]["version"],
            "matched_rules": result["matched_rules"],
            "allowed": result["allowed"],
            "required": result["required"],
            "reports": result["reports"],
            "forbidden": result["forbidden"],
        },
    }

    if normalization_error is not None:
        decision["promotion"].update(
            {
                "normalized_code": "",
                "eligibility": "UNKNOWN",
                "presentation": "HIDDEN",
                "reason": normalization_error,
            }
        )
    validate_decision(decision, catalog)
    return decision


def _validate_string_list(value: Any, allowed: set[str], label: str) -> None:
    if (
        not isinstance(value, list)
        or len(value) != len(set(value))
        or any(not isinstance(item, str) or item not in allowed for item in value)
    ):
        raise SalesPolicyError(f"invalid {label}")


def validate_decision(decision: Mapping[str, Any], catalog: Mapping[str, Any] | None = None) -> None:
    """Validate a decision structurally and against current sales invariants."""

    catalog = catalog or load_catalog()
    _exact_keys(
        decision,
        {"schema", "input", "offer", "promotion", "payment", "metering", "policy"},
        "sales decision",
    )
    if decision["schema"] != "subactor.sales/decision/v1":
        raise SalesPolicyError("incompatible sales decision schema")
    _exact_keys(decision["input"], {"plan_id", "promo_code"}, "decision input")
    _exact_keys(
        decision["offer"],
        {"plan_id", "public_code", "kind", "entitlement_kind", "display_name", "active_twins_included"},
        "decision offer",
    )
    _exact_keys(
        decision["promotion"],
        {"normalized_code", "eligibility", "presentation", "reason"},
        "decision promotion",
    )
    _exact_keys(decision["payment"], {"card_required"}, "decision payment")
    _exact_keys(
        decision["metering"],
        {"unit", "included", "scope", "source", "label_pl"},
        "decision metering",
    )
    _exact_keys(
        decision["policy"],
        {"document", "version", "matched_rules", "allowed", "required", "reports", "forbidden"},
        "decision policy",
    )

    if decision["policy"]["document"] != POLICY_DOCUMENT or decision["policy"]["version"] != POLICY_VERSION:
        raise SalesPolicyError("decision is not bound to SUBACTOR_SALES version 1")
    if decision["metering"]["unit"] != METERING_UNIT:
        raise SalesPolicyError("decision uses an incompatible metering unit")

    input_plan = decision["input"]["plan_id"]
    if not isinstance(input_plan, str) or not input_plan:
        raise SalesPolicyError("decision input plan_id must be a non-empty string")
    input_promo = decision["input"]["promo_code"]
    if not isinstance(input_promo, str) or len(input_promo) > 128:
        raise SalesPolicyError("decision input promo_code must be a string up to 128 characters")

    plan = _resolve_plan(catalog, input_plan)
    offer = decision["offer"]
    expected_offer = {
        "plan_id": plan["plan_id"],
        "public_code": plan["public_code"],
        "kind": plan["kind"],
        "entitlement_kind": plan["entitlement_kind"],
        "display_name": plan["display_name"],
        "active_twins_included": plan["active_twins_included"],
    }
    if dict(offer) != expected_offer:
        raise SalesPolicyError("decision offer does not match the current catalog")

    expected_metering = {
        "unit": METERING_UNIT,
        "included": plan["agent_operations_included"],
        "scope": plan["operation_scope"],
        "source": plan["operations_source"],
        "label_pl": plan["operation_label_pl"],
    }
    if dict(decision["metering"]) != expected_metering:
        raise SalesPolicyError("decision metering does not match the current catalog")

    policy = decision["policy"]
    matched_rules = policy["matched_rules"]
    if (
        not isinstance(matched_rules, list)
        or len(matched_rules) != len(set(matched_rules))
        or any(not isinstance(item, str) or not re.fullmatch(r"[A-Z][A-Z0-9_-]*", item) for item in matched_rules)
    ):
        raise SalesPolicyError("invalid matched_rules")
    _validate_string_list(policy["allowed"], ALLOW_VALUES, "allowed policy descriptors")
    _validate_string_list(policy["required"], REQUIRE_VALUES, "required policy descriptors")
    _validate_string_list(policy["reports"], REPORT_VALUES, "policy reports")

    forbidden = policy["forbidden"]
    if not isinstance(forbidden, list):
        raise SalesPolicyError("policy forbidden must be an array")
    normalized_forbidden: list[tuple[str, str]] = []
    for index, item in enumerate(forbidden):
        _exact_keys(item, {"opcode", "payload"}, f"policy forbidden[{index}]")
        if item["opcode"] not in FORBIDDEN_OPCODES or not isinstance(item["payload"], str):
            raise SalesPolicyError("invalid forbidden policy directive")
        pair = (item["opcode"], item["payload"])
        if pair in normalized_forbidden:
            raise SalesPolicyError("duplicate forbidden policy directive")
        normalized_forbidden.append(pair)

    normalized_input, normalization_error, _ = _normalize_promo_code(input_promo)
    if normalized_input == "":
        expected_promotion = {
            "normalized_code": "",
            "eligibility": "NONE",
            "presentation": "HIDDEN",
            "reason": "NO_PROMO",
        }
        promo_rule = "SALES-PROMO-NONE"
        expected_allowed: set[str] = set()
        expected_required: set[str] = set()
        promo_forbidden: set[str] = set()
    elif normalized_input == "NOCC100" and plan["plan_id"] == "saas-start":
        expected_promotion = {
            "normalized_code": "NOCC100",
            "eligibility": "ELIGIBLE",
            "presentation": "VISIBLE",
            "reason": "ELIGIBLE_BASIC",
        }
        promo_rule = "SALES-PROMO-NOCC100-BASIC"
        expected_allowed = {"APPLY_PROMOTION"}
        expected_required = set()
        promo_forbidden = set()
    elif normalized_input == "NOCC100":
        expected_promotion = {
            "normalized_code": "",
            "eligibility": "INELIGIBLE",
            "presentation": "HIDDEN",
            "reason": "PLAN_NOT_ELIGIBLE",
        }
        promo_rule = "SALES-PROMO-NOCC100-NON-BASIC"
        expected_allowed = set()
        expected_required = {"PROMOTION_SANITIZED"}
        promo_forbidden = {"APPLY_PROMOTION", "DISPLAY_PROMOTION"}
    else:
        expected_promotion = {
            "normalized_code": "",
            "eligibility": "UNKNOWN",
            "presentation": "HIDDEN",
            "reason": normalization_error or "UNKNOWN_PROMO_CODE",
        }
        promo_rule = "SALES-PROMO-UNKNOWN"
        expected_allowed = set()
        expected_required = {"PROMOTION_SANITIZED"}
        promo_forbidden = {"APPLY_PROMOTION", "DISPLAY_PROMOTION"}

    if dict(decision["promotion"]) != expected_promotion:
        raise SalesPolicyError("promotion decision does not match the request and plan")
    if set(policy["allowed"]) != expected_allowed:
        raise SalesPolicyError("allowed policy descriptors do not match promotion eligibility")
    if set(policy["required"]) != expected_required:
        raise SalesPolicyError("required policy descriptors do not match promotion eligibility")

    expected_card = False if expected_promotion["eligibility"] == "ELIGIBLE" else plan["payment_card_required"]
    if decision["payment"]["card_required"] is not expected_card:
        raise SalesPolicyError("card requirement does not match the promotion decision")

    expected_rules = {promo_rule}
    if plan["plan_id"] == "prepaid-actions":
        expected_rules.add("SALES-TWIN-PLUS-PRESENTATION")
    if set(matched_rules) != expected_rules:
        raise SalesPolicyError("matched rules do not match promotion and plan-presentation concerns")

    forbidden_opcodes = {item["opcode"] for item in forbidden}
    if not promo_forbidden.issubset(forbidden_opcodes):
        raise SalesPolicyError("promotion sanitization directives are incomplete")
    if not promo_forbidden and forbidden_opcodes & {"APPLY_PROMOTION", "DISPLAY_PROMOTION"}:
        raise SalesPolicyError("eligible or empty promotion must not be forbidden")

    if plan["plan_id"] == "prepaid-actions":
        if "DISPLAY_OPERATION_LABEL" not in forbidden_opcodes:
            raise SalesPolicyError("Twin Plus must forbid the ambiguous 'Brak' label")
        if policy["reports"] != ["OPERATIONS_PURCHASED_SEPARATELY"]:
            raise SalesPolicyError("Twin Plus must report its separate operation package")
        if "Brak" in decision["metering"]["label_pl"] or "Operations Plus" not in decision["metering"]["label_pl"]:
            raise SalesPolicyError("Twin Plus label must explain the separate operation package")
    else:
        if "DISPLAY_OPERATION_LABEL" in forbidden_opcodes:
            raise SalesPolicyError("non-Twin plans must not carry the Twin label guard")
        if policy["reports"]:
            raise SalesPolicyError("only Twin Plus may emit the separate-package report")


def load_offer_home_lock() -> dict[str, Any]:
    try:
        lock = json.loads(OFFER_HOME_LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"offer-home lock is unreadable: {error}") from error
    if lock.get("schema") != "wellmanifest.policy/offer-home-lock/v1":
        raise SalesPolicyError("offer-home lock schema mismatch")
    home = lock.get("home")
    if not isinstance(home, dict):
        raise SalesPolicyError("offer-home lock missing home object")
    for key in ("repository", "catalog_path", "offer_id", "version", "digest"):
        if key not in home:
            raise SalesPolicyError(f"offer-home lock missing home.{key}")
    if not isinstance(home["digest"], str) or not home["digest"].startswith("sha256:"):
        raise SalesPolicyError("offer-home lock digest must be sha256:<hex>")
    fields = lock.get("mirrored_fields")
    if not isinstance(fields, list) or not fields or any(not isinstance(item, str) for item in fields):
        raise SalesPolicyError("offer-home lock mirrored_fields must be a non-empty string list")
    fixture = lock.get("fixture_path")
    if not isinstance(fixture, str) or not fixture:
        raise SalesPolicyError("offer-home lock fixture_path must be a relative path string")
    return lock


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _home_operations(plan: Mapping[str, Any]) -> Any:
    if "agent_operations_included" in plan:
        return plan["agent_operations_included"]
    return plan.get("actions_included")


def compare_offer_home(home_catalog_path: Path | None = None) -> dict[str, Any]:
    """Fail closed when the sales ADOPT projection drifts from pinned ``subactor/offer`` HOME.

    The lock digests the HOME catalog bytes. Commercial amount/entitlement fields on
    ``offer-catalog.json`` must match that HOME document plan-by-plan. This pack must
    not become a second price SSOT.
    """

    lock = load_offer_home_lock()
    home_meta = lock["home"]
    path = home_catalog_path
    if path is None:
        path = ROOT / lock["fixture_path"]
    if not path.is_file():
        raise SalesPolicyError(f"HOME offer catalog missing: {path}")

    actual_digest = _file_digest(path)
    expected_digest = home_meta["digest"]
    if actual_digest != expected_digest:
        raise SalesPolicyError(
            f"HOME offer digest drift: expected {expected_digest}, actual {actual_digest}"
        )

    try:
        home_doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"HOME offer catalog is unreadable: {error}") from error

    if home_doc.get("schema") != "subactor.offer/catalog/v1":
        raise SalesPolicyError("HOME offer catalog schema mismatch")
    if home_doc.get("id") != home_meta["offer_id"]:
        raise SalesPolicyError(
            f"HOME offer id expected {home_meta['offer_id']!r}, got {home_doc.get('id')!r}"
        )
    if home_doc.get("version") != home_meta["version"]:
        raise SalesPolicyError(
            f"HOME offer version expected {home_meta['version']!r}, got {home_doc.get('version')!r}"
        )

    sales = load_catalog()
    home_plans = home_doc.get("plans")
    if not isinstance(home_plans, list):
        raise SalesPolicyError("HOME offer catalog plans must be an array")
    home_by_id = {}
    for index, plan in enumerate(home_plans):
        if not isinstance(plan, dict):
            raise SalesPolicyError(f"HOME plans[{index}] must be an object")
        plan_id = plan.get("plan_id")
        if not isinstance(plan_id, str) or not plan_id:
            raise SalesPolicyError(f"HOME plans[{index}] lacks plan_id")
        if plan_id in home_by_id:
            raise SalesPolicyError(f"duplicate HOME plan_id {plan_id}")
        home_by_id[plan_id] = plan

    checked: list[str] = []
    for plan in sales["plans"]:
        plan_id = plan["plan_id"]
        if plan_id not in home_by_id:
            raise SalesPolicyError(f"sales catalog plan {plan_id} absent from HOME offer")
        home_plan = home_by_id[plan_id]
        for field in lock["mirrored_fields"]:
            if field == "agent_operations_included":
                expected = _home_operations(home_plan)
                actual = plan.get("agent_operations_included")
            else:
                expected = home_plan.get(field)
                actual = plan.get(field)
            if actual != expected:
                raise SalesPolicyError(
                    f"{plan_id}.{field}: HOME={expected!r} sales={actual!r}"
                )
        checked.append(plan_id)

    return {
        "ok": True,
        "offer_id": home_meta["offer_id"],
        "version": home_meta["version"],
        "digest": expected_digest,
        "checked_plan_ids": checked,
        "home_path": str(path),
    }


def compare_www_plans(plans_path: Path) -> None:
    """Fail closed when a portal plans.json facade drifts from the sales catalog.

    List prices HOME in ``subactor/offer``; this catalog mirrors amounts for
    entitlement/promo parity checks. The portal facade must match mirrored
    entitlements, names (including legacy aliases) and amount mirrors.
    """

    catalog = load_catalog()
    try:
        payload = json.loads(plans_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"www plans are unreadable: {error}") from error

    if not isinstance(payload, dict) or "plans" not in payload:
        raise SalesPolicyError("www plans must be an object with a plans field")

    raw_plans = payload["plans"]
    if isinstance(raw_plans, dict):
        by_id = raw_plans
    elif isinstance(raw_plans, list):
        by_id = {}
        for index, item in enumerate(raw_plans):
            if not isinstance(item, dict):
                raise SalesPolicyError(f"www plans[{index}] must be an object")
            plan_id = item.get("id") or item.get("plan_id")
            if not isinstance(plan_id, str) or not plan_id:
                raise SalesPolicyError(f"www plans[{index}] lacks id")
            if plan_id in by_id:
                raise SalesPolicyError(f"duplicate www plan id {plan_id}")
            by_id[plan_id] = item
    else:
        raise SalesPolicyError("www plans must be an object map or array")

    for plan in catalog["plans"]:
        plan_id = plan["plan_id"]
        if plan_id not in by_id:
            raise SalesPolicyError(f"www plans missing catalog plan {plan_id}")
        facade = by_id[plan_id]
        if not isinstance(facade, dict):
            raise SalesPolicyError(f"www plan {plan_id} must be an object")

        actions = facade.get("actions_included", facade.get("agent_operations_included"))
        if actions != plan["agent_operations_included"]:
            raise SalesPolicyError(
                f"{plan_id} actions_included expected {plan['agent_operations_included']!r}, "
                f"got {actions!r}"
            )

        twins = facade.get("active_twins_included")
        if twins != plan["active_twins_included"]:
            raise SalesPolicyError(
                f"{plan_id} active_twins_included expected {plan['active_twins_included']!r}, "
                f"got {twins!r}"
            )

        allowed_names = {plan["display_name"], *plan["legacy_display_names"]}
        name = facade.get("name") or facade.get("display_name")
        if name not in allowed_names:
            raise SalesPolicyError(
                f"{plan_id} name {name!r} not in {sorted(allowed_names)}"
            )

        if facade.get("amount_monthly_minor") != plan["amount_monthly_minor"]:
            raise SalesPolicyError(
                f"{plan_id} amount_monthly_minor expected {plan['amount_monthly_minor']!r}, "
                f"got {facade.get('amount_monthly_minor')!r}"
            )
        if facade.get("amount_annual_minor") != plan["amount_annual_minor"]:
            raise SalesPolicyError(
                f"{plan_id} amount_annual_minor expected {plan['amount_annual_minor']!r}, "
                f"got {facade.get('amount_annual_minor')!r}"
            )
        if facade.get("currency") != plan["currency"]:
            raise SalesPolicyError(
                f"{plan_id} currency expected {plan['currency']!r}, "
                f"got {facade.get('currency')!r}"
            )


def matrix() -> dict[str, Any]:
    cases = [
        ("NOCC100_BASIC", "saas-start", "NOCC100"),
        ("NOCC100_OPERATIONS_PLUS", "saas-business", "NOCC100"),
        ("NOCC100_TWIN_PLUS", "prepaid-actions", "NOCC100"),
        ("NOCC100_ON_PREMISE", "on-premise", "NOCC100"),
        ("NO_PROMO_BASIC", "saas-start", ""),
        ("UNKNOWN_PROMO_BASIC", "saas-start", "OTHER100"),
        ("INVALID_PROMO_BASIC", "saas-start", "NOCC 100"),
    ]
    return {
        "schema": "subactor.sales/decision-matrix/v1",
        "cases": [
            {"name": name, "decision": decide(current_plan, current_promo)}
            for name, current_plan, current_promo in cases
        ],
    }


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    decide_parser = subparsers.add_parser("decide", help="evaluate one sales decision")
    decide_parser.add_argument("--plan-id", required=True)
    decide_parser.add_argument("--promo-code", default="")

    matrix_parser = subparsers.add_parser("matrix", help="emit or verify the current decision matrix")
    matrix_parser.add_argument("--check", type=Path)

    subparsers.add_parser("validate-catalog", help="validate the closed current catalog")

    compare_parser = subparsers.add_parser(
        "compare-www-plans",
        help="fail closed when a portal plans.json facade drifts from the sales catalog",
    )
    compare_parser.add_argument("--plans", type=Path, required=True)

    home_parser = subparsers.add_parser(
        "compare-offer-home",
        help="fail closed when sales amounts drift from the pinned subactor/offer HOME catalog",
    )
    home_parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="path to subactor/offer catalogs/.../offer.json (defaults to locked fixture)",
    )

    export_parser = subparsers.add_parser(
        "export-decisions",
        help="write or verify the frozen consumer decision/v1 matrix fixture",
    )
    export_parser.add_argument("--out", type=Path, help="write matrix() JSON to this path")
    export_parser.add_argument(
        "--check",
        type=Path,
        help="fail closed when the fixture differs from matrix()",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.command == "decide":
            print(_json(decide(args.plan_id, args.promo_code)), end="")
        elif args.command == "validate-catalog":
            load_catalog()
            compare_offer_home()
            print("SALES-CATALOG-PASS")
        elif args.command == "compare-www-plans":
            compare_www_plans(args.plans)
            print("SALES-WWW-PLANS-PASS")
        elif args.command == "compare-offer-home":
            result = compare_offer_home(args.catalog)
            print(_json(result), end="")
        elif args.command == "export-decisions":
            actual = matrix()
            if args.check is not None:
                expected = json.loads(args.check.read_text(encoding="utf-8"))
                if expected != actual:
                    raise SalesPolicyError(f"decision fixture differs from {args.check}")
                print("SALES-DECISIONS-PASS")
            elif args.out is not None:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(_json(actual), encoding="utf-8")
                print(f"SALES-DECISIONS-WROTE {args.out}")
            else:
                print(_json(actual), end="")
        else:
            actual = matrix()
            if args.check is not None:
                expected = json.loads(args.check.read_text(encoding="utf-8"))
                if expected != actual:
                    raise SalesPolicyError(f"decision matrix differs from {args.check}")
                print("SALES-MATRIX-PASS")
            else:
                print(_json(actual), end="")
    except (OSError, json.JSONDecodeError, SalesPolicyError) as error:
        print(f"SALES-POLICY-001: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
