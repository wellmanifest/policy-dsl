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
POLICY_VERSION = 2
METERING_UNIT = "AGENT_OPERATION"
CATALOG_SCHEMA = "subactor.sales/catalog/v2"
DECISION_SCHEMA = "subactor.sales/decision/v2"
DECISION_MATRIX_SCHEMA = "subactor.sales/decision-matrix/v2"
OFFER_HOME_LOCK_SCHEMA = "wellmanifest.policy/offer-home-lock/v2"

ALLOW_VALUES = {"APPLY_PROMOTION"}
REQUIRE_VALUES = {"PROMOTION_SANITIZED"}
REPORT_VALUES: set[str] = set()
FORBIDDEN_OPCODES = {
    "APPLY_PROMOTION",
    "DISPLAY_PROMOTION",
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
    """Load and validate the closed sales catalog.

    The catalog holds only what this pack owns: plan identifiers, public codes,
    card requirements and promotion eligibility. Names, amounts, currencies,
    operation entitlements and copy are read from the locked HOME offer.
    """

    catalog_path = CATALOG_PATH if path is None else path
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"catalog is unreadable: {error}") from error

    _exact_keys(catalog, {"schema", "plans"}, "catalog")
    if catalog["schema"] != CATALOG_SCHEMA:
        raise SalesPolicyError("incompatible sales catalog schema")

    plans = catalog["plans"]
    if not isinstance(plans, list) or not plans:
        raise SalesPolicyError("catalog plans must be a non-empty array")

    plan_keys = {"plan_id", "public_code", "legacy_public_codes", "payment_card_required", "eligible_promo_codes"}
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    code_pattern = r"[a-z][a-z0-9-]*"
    for index, plan in enumerate(plans):
        _exact_keys(plan, plan_keys, f"plan[{index}]")
        plan_id = plan["plan_id"]
        if not isinstance(plan_id, str) or not re.fullmatch(code_pattern, plan_id):
            raise SalesPolicyError(f"invalid plan_id at plan[{index}]")
        codes = [plan["public_code"], *plan["legacy_public_codes"]] if isinstance(plan["legacy_public_codes"], list) else None
        if codes is None or any(not isinstance(code, str) or not re.fullmatch(code_pattern, code) for code in codes):
            raise SalesPolicyError(f"invalid public or legacy code for {plan_id}")
        identifiers = {plan_id, *codes}
        if plan_id in seen_ids or identifiers & seen_codes or len(codes) != len(set(codes)):
            raise SalesPolicyError("duplicate plan_id, public_code or legacy public code")
        seen_ids.add(plan_id)
        seen_codes.update(identifiers)

        card_required = plan["payment_card_required"]
        if card_required is not None and not isinstance(card_required, bool):
            raise SalesPolicyError(f"invalid payment_card_required for {plan_id}")
        promo_codes = plan["eligible_promo_codes"]
        if (
            not isinstance(promo_codes, list)
            or len(promo_codes) != len(set(promo_codes))
            or any(not isinstance(code, str) or not re.fullmatch(r"[A-Z0-9_-]{1,64}", code) for code in promo_codes)
        ):
            raise SalesPolicyError(f"invalid eligible_promo_codes for {plan_id}")

    by_id = {plan["plan_id"]: plan for plan in plans}
    expected = {
        "saas-start": ("basic", [], True, ["NOCC100"]),
        "saas-business": ("pro", ["operations-plus"], True, []),
        "prepaid-actions": ("max", ["twin-plus"], True, []),
        "on-premise": ("on-premise", [], None, []),
    }
    if set(by_id) != set(expected):
        raise SalesPolicyError(f"current profile requires plans {sorted(expected)}")
    for plan_id, (public_code, legacy_codes, card_required, promo_codes) in expected.items():
        plan = by_id[plan_id]
        actual = (plan["public_code"], plan["legacy_public_codes"], plan["payment_card_required"], plan["eligible_promo_codes"])
        if actual != (public_code, legacy_codes, card_required, promo_codes):
            raise SalesPolicyError(f"current catalog drift for {plan_id}: expected={(public_code, legacy_codes, card_required, promo_codes)!r}, actual={actual!r}")
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
        if identifier in {plan["plan_id"], plan["public_code"], *plan["legacy_public_codes"]}:
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
    """Evaluate one inert sales decision for a plan id, public code or legacy code."""

    catalog = load_catalog()
    home = load_home_offer()
    plan = _resolve_plan(catalog, plan_id)
    home_plan = home["plans"][plan["plan_id"]]
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
        "schema": DECISION_SCHEMA,
        "input": {"plan_id": plan_id, "promo_code": raw_code},
        "offer": {
            "plan_id": plan["plan_id"],
            "public_code": plan["public_code"],
            "display_name": home_plan["canonical_display_name"],
            "commercial_type": home_plan["commercial_type"],
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
            "included": home_plan["agent_operations_included"],
            "period": home_plan["unit"],
        },
        "home": {"offer_ref": home["offer_ref"], "digest": home["digest"]},
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
    validate_decision(decision, catalog, home)
    return decision


def _validate_string_list(value: Any, allowed: set[str], label: str) -> None:
    if (
        not isinstance(value, list)
        or len(value) != len(set(value))
        or any(not isinstance(item, str) or item not in allowed for item in value)
    ):
        raise SalesPolicyError(f"invalid {label}")


def validate_decision(
    decision: Mapping[str, Any],
    catalog: Mapping[str, Any] | None = None,
    home: Mapping[str, Any] | None = None,
) -> None:
    """Validate a decision structurally and against current sales invariants."""

    catalog = catalog or load_catalog()
    home = home or load_home_offer()
    _exact_keys(
        decision,
        {"schema", "input", "offer", "promotion", "payment", "metering", "home", "policy"},
        "sales decision",
    )
    if decision["schema"] != DECISION_SCHEMA:
        raise SalesPolicyError("incompatible sales decision schema")
    _exact_keys(decision["input"], {"plan_id", "promo_code"}, "decision input")
    _exact_keys(decision["offer"], {"plan_id", "public_code", "display_name", "commercial_type"}, "decision offer")
    _exact_keys(
        decision["promotion"],
        {"normalized_code", "eligibility", "presentation", "reason"},
        "decision promotion",
    )
    _exact_keys(decision["payment"], {"card_required"}, "decision payment")
    _exact_keys(decision["metering"], {"unit", "included", "period"}, "decision metering")
    _exact_keys(decision["home"], {"offer_ref", "digest"}, "decision home")
    _exact_keys(
        decision["policy"],
        {"document", "version", "matched_rules", "allowed", "required", "reports", "forbidden"},
        "decision policy",
    )

    if decision["policy"]["document"] != POLICY_DOCUMENT or decision["policy"]["version"] != POLICY_VERSION:
        raise SalesPolicyError(f"decision is not bound to {POLICY_DOCUMENT} version {POLICY_VERSION}")
    if decision["metering"]["unit"] != METERING_UNIT:
        raise SalesPolicyError("decision uses an incompatible metering unit")

    input_plan = decision["input"]["plan_id"]
    if not isinstance(input_plan, str) or not input_plan:
        raise SalesPolicyError("decision input plan_id must be a non-empty string")
    input_promo = decision["input"]["promo_code"]
    if not isinstance(input_promo, str) or len(input_promo) > 128:
        raise SalesPolicyError("decision input promo_code must be a string up to 128 characters")

    plan = _resolve_plan(catalog, input_plan)
    home_plan = home["plans"][plan["plan_id"]]
    expected_offer = {
        "plan_id": plan["plan_id"],
        "public_code": plan["public_code"],
        "display_name": home_plan["canonical_display_name"],
        "commercial_type": home_plan["commercial_type"],
    }
    if dict(decision["offer"]) != expected_offer:
        raise SalesPolicyError("decision offer does not match the catalog and HOME offer")
    expected_metering = {
        "unit": METERING_UNIT,
        "included": home_plan["agent_operations_included"],
        "period": home_plan["unit"],
    }
    if dict(decision["metering"]) != expected_metering:
        raise SalesPolicyError("decision metering does not match the HOME offer")
    if dict(decision["home"]) != {"offer_ref": home["offer_ref"], "digest": home["digest"]}:
        raise SalesPolicyError("decision is not bound to the locked HOME offer")

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
    if policy["reports"] != []:
        raise SalesPolicyError("the sales profile emits no reports")

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
    elif normalized_input == "NOCC100" and "NOCC100" in plan["eligible_promo_codes"]:
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

    if set(matched_rules) != {promo_rule}:
        raise SalesPolicyError("matched rules do not match the promotion concern")

    forbidden_opcodes = {item["opcode"] for item in forbidden}
    if forbidden_opcodes != promo_forbidden:
        raise SalesPolicyError("promotion sanitization directives do not match eligibility")


def load_offer_home_lock() -> dict[str, Any]:
    try:
        lock = json.loads(OFFER_HOME_LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"offer-home lock is unreadable: {error}") from error
    _exact_keys(lock, {"schema", "home", "fixture_path"}, "offer-home lock")
    if lock["schema"] != OFFER_HOME_LOCK_SCHEMA:
        raise SalesPolicyError("offer-home lock schema mismatch")
    home = lock["home"]
    _exact_keys(
        home,
        {"repository", "catalog_path", "offer_id", "version", "sourceRevision", "digest"},
        "offer-home lock home",
    )
    if not isinstance(home["digest"], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", home["digest"]):
        raise SalesPolicyError("offer-home lock digest must be sha256:<hex>")
    if not isinstance(home["sourceRevision"], str) or not re.fullmatch(r"[0-9a-f]{40}", home["sourceRevision"]):
        raise SalesPolicyError("offer-home lock sourceRevision must be a full Git SHA")
    fixture = lock["fixture_path"]
    if not isinstance(fixture, str) or not fixture or fixture.startswith("/") or ".." in Path(fixture).parts:
        raise SalesPolicyError("offer-home lock fixture_path must be a relative path string")
    return lock


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_home_offer(home_catalog_path: Path | None = None) -> dict[str, Any]:
    """Load the HOME offer catalog bound by the lock and index its plans.

    The catalog must match the locked digest, identity and version, and it must
    still be ``current`` in HOME. Every sales plan must exist in HOME.
    """

    lock = load_offer_home_lock()
    home_meta = lock["home"]
    path = ROOT / lock["fixture_path"] if home_catalog_path is None else home_catalog_path
    if not path.is_file():
        raise SalesPolicyError(f"HOME offer catalog missing: {path}")
    actual_digest = _file_digest(path)
    if actual_digest != home_meta["digest"]:
        raise SalesPolicyError(f"HOME offer digest drift: expected {home_meta['digest']}, actual {actual_digest}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SalesPolicyError(f"HOME offer catalog is unreadable: {error}") from error
    if document.get("schema") != "subactor.offer/catalog/v1":
        raise SalesPolicyError("HOME offer catalog schema mismatch")
    if document.get("id") != home_meta["offer_id"]:
        raise SalesPolicyError(f"HOME offer id expected {home_meta['offer_id']!r}, got {document.get('id')!r}")
    if document.get("version") != home_meta["version"]:
        raise SalesPolicyError(
            f"HOME offer version expected {home_meta['version']!r}, got {document.get('version')!r}"
        )
    if document.get("status") != "current":
        raise SalesPolicyError(
            f"HOME offer {home_meta['offer_id']} v{home_meta['version']} is {document.get('status')!r}, not 'current'"
        )
    vocabulary = document.get("vocabulary")
    if not isinstance(vocabulary, dict) or vocabulary.get("unit_code") != METERING_UNIT:
        raise SalesPolicyError(f"HOME offer must meter {METERING_UNIT}")

    plans = document.get("plans")
    if not isinstance(plans, list):
        raise SalesPolicyError("HOME offer catalog plans must be an array")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, plan in enumerate(plans):
        if not isinstance(plan, dict) or not isinstance(plan.get("plan_id"), str) or not plan["plan_id"]:
            raise SalesPolicyError(f"HOME plans[{index}] lacks plan_id")
        if plan["plan_id"] in by_id:
            raise SalesPolicyError(f"duplicate HOME plan_id {plan['plan_id']}")
        for field in ("canonical_display_name", "commercial_type", "unit", "currency"):
            _require_string(plan.get(field), f"HOME {plan['plan_id']}.{field}")
        _require_optional_non_negative_integer(
            plan.get("agent_operations_included"), f"HOME {plan['plan_id']}.agent_operations_included"
        )
        by_id[plan["plan_id"]] = plan
    return {
        "offer_ref": f"offer://subactor/offer/{home_meta['offer_id']}/v{home_meta['version']}",
        "offer_id": home_meta["offer_id"],
        "version": home_meta["version"],
        "digest": actual_digest,
        "document": document,
        "plans": by_id,
        "path": path,
    }


def _require_current_home_version(home_root: Path, home_meta: Mapping[str, Any]) -> str:
    """Return the HOME catalog path of the pinned version when it is the current one.

    A ``subactor/offer`` checkout holds every catalog version of an offer under
    ``catalogs/<offer_id>/``. Exactly one of them may be ``current``; the lock
    must pin that version, otherwise the projection adopts a superseded offer.
    """

    offer_id = home_meta["offer_id"]
    catalogs = home_root / "catalogs" / offer_id
    if not catalogs.is_dir():
        raise SalesPolicyError(f"HOME offer root lacks catalogs/{offer_id}: {home_root}")
    current: list[tuple[Any, str]] = []
    for candidate in sorted(catalogs.glob("*/offer.json")):
        try:
            document = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SalesPolicyError(f"HOME offer catalog is unreadable: {candidate}: {error}") from error
        if document.get("id") == offer_id and document.get("status") == "current":
            current.append((document.get("version"), candidate.relative_to(home_root).as_posix()))
    if len(current) != 1:
        raise SalesPolicyError(
            f"HOME offer {offer_id} must have exactly one current catalog, found {len(current)}"
        )
    version, relative = current[0]
    if version != home_meta["version"] or relative != home_meta["catalog_path"]:
        raise SalesPolicyError(
            f"HOME offer {offer_id} v{home_meta['version']} ({home_meta['catalog_path']}) is superseded: "
            f"current is v{version} ({relative})"
        )
    return relative


def compare_offer_home(
    home_catalog_path: Path | None = None,
    home_root: Path | None = None,
) -> dict[str, Any]:
    """Fail closed when the sales catalog drifts from the pinned ``subactor/offer`` HOME.

    This pack holds no prices, names or entitlements; it binds plan identifiers
    to one locked, current HOME catalog. With a HOME checkout (``home_root``) the
    lock must also pin the offer's only current version, so an archived or
    superseded catalog cannot pass.
    """

    lock = load_offer_home_lock()
    path = home_catalog_path
    if home_root is not None:
        relative = _require_current_home_version(home_root, lock["home"])
        if path is None:
            path = home_root / relative
    home = load_home_offer(path)
    sales = load_catalog()
    sales_ids = [plan["plan_id"] for plan in sales["plans"]]
    missing = [plan_id for plan_id in sales_ids if plan_id not in home["plans"]]
    if missing:
        raise SalesPolicyError(f"sales catalog plans absent from HOME offer: {missing}")
    uncovered = [
        plan_id for plan_id, plan in home["plans"].items() if plan.get("public") is not False and plan_id not in sales_ids
    ]
    if uncovered:
        raise SalesPolicyError(f"public HOME plans lack a sales catalog entry: {uncovered}")
    return {
        "ok": True,
        "offer_id": home["offer_id"],
        "version": home["version"],
        "digest": home["digest"],
        "checked_plan_ids": sales_ids,
        "home_path": str(home["path"]),
    }


def compare_www_plans(plans_path: Path) -> None:
    """Fail closed when a portal plans.json facade drifts from the locked HOME offer.

    Prices, names and operation entitlements HOME in ``subactor/offer``; this pack
    compares the facade with that locked HOME catalog and holds no copy of them.
    """

    catalog = load_catalog()
    home = load_home_offer()
    aliases = home["document"].get("compatibility", {}).get("read_aliases", {})
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
        home_plan = home["plans"][plan_id]

        actions = facade.get("actions_included", facade.get("agent_operations_included"))
        if actions != home_plan["agent_operations_included"]:
            raise SalesPolicyError(
                f"{plan_id} actions_included expected {home_plan['agent_operations_included']!r}, got {actions!r}"
            )

        canonical = home_plan["canonical_display_name"]
        allowed_names = {canonical, home_plan.get("name"), *(home_plan.get("legacy_display_names") or [])}
        allowed_names |= {alias for alias, target in aliases.items() if target == canonical}
        name = facade.get("name") or facade.get("display_name")
        if name not in allowed_names:
            raise SalesPolicyError(f"{plan_id} name {name!r} not in {sorted(item for item in allowed_names if item)}")

        for field in ("amount_monthly_minor", "amount_annual_minor", "currency"):
            if facade.get(field) != home_plan.get(field):
                raise SalesPolicyError(
                    f"{plan_id} {field} expected {home_plan.get(field)!r}, got {facade.get(field)!r}"
                )


def matrix() -> dict[str, Any]:
    cases = [
        ("NOCC100_BASIC", "saas-start", "NOCC100"),
        ("NOCC100_PRO", "saas-business", "NOCC100"),
        ("NOCC100_MAX", "prepaid-actions", "NOCC100"),
        ("NOCC100_ON_PREMISE", "on-premise", "NOCC100"),
        ("NO_PROMO_BASIC", "saas-start", ""),
        ("UNKNOWN_PROMO_BASIC", "saas-start", "OTHER100"),
        ("INVALID_PROMO_BASIC", "saas-start", "NOCC 100"),
    ]
    return {
        "schema": DECISION_MATRIX_SCHEMA,
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
        help="fail closed when the sales catalog drifts from the pinned, current subactor/offer HOME catalog",
    )
    home_parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="path to subactor/offer catalogs/.../offer.json (defaults to locked fixture)",
    )
    home_parser.add_argument(
        "--home-root",
        type=Path,
        default=None,
        help="subactor/offer checkout; the lock must pin its only current catalog version",
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
            result = compare_offer_home(args.catalog, args.home_root)
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
