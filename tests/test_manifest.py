import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DslManifestTest(unittest.TestCase):
    def test_version_and_artifact_digests(self):
        manifest = json.loads((ROOT / "dsl-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), manifest["version"])

        paths = [artifact["path"] for artifact in manifest["artifacts"]]
        self.assertEqual(len(paths), len(set(paths)))
        for artifact in manifest["artifacts"]:
            with self.subTest(path=artifact["path"]):
                path = ROOT / artifact["path"]
                self.assertTrue(path.is_file())
                digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(artifact["digest"], digest)

    def test_sales_profile_is_published_by_the_manifest(self):
        manifest = json.loads((ROOT / "dsl-manifest.json").read_text(encoding="utf-8"))
        paths = {artifact["path"] for artifact in manifest["artifacts"]}
        expected = {
            "docs/DOMAIN_VOCABULARY_PL.md",
            "profiles/sales/README.md",
            "profiles/sales/ADOPTION_PL.md",
            "profiles/sales/subactor-sales.policy",
            "profiles/sales/offer-catalog.json",
            "profiles/sales/decision-matrix.json",
            "profiles/sales/reference_engine.py",
            "schemas/sales-request.schema.json",
            "schemas/sales-offer-catalog.schema.json",
            "schemas/sales-decision.schema.json",
            "tests/test_sales_profile.py",
        }
        self.assertTrue(expected <= paths)
        self.assertIn("profiles/**", manifest["ownedPaths"])


if __name__ == "__main__":
    unittest.main()
