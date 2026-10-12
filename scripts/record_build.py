#!/usr/bin/env python3
"""Record a successful build after manually reviewing page transcription statuses."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import re
import sys
from validate_sources import input_digest, sha256, validate

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--require-sources", action="store_true", help="Require every original PDF to be present")
args = parser.parse_args()
result = validate(root, require_sources=args.require_sources, check_build=False)
if result["errors"]:
    sys.exit("\n".join(result["errors"]))
for warning in result["warnings"]:
    print(f"NOTE: {warning}")
log = (root / "build/main.log").read_text()
match = re.search(r"Output written on .*?\((\d+) pages?,", log)
if not match or re.search(r"Overfull|undefined references|LaTeX Error|Emergency stop|Fatal error", log, re.I):
    sys.exit("Build missing or contains unresolved errors/clipped boxes; compile and inspect first")
pdf = root / "build/main.pdf"
if not pdf.is_file():
    sys.exit("Missing build/main.pdf")
# A build's recorder must include all inputs, and the output must be current.
inputs = [root / "main.tex"] + list((root / "tex").rglob("*.tex")) + list((root / "lectures").rglob("*.tex"))
inputs += [p for p in (root / "assets").rglob("*") if p.is_file()]
recorder = (root / "build/main.fls").read_text()
recorded_inputs = {(root / name).resolve() for name in re.findall(r"^INPUT (.+)$", recorder, re.M)}
if any(p.resolve() not in recorded_inputs for p in inputs):
    sys.exit("Compilation recorder does not include every tracked typeset input")
if any(p.stat().st_mtime > pdf.stat().st_mtime for p in inputs):
    sys.exit("Typeset inputs changed after compilation; rebuild first")
path = root / "sources.json"
manifest = json.loads(path.read_text())
available_sources = [s["filename"] for s in manifest["sources"]
                     if (root / "pdf-prof" / s["filename"]).is_file()]
absent_sources = [s["filename"] for s in manifest["sources"]
                  if s["filename"] not in available_sources]
manifest["verification"] = {
    "build_succeeded": True,
    "build_command": "latexmk -pdf -outdir=build main.tex",
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    "compiled_pdf": "build/main.pdf",
    "compiled_pdf_sha256": sha256(pdf),
    "compiled_page_count": int(match[1]),
    "inputs_sha256": input_digest(root),
    "review_method": "Visual inspection of available source pages and rendered notes; retained crops checked with their surrounding text. Earlier review states are preserved when originals are absent.",
    "available_originals": available_sources,
    "absent_originals": absent_sources
}
for source in manifest["sources"]:
    source["status"] = "complete" if all(p["status"] == "visually_verified" for p in source["pages"]) else "in_progress"
path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print("Recorded successful build; page statuses were left as manually reviewed.")
