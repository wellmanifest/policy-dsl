import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("policy_dsl_check", Path(__file__).with_name("policy_dsl_check.py"))
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)

SERVER = ROOT / "examples/hosting/subactor-production-server.policy"
RPI = ROOT / "examples/hosting/subactor-rpi5.policy"


class HostHardwarePolicyTest(unittest.TestCase):
    def test_production_server_policy_parses(self):
        ir = CHECK.parse(SERVER.read_text(encoding="utf-8"))
        self.assertEqual("SUBACTOR_PRODUCTION_SERVER", ir["document"]["name"])
        self.assertEqual("subactor.host/production-server/v1", ir["document"]["policy"])
        self.assertEqual(1, ir["document"]["version"])
        ids = [rule["id"] for rule in ir["rules"]]
        self.assertIn("SRV-RECOMMENDED-FIT", ids)
        self.assertIn("SRV-PLESK-EDGE-ONLY", ids)
        self.assertGreaterEqual(len(ir["rules"]), 8)

    def test_rpi5_policy_parses(self):
        ir = CHECK.parse(RPI.read_text(encoding="utf-8"))
        self.assertEqual("SUBACTOR_RPI5", ir["document"]["name"])
        self.assertEqual("subactor.host/rpi5/v1", ir["document"]["policy"])
        ids = [rule["id"] for rule in ir["rules"]]
        self.assertIn("RPI-FORBID-FULL-PLATFORM", ids)
        self.assertIn("RPI-PORTAL-EDGE", ids)
        self.assertIn("RPI-REJECT-MICROSD-DATA", ids)

    def test_host_policies_are_separate_documents(self):
        server = CHECK.parse(SERVER.read_text(encoding="utf-8"))
        rpi = CHECK.parse(RPI.read_text(encoding="utf-8"))
        self.assertNotEqual(server["document"]["name"], rpi["document"]["name"])
        self.assertNotEqual(server["document"]["policy"], rpi["document"]["policy"])

    def test_ir_schema_closed_for_both(self):
        for path in (SERVER, RPI):
            ir = CHECK.parse(path.read_text(encoding="utf-8"))
            CHECK.validate_ir(ir)


if __name__ == "__main__":
    unittest.main()
