#!/usr/bin/env python3
"""Record a successful build after manually reviewing page transcription statuses."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from validate_sources import input_digest, sha256, validate

root = Path(__file__).resolve().parents[1]
result = validate(root, require_sources=True, check_build=False)
if result["errors"]:
    sys.exit("\n".join(result["errors"]))
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
manifest["verification"] = {
    "build_succeeded": True,
    "build_command": "latexmk -pdf -outdir=build main.tex",
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    "compiled_pdf": "build/main.pdf",
    "compiled_pdf_sha256": sha256(pdf),
    "compiled_page_count": int(match[1]),
    "inputs_sha256": input_digest(root),
    "review_method": "Visual inspection of every source page and rendered notes; retained crops checked with their surrounding text."
}
for source in manifest["sources"]:
    source["status"] = "complete" if all(p["status"] == "visually_verified" for p in source["pages"]) else "in_progress"
path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print("Recorded successful build; page statuses were left as manually reviewed.")
