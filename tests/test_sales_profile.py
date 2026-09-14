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
        self.assertEqual(2, ir["document"]["version"])
        self.assertEqual(4, len(ir["rules"]))
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

    def test_catalog_holds_only_sales_owned_fields(self):
        catalog = SALES.load_catalog()
        self.assertEqual("subactor.sales/catalog/v2", catalog["schema"])
        allowed = {"plan_id", "public_code", "legacy_public_codes", "payment_card_required", "eligible_promo_codes"}
        for plan in catalog["plans"]:
            with self.subTest(plan_id=plan["plan_id"]):
                self.assertEqual(allowed, set(plan))

    def test_catalog_rejects_home_owned_fields(self):
        for field, value in (
            ("amount_monthly_minor", 5000),
            ("display_name", "Pro"),
            ("active_twins_included", 0),
            ("operation_label_pl", "5 000 operacji agenta / miesiąc"),
        ):
            catalog = json.loads((ROOT / "profiles/sales/offer-catalog.json").read_text(encoding="utf-8"))
            catalog["plans"][1][field] = value
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "offer-catalog.json"
                path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaisesRegex(SALES.SalesPolicyError, rf"closed plan\[1\]: unknown=\['{field}'\]"):
                    SALES.load_catalog(path)

    def test_entitlements_names_and_amounts_come_from_home(self):
        home = SALES.load_home_offer()
        self.assertEqual("offer://subactor/offer/subactor-cloud/v2", home["offer_ref"])
        expected = {
            "saas-start": ("basic", "Basic", 1000, 5000),
            "saas-business": ("pro", "Pro", 5000, 22500),
            "prepaid-actions": ("max", "Max", 20000, 80000),
        }
        for plan_id, (public_code, name, included, monthly) in expected.items():
            with self.subTest(plan_id=plan_id):
                decision = SALES.decide(plan_id, "")
                self.assertEqual(public_code, decision["offer"]["public_code"])
                self.assertEqual(name, decision["offer"]["display_name"])
                self.assertEqual("usage-subscription", decision["offer"]["commercial_type"])
                self.assertEqual(included, decision["metering"]["included"])
                self.assertEqual("actions_monthly", decision["metering"]["period"])
                self.assertEqual(monthly, home["plans"][plan_id]["amount_monthly_minor"])
                self.assertEqual(home["digest"], decision["home"]["digest"])

    def test_decisions_carry_no_twin_or_copy_fields(self):
        encoded = json.dumps(SALES.matrix(), ensure_ascii=False)
        for fragment in ("active_twins", "entitlement_kind", "label_pl", "seat_summary", "Twin Plus", "Operations Plus"):
            self.assertNotIn(fragment, encoded)
        for case in SALES.matrix()["cases"]:
            with self.subTest(name=case["name"]):
                self.assertEqual([], case["decision"]["policy"]["reports"])

    def test_public_and_legacy_plan_codes_resolve(self):
        cases = {
            "basic": ("saas-start", "basic"),
            "pro": ("saas-business", "pro"),
            "max": ("prepaid-actions", "max"),
            "operations-plus": ("saas-business", "pro"),
            "twin-plus": ("prepaid-actions", "max"),
        }
        for identifier, (plan_id, public_code) in cases.items():
            with self.subTest(identifier=identifier):
                decision = SALES.decide(identifier, "")
                self.assertEqual(plan_id, decision["offer"]["plan_id"])
                self.assertEqual(public_code, decision["offer"]["public_code"])

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

    def test_golden_decision_matrix(self):
        expected = json.loads(
            (ROOT / "profiles/sales/decision-matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual(expected, SALES.matrix())

    def test_consumer_decision_fixture_matches_decide(self):
        fixture_path = ROOT / "examples/sales/decisions/matrix.v2.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual("subactor.sales/decision-matrix/v2", fixture["schema"])
        self.assertEqual(fixture, SALES.matrix())
        required = {"schema", "input", "offer", "promotion", "payment", "metering", "home", "policy"}
        for case in fixture["cases"]:
            with self.subTest(name=case["name"]):
                decision = case["decision"]
                self.assertEqual("subactor.sales/decision/v2", decision["schema"])
                self.assertEqual(required, set(decision))
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
        self.assertEqual("examples/sales/fixtures/www-plans.facade.json", lock["fixture_path"])
        self.assertEqual("offer://subactor/offer/subactor-cloud/v2", lock["facade"]["offer_pin"])
        self.assertNotIn("active_twins_included", lock["compared_fields"])
        SALES.compare_www_plans(fixture)

    def test_compare_www_plans_accepts_home_legacy_names(self):
        fixture = ROOT / "examples/sales/fixtures/www-plans.facade.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["plans"]["saas-business"]["name"] = "Operations Plus"
        payload["plans"]["prepaid-actions"]["name"] = "Twin Plus"
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "plans.json"
            legacy.write_text(json.dumps(payload), encoding="utf-8")
            SALES.compare_www_plans(legacy)

    def test_compare_www_plans_rejects_price_drift(self):
        fixture = ROOT / "examples/sales/fixtures/www-plans.facade.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["plans"]["saas-start"]["amount_monthly_minor"] = 9700
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "plans.json"
            stale.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SALES.SalesPolicyError, "saas-start amount_monthly_minor expected 5000, got 9700"):
                SALES.compare_www_plans(stale)

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

    def test_compare_offer_home_accepts_locked_fixture(self):
        lock = SALES.load_offer_home_lock()
        result = SALES.compare_offer_home()
        self.assertTrue(result["ok"])
        self.assertEqual("subactor-cloud", result["offer_id"])
        self.assertEqual(2, result["version"])
        self.assertEqual(lock["home"]["digest"], result["digest"])
        self.assertEqual(
            ["saas-start", "saas-business", "prepaid-actions", "on-premise"],
            result["checked_plan_ids"],
        )

    def _patched_home(self, tmp: str, document: dict):
        from unittest import mock

        lock = SALES.load_offer_home_lock()
        path = Path(tmp) / "offer.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        patched = json.loads(json.dumps(lock))
        patched["home"]["digest"] = SALES._file_digest(path)
        return path, mock.patch.object(SALES, "load_offer_home_lock", return_value=patched)

    def test_compare_offer_home_rejects_uncovered_public_home_plan(self):
        lock = SALES.load_offer_home_lock()
        document = json.loads((ROOT / lock["fixture_path"]).read_text(encoding="utf-8"))
        extra = dict(document["plans"][0], plan_id="saas-enterprise", public=True)
        document["plans"].append(extra)
        with tempfile.TemporaryDirectory() as tmp:
            path, patch = self._patched_home(tmp, document)
            with patch, self.assertRaisesRegex(SALES.SalesPolicyError, "public HOME plans lack a sales catalog entry"):
                SALES.compare_offer_home(path)

    def test_compare_offer_home_rejects_non_current_catalog(self):
        lock = SALES.load_offer_home_lock()
        document = json.loads((ROOT / lock["fixture_path"]).read_text(encoding="utf-8"))
        document["status"] = "archived"
        with tempfile.TemporaryDirectory() as tmp:
            path, patch = self._patched_home(tmp, document)
            with patch, self.assertRaisesRegex(SALES.SalesPolicyError, "is 'archived', not 'current'"):
                SALES.compare_offer_home(path)

    def _home_root(self, tmp: str, versions: dict[str, dict]) -> Path:
        root = Path(tmp) / "offer"
        for version_dir, document in versions.items():
            target = root / "catalogs" / "subactor-cloud" / version_dir / "offer.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(document), encoding="utf-8")
        return root

    def test_compare_offer_home_accepts_home_root_when_pin_is_current(self):
        lock = SALES.load_offer_home_lock()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "offer"
            target = root / lock["home"]["catalog_path"]
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / lock["fixture_path"]).read_bytes())
            result = SALES.compare_offer_home(home_root=root)
        self.assertTrue(result["ok"])

    def test_compare_offer_home_rejects_superseded_pin(self):
        lock = SALES.load_offer_home_lock()
        pinned = json.loads((ROOT / lock["fixture_path"]).read_text(encoding="utf-8"))
        version = lock["home"]["version"]
        with tempfile.TemporaryDirectory() as tmp:
            root = self._home_root(
                tmp,
                {
                    f"v{version}": dict(pinned, status="archived"),
                    f"v{version + 1}": dict(pinned, status="current", version=version + 1),
                },
            )
            with self.assertRaisesRegex(
                SALES.SalesPolicyError, f"v{version} \\(.+\\) is superseded: current is v{version + 1}"
            ):
                SALES.compare_offer_home(home_root=root)

    def test_compare_offer_home_rejects_ambiguous_current_versions(self):
        lock = SALES.load_offer_home_lock()
        pinned = json.loads((ROOT / lock["fixture_path"]).read_text(encoding="utf-8"))
        version = lock["home"]["version"]
        with tempfile.TemporaryDirectory() as tmp:
            root = self._home_root(
                tmp, {f"v{version}": pinned, f"v{version + 1}": dict(pinned, version=version + 1)}
            )
            with self.assertRaisesRegex(SALES.SalesPolicyError, "exactly one current catalog, found 2"):
                SALES.compare_offer_home(home_root=root)

    def test_live_home_checkout_pins_the_current_offer_when_present(self):
        home_root = Path("/home/tom/github/subactor/offer")
        if not (home_root / "catalogs").is_dir():
            self.skipTest("subactor/offer checkout not available on this host")
        SALES.compare_offer_home(home_root=home_root)


if __name__ == "__main__":
    unittest.main()
