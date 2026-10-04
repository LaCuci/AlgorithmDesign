#!/usr/bin/env python3
"""Scaffold a newly discovered PDF without marking any content transcribed."""
import argparse
import json
from pathlib import Path
import re
import sys
from validate_sources import filename_key, sha256

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("filename", help="Exact PDF filename inside pdf-prof")
parser.add_argument("--pages", type=int, required=True, help="Visually confirmed source page count")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
if Path(args.filename).name != args.filename or args.pages < 1:
    sys.exit("Supply a PDF basename and a positive page count")
pdf = root / "pdf-prof" / args.filename
match = re.match(r"(\d+)", args.filename)
if not pdf.is_file() or pdf.suffix.lower() != ".pdf" or not match:
    sys.exit("PDF must exist in pdf-prof and have a numerical filename prefix")
lecture_id = match[1]
path = root / "sources.json"
manifest = json.loads(path.read_text())
if any(s["filename"] == args.filename or s["id"] == lecture_id for s in manifest["sources"]):
    sys.exit("PDF filename or lecture ID already recorded")
folder = root / "lectures" / lecture_id
if folder.exists():
    sys.exit("Lecture folder already exists; refusing to overwrite it")
main_path = root / "main.tex"
main = main_path.read_text()
block = re.search(r"(?:\\input\{lectures/[^}]+\}\s*)+", main)
if not block:
    sys.exit("Cannot locate the explicit lecture inclusion block in main.tex")
folder.mkdir(parents=True)
pages = []
for number in range(1, args.pages + 1):
    relative = f"lectures/{lecture_id}/page-{number:03}.tex"
    (root / relative).write_text(f"% Source: {args.filename}, page {number}.\n"
                                 f"\\sourcepage{{{lecture_id}}}{{{number}}}\n"
                                 "% PENDING: visually inspect and transcribe all source content here.\n")
    pages.append({"page": number, "tex_file": relative, "status": "pending",
                  "content_kind": "substantive", "assets": [], "review_notes": []})
escapes = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "%": r"\%",
           "&": r"\&", "#": r"\#", "_": r"\_", "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
bookmark = "".join(escapes.get(c, c) for c in args.filename)
wrapper = f"% Source: {args.filename}\n\\pdfbookmark[0]{{{bookmark}}}{{lecture-{lecture_id}}}\n"
wrapper += "".join("\\input{" + p["tex_file"][:-4] + "}\n" for p in pages)
(folder / "lecture.tex").write_text(wrapper)
manifest["sources"].append({"id": lecture_id, "filename": args.filename, "sha256": sha256(pdf),
                             "page_count": args.pages, "lecture_file": f"lectures/{lecture_id}/lecture.tex",
                             "status": "pending", "pages": pages})
manifest["sources"].sort(key=lambda s: filename_key(s["filename"]))
includes = "".join("\\input{" + s["lecture_file"][:-4] + "}\n" for s in manifest["sources"])
main_path.write_text(main[:block.start()] + includes + main[block.end():])
path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print(f"Added lecture {lecture_id}: {args.pages} pending pages. Transcribe, review, compile, then record the build.")
