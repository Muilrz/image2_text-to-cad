"""Release contracts: install references, independent identity and portable source archives."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/text-to-cad-visual"


class DistributionTests(unittest.TestCase):
    def test_codex_marketplace_points_to_installable_plugin(self):
        market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entry = market["plugins"][0]
        self.assertEqual(market["name"], "ming-cad-lab")
        self.assertEqual((ROOT / entry["source"]["path"]).resolve(), PLUGIN.resolve())
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(manifest["name"], "text-to-cad-visual")
        self.assertTrue((PLUGIN / manifest["skills"]).is_dir())
        self.assertTrue((PLUGIN / manifest["mcpServers"]).is_file())
        server = json.loads((PLUGIN / manifest["mcpServers"]).read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(set(server), {"cad_visual"})
        self.assertIn("cadgen==0.7.24", server["cad_visual"]["args"])
        self.assertTrue((PLUGIN / "skills/image-cad-preflight/scripts/visual_preflight.py").is_file())

    def test_other_manifests_do_not_advertise_upstream_plugin_identity(self):
        for name in ("plugin.json", "gemini-extension.json", ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
            with self.subTest(name=name):
                doc = json.loads((PLUGIN / name).read_text(encoding="utf-8"))
                self.assertEqual(doc["name"], "text-to-cad-visual")
                for field in ("skills", "mcpServers", "logo"):
                    if isinstance(doc.get(field), str):
                        self.assertTrue((PLUGIN / doc[field]).exists(), field)
        market = json.loads((PLUGIN / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(market["name"], "ming-cad-lab")
        self.assertEqual(market["plugins"][0]["name"], "text-to-cad-visual")

    def test_source_archive_runs_without_local_baseline_or_dependencies(self):
        with tempfile.TemporaryDirectory(prefix="cad distribution ") as folder:
            output = Path(folder) / "plugin.zip"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/package_for_github.py"), "--output", str(output)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                for private in ("baseline.json", "VALIDATION.md", "README.zh-CN.md"):
                    self.assertNotIn("text-to-cad-visual/" + private, names)
                for name in names:
                    self.assertFalse(set(Path(name).parts) & {".tmp", ".git", "__pycache__", ".cad_context"}, name)
                self.assertIn("text-to-cad-visual/.github/workflows/test.yml", names)
                archive.extractall(Path(folder) / "unpacked")
            clean = Path(folder) / "unpacked/text-to-cad-visual"
            check = subprocess.run([sys.executable, "scripts/check_fork.py"], cwd=clean,
                                   capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertEqual(json.loads(check.stdout)["baseline_files_checked"], 0)
            # Exercise the distributed CLI from a different working directory, with only in-chat data.
            data = Path(folder) / "inspection.json"
            data.write_text(json.dumps({"schema_version":"1.0", "p0":[], "p1":[], "unknown":[]}), encoding="utf-8")
            md, raw = Path(folder) / "spec.md", Path(folder) / "spec.json"
            child = subprocess.run([sys.executable, str(clean / "plugins/text-to-cad-visual/skills/image-cad-preflight/scripts/visual_preflight.py"),
                                    "--from-json", str(data), "--image-label", "view 1", "--output", str(md), "--json-out", str(raw)],
                                   cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertEqual(json.loads(raw.read_text(encoding="utf-8"))["mode"], "main-session")
            self.assertTrue(md.is_file())


if __name__ == "__main__":
    unittest.main()
