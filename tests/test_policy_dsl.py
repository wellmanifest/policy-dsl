import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("policy_dsl_check", Path(__file__).with_name("policy_dsl_check.py"))
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class PolicyDslConformanceTest(unittest.TestCase):
    def test_valid_fixture_produces_typed_ir(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        self.assertEqual("1", ir["language_version"])
        self.assertEqual(13, ir["document"]["version"])
        self.assertEqual("binary", ir["rules"][0]["condition"]["node"])
        self.assertEqual("symbol", ir["rules"][0]["actions"][0]["payload"]["node"])
        self.assertNotIn('"text"', json.dumps(ir))

    def test_invalid_shell_fixture_is_rejected(self):
        with self.assertRaisesRegex(CHECK.PolicyError, "POLICY-SECURITY-001"):
            CHECK.parse((ROOT / "examples/invalid/shell-injection.policy").read_text(encoding="utf-8"))

    def test_ir_contract_is_closed(self):
        schema = json.loads((ROOT / "schemas/policy-ir.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(CHECK.schema_is_closed(schema))
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["unexpected"] = True
        with self.assertRaisesRegex(CHECK.PolicyError, "closed Policy IR"):
            CHECK.validate_ir(ir)

    def test_candidate_boundary_rejects_runtime_opcode(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(CHECK.PolicyError, "POLICY-SECURITY-001"):
            CHECK.validate_candidate(ir)

    def test_candidate_boundary_rejects_malformed_closed_ir(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["rules"][0]["type"] = "OPTIONAL"
        with self.assertRaisesRegex(CHECK.PolicyError, "POLICY-SEMANTIC-001"):
            CHECK.validate_candidate(ir)

        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["states"] = "START"
        with self.assertRaisesRegex(CHECK.PolicyError, "POLICY-SEMANTIC-001"):
            CHECK.validate_candidate(ir)

    def test_operator_precedence(self):
        expression = CHECK.parse_expression("A = TRUE OR B = FALSE AND C IN [A, B]", 1)
        self.assertEqual("OR", expression["operator"])
        self.assertEqual("AND", expression["right"]["operator"])

    def test_markdown_selector_ignores_examples_and_shell_fences(self):
        markdown = (ROOT / "examples/valid/CONTRIBUTING.md").read_text(encoding="utf-8")
        ir = CHECK.parse_markdown(markdown)
        self.assertEqual(["C-CONTRIBUTING-001"], [rule["id"] for rule in ir["rules"]])
        self.assertEqual("binary", ir["rules"][0]["condition"]["node"])
        self.assertEqual(["PLAN", "PUBLICATION", "VALIDATION"], sorted(ir["states"]))
        self.assertEqual("VALIDATION", ir["rules"][0]["next"][0]["target"])
        self.assertEqual("PLAN", ir["rules"][0]["next"][1]["target"])

    def test_validate_ir_rejects_duplicate_binding(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["bindings"].append(dict(ir["bindings"][0]))
        with self.assertRaisesRegex(CHECK.PolicyError, "duplicate binding"):
            CHECK.validate_ir(ir)

    def test_validate_ir_rejects_duplicate_environment_name(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        variable = next(item for item in ir["environment"] if item["kind"] == "variable")
        ir["environment"].append(dict(variable))
        with self.assertRaisesRegex(CHECK.PolicyError, "duplicate environment name"):
            CHECK.validate_ir(ir)

    def test_validate_ir_rejects_duplicate_transition(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["transitions"].append(dict(ir["transitions"][0]))
        with self.assertRaisesRegex(CHECK.PolicyError, "duplicate transition"):
            CHECK.validate_ir(ir)

    def test_validate_ir_rejects_undeclared_next_state(self):
        ir = CHECK.parse((ROOT / "examples/valid/contributing.policy").read_text(encoding="utf-8"))
        ir["rules"][0]["next"] = [{"target": "MISSING", "condition": None}]
        with self.assertRaisesRegex(CHECK.PolicyError, "undeclared state"):
            CHECK.validate_ir(ir)

    def test_invalid_uniqueness_fixtures_reject(self):
        cases = {
            "duplicate-binding.policy": "duplicate binding",
            "duplicate-environment.policy": "duplicate environment name",
            "duplicate-transition.policy": "duplicate transition",
            "undeclared-next-state.policy": "undeclared state",
        }
        for name, message in cases.items():
            with self.subTest(name=name):
                with self.assertRaisesRegex(CHECK.PolicyError, message):
                    CHECK.parse((ROOT / "examples/invalid" / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
