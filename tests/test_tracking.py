"""Integrity checks using temporary copies; originals are never modified."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_sources import validate


class TrackingIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ["tex", "lectures", "assets", "pdf-prof"]:
            shutil.copytree(ROOT / directory, self.root / directory)
        for filename in ["main.tex", "sources.json"]:
            shutil.copy2(ROOT / filename, self.root / filename)
        self.manifest = json.loads((self.root / "sources.json").read_text())

    def save(self):
        (self.root / "sources.json").write_text(json.dumps(self.manifest))

    def assert_error(self, phrase):
        errors = validate(self.root, require_sources=True)["errors"]
        self.assertTrue(any(phrase in error for error in errors), errors)

    def test_complete_project(self):
        result = validate(self.root, require_sources=True)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["source_pages"], sum(s["page_count"] for s in self.manifest["sources"]))

    def test_omitted_page(self):
        self.manifest["sources"][0]["pages"].pop(4)
        self.save()
        self.assert_error("Page coverage/order mismatch")

    def test_duplicate_source(self):
        self.manifest["sources"].append(self.manifest["sources"][0])
        self.save()
        self.assert_error("Duplicate PDF")

    def test_duplicate_page(self):
        pages = self.manifest["sources"][0]["pages"]
        pages[1] = pages[0]
        self.save()
        self.assert_error("Duplicate page entry")

    def test_changed_pdf(self):
        source = self.root / "pdf-prof" / self.manifest["sources"][0]["filename"]
        source.write_bytes(source.read_bytes() + b"\n% changed source\n")
        self.assert_error("Source checksum changed")

    def test_unrecorded_pdf_reported_pending(self):
        source = self.root / "pdf-prof" / self.manifest["sources"][0]["filename"]
        shutil.copy2(source, self.root / "pdf-prof/999999 - Tracking test.pdf")
        result = validate(self.root, require_sources=True)
        self.assertTrue(result["errors"])
        self.assertEqual(result["pending_sources"][0]["filename"], "999999 - Tracking test.pdf")
        self.assertEqual(result["pending_sources"][0]["status"], "pending")

    def test_wrong_source_order(self):
        sources = self.manifest["sources"]
        sources[0], sources[1] = sources[1], sources[0]
        self.save()
        self.assert_error("PDF source order")

    def test_missing_asset(self):
        next((self.root / "assets").rglob("*.png")).unlink()
        self.assert_error("Missing inclusion/asset")

    def test_stale_build(self):
        page = self.root / "lectures/01/page-001.tex"
        page.write_text(page.read_text() + "\n% modified after review\n")
        self.assert_error("changed since the verified build")

    def test_compile_sources_do_not_require_originals(self):
        shutil.rmtree(self.root / "pdf-prof")
        self.assertEqual(validate(self.root)["errors"], [])


if __name__ == "__main__":
    unittest.main()
