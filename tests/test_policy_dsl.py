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

    def test_markdown_rejects_unclassified_dsl_fence(self):
        markdown = (ROOT / "examples/invalid/unclassified-dsl-fence.md").read_text(encoding="utf-8")
        with self.assertRaisesRegex(CHECK.PolicyError, "POLICY-SYNTAX-001: line 19: dsl fence is neither"):
            CHECK.parse_markdown(markdown)

    def test_markdown_skips_independent_documents_and_registered_records(self):
        markdown = (ROOT / "examples/valid/mixed-carrier.md").read_text(encoding="utf-8")
        ir = CHECK.parse_markdown(markdown)
        self.assertEqual("CONTRIBUTING", ir["document"]["name"])
        self.assertEqual(["C-DONE-001"], [rule["id"] for rule in ir["rules"]])
        self.assertEqual(["DONE", "EDIT"], sorted(ir["states"]))

    def test_markdown_rejects_policy_fence_before_header(self):
        markdown = "```dsl\nSTATE EDIT\n```\n\n```dsl\nDOCUMENT X\nVERSION 1\nMODE STRICT\n```\n"
        with self.assertRaisesRegex(CHECK.PolicyError, "precedes the DOCUMENT header"):
            CHECK.parse_markdown(markdown)

    def test_markdown_with_only_independent_schema_documents_has_no_policy(self):
        markdown = '```dsl\nDOCUMENT MERGE_DECISION\nVERSION 1\nMODE STRICT\nSCHEMA "wellmanifest.merge-decision/v1"\n```\n'
        with self.assertRaisesRegex(CHECK.PolicyError, "no concrete Policy DSL DOCUMENT fence"):
            CHECK.parse_markdown(markdown)

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

    def test_compact_constructs_desugar_to_identical_closed_ir(self):
        expanded = """DOCUMENT COMPACT_EQ
VERSION 1
MODE STRICT
STATE START
STATE EDIT
STATE VALIDATION
STATE BLOCKED
STATE REJECTED
TRANSITION START -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
TRANSITION EDIT -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
TRANSITION VALIDATION -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
RULE R-LOW-RAM TYPE REQUIRED
WHEN HOST_KIND = "PRODUCTION_SERVER" AND RAM_GIB < 8
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
DO RECORD REJECT_REASON "RAM_BELOW_MINIMUM"
NEXT REJECTED
RULE R-LOW-CPU TYPE REQUIRED
WHEN HOST_KIND = "PRODUCTION_SERVER" AND VCPU < 4
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
DO RECORD REJECT_REASON "VCPU_BELOW_MINIMUM"
NEXT REJECTED
"""
        compact = """DOCUMENT COMPACT_EQ
VERSION 1
MODE STRICT
STATES [START, EDIT, VALIDATION, BLOCKED, REJECTED]
TRANSITION [START, EDIT, VALIDATION] -> BLOCKED WHEN EVIDENCE_MISSING = TRUE
TEMPLATE REJECT_HOST
DO RECORD HOST_FIT "REJECT"
FORBID DEPLOY_PLATFORM
NEXT REJECTED
END
SCOPE WHEN HOST_KIND = "PRODUCTION_SERVER"
RULE R-LOW-RAM TYPE REQUIRED
WHEN RAM_GIB < 8
DO APPLY_TEMPLATE REJECT_HOST
DO RECORD REJECT_REASON "RAM_BELOW_MINIMUM"
RULE R-LOW-CPU TYPE REQUIRED
WHEN VCPU < 4
DO APPLY_TEMPLATE REJECT_HOST
DO RECORD REJECT_REASON "VCPU_BELOW_MINIMUM"
END
"""
        ir_expanded = CHECK.parse(expanded)
        ir_compact = CHECK.parse(compact)
        self.assertEqual(ir_expanded, ir_compact)

    def test_compact_constructs_in_markdown_carrier(self):
        markdown = """# Compact Policy
```dsl
DOCUMENT COMPACT_MD
VERSION 1
MODE STRICT
```
```dsl
STATES [PLAN, EDIT, BLOCKED]
TRANSITION [PLAN, EDIT] -> BLOCKED WHEN BLOCKED_FLAG = TRUE
```
```dsl
TEMPLATE T-REQ
DO REQUIRE CHECK_PASSED
NEXT EDIT
END
SCOPE WHEN ACTIVE = TRUE
RULE R-MD-001
WHEN READY = TRUE
DO APPLY_TEMPLATE T-REQ
END
```
"""
        ir = CHECK.parse_markdown(markdown)
        self.assertEqual(["PLAN", "EDIT", "BLOCKED"], ir["states"])
        self.assertEqual(2, len(ir["transitions"]))
        self.assertEqual("AND", ir["rules"][0]["condition"]["operator"])
        self.assertEqual("CHECK_PASSED", ir["rules"][0]["actions"][0]["payload"]["name"])
        self.assertEqual("EDIT", ir["rules"][0]["next"][0]["target"])

    def test_compact_construct_error_diagnostics(self):
        base = "DOCUMENT ERR\nVERSION 1\nMODE STRICT\nSTATES [A, B]\n"
        with self.assertRaisesRegex(CHECK.PolicyError, "unknown template"):
            CHECK.parse(base + "RULE R-1\nWHEN X = 1\nDO APPLY_TEMPLATE MISSING\n")
        with self.assertRaisesRegex(CHECK.PolicyError, "duplicate template"):
            CHECK.parse(base + "TEMPLATE T1\nDO ALLOW X\nEND\nTEMPLATE T1\nDO ALLOW Y\nEND\n")
        with self.assertRaisesRegex(CHECK.PolicyError, "empty template"):
            CHECK.parse(base + "TEMPLATE T1\nEND\n")
        with self.assertRaisesRegex(CHECK.PolicyError, "empty SCOPE block"):
            CHECK.parse(base + "SCOPE WHEN X = 1\nEND\n")
        with self.assertRaisesRegex(CHECK.PolicyError, "SCOPE requires closing END"):
            CHECK.parse(base + "SCOPE WHEN X = 1\nRULE R-1\nWHEN Y = 2\nDO ALLOW Z\n")

    def test_audit_compaction_detects_all_four_patterns(self):
        bloated = """DOCUMENT BLOATED_TEST
VERSION 1
MODE STRICT
STATES [S1, S2, S3, BLOCKED, REJECTED]
TRANSITION S1 -> BLOCKED WHEN ERR = TRUE
TRANSITION S2 -> BLOCKED WHEN ERR = TRUE
TRANSITION S3 -> BLOCKED WHEN ERR = TRUE
RULE R-1
WHEN ENV = "PROD" AND VERY_LONG_PROSE_SYMBOL_THAT_ENCODES_AN_ENTIRE_SENTENCE_WITH_MANY_UNDERSCORES = TRUE
DO RECORD FIT "REJECT"
FORBID DEPLOY_ALL
NEXT REJECTED
RULE R-2
WHEN ENV = "PROD" AND MEM < 8
DO RECORD FIT "REJECT"
FORBID DEPLOY_ALL
NEXT REJECTED
RULE R-3
WHEN ENV = "PROD" AND CPU < 4
DO RECORD FIT "REJECT"
FORBID DEPLOY_ALL
NEXT REJECTED
"""
        report = CHECK.audit_compaction(bloated)
        codes = {item["code"] for item in report["findings"]}
        self.assertEqual(
            {"POLICY-COMPACT-001", "POLICY-COMPACT-002", "POLICY-COMPACT-003", "POLICY-COMPACT-004"},
            codes,
        )
        self.assertGreaterEqual(report["stats"]["estimated_lines_saved"], 8)


if __name__ == "__main__":
    unittest.main()

