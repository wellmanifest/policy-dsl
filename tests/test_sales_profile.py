import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "subactor_sales_reference_engine",
    ROOT / "profiles/sales/reference_engine.py",
)
SALES = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SALES
SPEC.loader.exec_module(SALES)


class SubactorSalesProfileTest(unittest.TestCase):
    def test_policy_is_valid_and_uses_profile_safe_directives(self):
        ir = SALES.CHECK.parse(
            (ROOT / "profiles/sales/subactor-sales.policy").read_text(encoding="utf-8")
        )
        self.assertEqual("SUBACTOR_SALES", ir["document"]["name"])
        self.assertEqual(1, ir["document"]["version"])
        self.assertEqual(5, len(ir["rules"]))
        self.assertTrue(all(rule["type"] == "REQUIRED" for rule in ir["rules"]))
        action_opcodes = {
            action["opcode"]
            for rule in ir["rules"]
            for action in rule["actions"]
        }
        self.assertTrue(action_opcodes <= {"RECORD", "ALLOW", "REQUIRE", "REPORT"})
        forbidden_opcodes = {
            action["opcode"]
            for rule in ir["rules"]
            for action in rule["forbidden"]
        }
        self.assertTrue(forbidden_opcodes <= SALES.FORBIDDEN_OPCODES)

    def test_nocc100_is_eligible_only_for_basic(self):
        basic = SALES.decide("saas-start", " nocc100 ")
        self.assertEqual("ELIGIBLE", basic["promotion"]["eligibility"])
        self.assertEqual("NOCC100", basic["promotion"]["normalized_code"])
        self.assertEqual("VISIBLE", basic["promotion"]["presentation"])
        self.assertFalse(basic["payment"]["card_required"])
        self.assertIn("APPLY_PROMOTION", basic["policy"]["allowed"])

        for plan_id in ("saas-business", "prepaid-actions", "on-premise"):
            with self.subTest(plan_id=plan_id):
                decision = SALES.decide(plan_id, "NOCC100")
                self.assertEqual("INELIGIBLE", decision["promotion"]["eligibility"])
                self.assertEqual("", decision["promotion"]["normalized_code"])
                self.assertEqual("HIDDEN", decision["promotion"]["presentation"])
                self.assertEqual("PLAN_NOT_ELIGIBLE", decision["promotion"]["reason"])
                self.assertIn("PROMOTION_SANITIZED", decision["policy"]["required"])
                forbidden = {item["opcode"] for item in decision["policy"]["forbidden"]}
                self.assertIn("APPLY_PROMOTION", forbidden)
                self.assertIn("DISPLAY_PROMOTION", forbidden)
                self.assertNotIn("BLOCK_CHECKOUT", forbidden)
                self.assertEqual(plan_id, decision["offer"]["plan_id"])

    def test_empty_promo_does_not_create_a_promotion_effect(self):
        decision = SALES.decide("saas-business", "")
        self.assertEqual("NONE", decision["promotion"]["eligibility"])
        self.assertEqual("NO_PROMO", decision["promotion"]["reason"])
        self.assertEqual([], decision["policy"]["allowed"])
        self.assertEqual([], decision["policy"]["required"])
        forbidden = {item["opcode"] for item in decision["policy"]["forbidden"]}
        self.assertNotIn("APPLY_PROMOTION", forbidden)
        self.assertTrue(decision["payment"]["card_required"])

    def test_operations_vocabulary_and_legacy_alias(self):
        catalog = SALES.load_catalog()
        by_id = {plan["plan_id"]: plan for plan in catalog["plans"]}
        operations = by_id["saas-business"]
        self.assertEqual("Operations Plus", operations["display_name"])
        self.assertIn("Actions Plus", operations["legacy_display_names"])
        self.assertEqual("AGENT_OPERATION", catalog["vocabulary"]["unit_code"])
        self.assertNotIn("actions_included", operations)
        self.assertEqual("2026-08-16", catalog["compatibility"]["write_freeze_date"])
        self.assertEqual("CANONICAL_ONLY", catalog["compatibility"]["write_policy"])

    def test_legacy_write_freeze_rejects_actions_included_on_plan(self):
        catalog = json.loads(
            (ROOT / "profiles/sales/offer-catalog.json").read_text(encoding="utf-8")
        )
        catalog["plans"][0]["actions_included"] = 1000
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            json.dump(catalog, handle)
            path = Path(handle.name)
        try:
            with self.assertRaisesRegex(SALES.SalesPolicyError, "legacy write freeze"):
                SALES.load_catalog(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(
            "agent_operations_included",
            catalog["compatibility"]["read_aliases"]["actions_included"],
        )
        self.assertEqual("CANONICAL_ONLY", catalog["compatibility"]["write_policy"])

    def test_twin_plus_explains_zero_operations_and_separate_package(self):
        decision = SALES.decide("prepaid-actions", "NOCC100")
        self.assertEqual(0, decision["metering"]["included"])
        self.assertEqual("SEPARATE_PACKAGE", decision["metering"]["source"])
        self.assertNotIn("Brak", decision["metering"]["label_pl"])
        self.assertIn("0 operacji", decision["metering"]["label_pl"])
        self.assertIn("Operations Plus", decision["metering"]["label_pl"])
        self.assertIn("OPERATIONS_PURCHASED_SEPARATELY", decision["policy"]["reports"])
        forbidden = {item["opcode"] for item in decision["policy"]["forbidden"]}
        self.assertIn("DISPLAY_OPERATION_LABEL", forbidden)

    def test_public_plan_codes_are_supported_without_changing_legacy_ids(self):
        operations = SALES.decide("operations-plus", "")
        twin = SALES.decide("twin-plus", "")
        basic = SALES.decide("basic", "")
        self.assertEqual("saas-business", operations["offer"]["plan_id"])
        self.assertEqual("prepaid-actions", twin["offer"]["plan_id"])
        self.assertEqual("saas-start", basic["offer"]["plan_id"])

    def test_unknown_and_invalid_codes_are_hidden(self):
        unknown = SALES.decide("saas-start", " other100 ")
        self.assertEqual("UNKNOWN", unknown["promotion"]["eligibility"])
        self.assertEqual("UNKNOWN_PROMO_CODE", unknown["promotion"]["reason"])
        self.assertEqual("", unknown["promotion"]["normalized_code"])
        self.assertEqual("HIDDEN", unknown["promotion"]["presentation"])

        invalid = SALES.decide("saas-start", "NOCC 100")
        self.assertEqual("UNKNOWN", invalid["promotion"]["eligibility"])
        self.assertEqual("INVALID_PROMO_FORMAT", invalid["promotion"]["reason"])
        self.assertEqual("", invalid["promotion"]["normalized_code"])
        self.assertEqual("HIDDEN", invalid["promotion"]["presentation"])
        self.assertIn("PROMOTION_SANITIZED", invalid["policy"]["required"])

    def test_evaluator_rejects_implicit_scalar_coercion(self):
        mixed_equality = {
            "node": "binary",
            "operator": "=",
            "left": {"node": "literal", "value": 1},
            "right": {"node": "literal", "value": True},
        }
        self.assertFalse(SALES.evaluate_expression(mixed_equality, {}))

        invalid_and = {
            "node": "binary",
            "operator": "AND",
            "left": {"node": "literal", "value": True},
            "right": {"node": "literal", "value": 1},
        }
        with self.assertRaisesRegex(SALES.SalesPolicyError, "AND requires BOOLEAN"):
            SALES.evaluate_expression(invalid_and, {})

        mixed_addition = {
            "node": "binary",
            "operator": "+",
            "left": {"node": "literal", "value": 1},
            "right": {"node": "literal", "value": 1.0},
        }
        with self.assertRaisesRegex(SALES.SalesPolicyError, "one scalar type"):
            SALES.evaluate_expression(mixed_addition, {})

        division_by_zero = {
            "node": "binary",
            "operator": "/",
            "left": {"node": "literal", "value": 1},
            "right": {"node": "literal", "value": 0},
        }
        with self.assertRaisesRegex(SALES.SalesPolicyError, "division by zero"):
            SALES.evaluate_expression(division_by_zero, {})

    def test_pricing_projection_matches_catalog_and_promotion_policy(self):
        html = (ROOT / "examples/sales/subactor-pricing-section.html").read_text(encoding="utf-8")
        catalog = SALES.load_catalog()
        by_id = {plan["plan_id"]: plan for plan in catalog["plans"]}

        self.assertIn(by_id["saas-business"]["display_name"], html)
        self.assertNotIn("Actions Plus", html)
        self.assertNotIn("akcji agenta", html)
        self.assertNotIn("pakiet akcji", html)
        self.assertIn(by_id["prepaid-actions"]["seat_summary_pl"], html)
        self.assertNotIn("• Brak", html)
        for plan_id in ("saas-start", "saas-business", "prepaid-actions"):
            self.assertIn(f'data-plan="{plan_id}"', html)

        business_start = html.index('data-plan="saas-business"')
        twin_start = html.index('data-plan="prepaid-actions"', business_start)
        business_card = html[business_start:twin_start]
        self.assertNotIn("NOCC100", business_card)
        self.assertIn("<dt>Karta przy starcie</dt><dd>Wymagana</dd>", business_card)

        basic_start = html.index('data-plan="saas-start"')
        business_start = html.index('data-plan="saas-business"', basic_start)
        basic_card = html[basic_start:business_start]
        self.assertIn(by_id["saas-start"]["promo_hint_pl"], basic_card)

    def test_golden_decision_matrix(self):
        expected = json.loads(
            (ROOT / "profiles/sales/decision-matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual(expected, SALES.matrix())

    def test_consumer_decision_fixture_matches_decide(self):
        fixture_path = ROOT / "examples/sales/decisions/matrix.v1.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual("subactor.sales/decision-matrix/v1", fixture["schema"])
        self.assertEqual(fixture, SALES.matrix())
        required = {"schema", "input", "offer", "promotion", "payment", "metering", "policy"}
        for case in fixture["cases"]:
            with self.subTest(name=case["name"]):
                decision = case["decision"]
                self.assertEqual("subactor.sales/decision/v1", decision["schema"])
                self.assertTrue(required <= set(decision))
                self.assertEqual(
                    decision,
                    SALES.decide(decision["input"]["plan_id"], decision["input"]["promo_code"]),
                )
        self.assertEqual(
            0,
            SALES.main(["export-decisions", "--check", str(fixture_path)]),
        )

    def test_sales_schemas_are_closed(self):
        for path in (
            ROOT / "schemas/sales-request.schema.json",
            ROOT / "schemas/sales-offer-catalog.schema.json",
            ROOT / "schemas/sales-decision.schema.json",
        ):
            with self.subTest(path=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(SALES.CHECK.schema_is_closed(schema))

    def test_unknown_plan_is_rejected(self):
        with self.assertRaisesRegex(SALES.SalesPolicyError, "unknown plan_id"):
            SALES.decide("enterprise-imaginary", "NOCC100")

    def test_compare_www_plans_accepts_locked_fixture(self):
        lock = json.loads(
            (ROOT / "profiles/sales/www-plans.lock.json").read_text(encoding="utf-8")
        )
        fixture = ROOT / lock["fixture_path"]
        self.assertTrue(fixture.is_file())
        self.assertEqual(
            "examples/sales/fixtures/www-plans.facade.json",
            lock["fixture_path"],
        )
        self.assertEqual(
            "offer://subactor/offer/subactor-cloud/v1",
            lock["facade"]["offer_pin"],
        )
        SALES.compare_www_plans(fixture)

    def test_compare_www_plans_rejects_ops_drift(self):
        import tempfile

        fixture = ROOT / "examples/sales/fixtures/www-plans.facade.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["plans"]["saas-business"]["actions_included"] = 10000
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            bad = Path(handle.name)
        try:
            with self.assertRaisesRegex(SALES.SalesPolicyError, "saas-business actions_included"):
                SALES.compare_www_plans(bad)
        finally:
            bad.unlink(missing_ok=True)

    def test_compare_www_plans_accepts_live_www_when_present(self):
        www_plans = Path("/home/tom/github/subactor/www-sub-actor/src/php_app/config/plans.json")
        if not www_plans.is_file():
            self.skipTest("www-sub-actor plans.json not available in this checkout")
        SALES.compare_www_plans(www_plans)

    def test_operations_plus_matches_otp_sheet_quota(self):
        catalog = SALES.load_catalog()
        by_id = {plan["plan_id"]: plan for plan in catalog["plans"]}
        self.assertEqual(1000, by_id["saas-business"]["agent_operations_included"])
        self.assertEqual(9700, by_id["saas-start"]["amount_monthly_minor"])
        self.assertEqual(5900, by_id["saas-business"]["amount_monthly_minor"])
        self.assertEqual(5900, by_id["prepaid-actions"]["amount_monthly_minor"])

    def test_compare_offer_home_accepts_locked_fixture(self):
        result = SALES.compare_offer_home()
        self.assertTrue(result["ok"])
        self.assertEqual("subactor-cloud", result["offer_id"])
        self.assertEqual(1, result["version"])
        self.assertEqual(
            "sha256:95c3392d3b677092240eb9b7781c70eb079d30e2c7b84eac337dd3de8a03a2dc",
            result["digest"],
        )
        self.assertEqual(
            ["saas-start", "saas-business", "prepaid-actions", "on-premise"],
            result["checked_plan_ids"],
        )

    def test_compare_offer_home_rejects_digest_drift(self):
        import tempfile

        lock = SALES.load_offer_home_lock()
        fixture = ROOT / lock["fixture_path"]
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["title"] = "tampered"
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            bad = Path(handle.name)
        try:
            with self.assertRaisesRegex(SALES.SalesPolicyError, "HOME offer digest drift"):
                SALES.compare_offer_home(bad)
        finally:
            bad.unlink(missing_ok=True)

    def test_compare_offer_home_rejects_amount_mirror_drift(self):
        import tempfile
        from unittest import mock

        catalog = json.loads((ROOT / "profiles/sales/offer-catalog.json").read_text(encoding="utf-8"))
        for plan in catalog["plans"]:
            if plan["plan_id"] == "saas-start":
                plan["amount_monthly_minor"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            bad_catalog = Path(tmp) / "offer-catalog.json"
            bad_catalog.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(SALES, "CATALOG_PATH", bad_catalog):
                with self.assertRaisesRegex(SALES.SalesPolicyError, "saas-start.amount_monthly_minor"):
                    SALES.compare_offer_home()


if __name__ == "__main__":
    unittest.main()
