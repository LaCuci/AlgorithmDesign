#!/usr/bin/env python3
"""Validate ordered PDF coverage, LaTeX inclusions, assets and build evidence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

STATUSES = {"pending", "transcribed", "visually_verified"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def filename_key(name):
    match = re.match(r"(\d+)", name)
    return (int(match[1]) if match else sys.maxsize, name)


def tex_text(path):
    return re.sub(r"(?<!\\)%[^\n]*", "", path.read_text())


def inclusions(path):
    return re.findall(r"\\input\{([^}]+)\}", tex_text(path))


def tex_path(name):
    return name if name.endswith(".tex") else name + ".tex"


def input_digest(root):
    """Bind compilation evidence to every typeset source and stored asset."""
    paths = [root / "main.tex"]
    paths += list((root / "tex").rglob("*.tex"))
    paths += list((root / "lectures").rglob("*.tex"))
    paths += [p for p in (root / "assets").rglob("*") if p.is_file()]
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def validate(root, require_sources=False, check_build=True):
    root = Path(root).resolve()
    errors, warnings, pending = [], [], []

    def error(message):
        errors.append(message)

    def checked_path(value):
        if not isinstance(value, str) or not value:
            error(f"Invalid inclusion/asset path: {value!r}")
            return None
        path = root / value
        if Path(value).is_absolute() or not path.resolve().is_relative_to(root):
            error(f"Path escapes project: {value}")
            return None
        if not path.is_file():
            error(f"Missing inclusion/asset: {value}")
            return None
        return path

    try:
        manifest = json.loads((root / "sources.json").read_text())
    except (OSError, ValueError) as exc:
        return {"errors": [f"Cannot read sources.json: {exc}"], "warnings": [], "pending_sources": []}
    sources = manifest.get("sources", [])
    if manifest.get("schema_version") != 1 or not isinstance(sources, list) or not sources:
        return {"errors": ["Invalid or empty ordered source record"], "warnings": [], "pending_sources": []}
    names = [s.get("filename", "") for s in sources]
    ids = [s.get("id", "") for s in sources]
    lectures = [s.get("lecture_file", "") for s in sources]
    for label, values in [("PDF", names), ("lecture ID", ids), ("lecture inclusion", lectures)]:
        for value, count in Counter(values).items():
            if count > 1:
                error(f"Duplicate {label}: {value}")
    if names != sorted(names, key=filename_key):
        error("PDF source order is not numerical filename order")
    main = checked_path("main.tex")
    if main:
        actual = [tex_path(p) for p in inclusions(main) if p.startswith("lectures/")]
        if actual != lectures:
            error("main.tex lecture inclusion order/coverage differs from sources.json")
    all_page_files, all_assets = [], []
    total = 0
    for source in sources:
        name, lecture_id = source.get("filename", ""), source.get("id", "")
        count = source.get("page_count")
        pages = source.get("pages", [])
        if not isinstance(count, int) or isinstance(count, bool) or count < 1 or not isinstance(pages, list):
            error(f"Invalid page inventory: {name}")
            continue
        total += count
        numbers = [p.get("page") for p in pages]
        if numbers != list(range(1, count + 1)):
            error(f"Page coverage/order mismatch: {name}; expected 1–{count}, got {numbers}")
        if len(numbers) != len(set(numbers)):
            error(f"Duplicate page entry: {name}")
        if source.get("status") not in {"pending", "in_progress", "complete"}:
            error(f"Invalid PDF status: {name}")
        if source.get("status") == "complete" and any(p.get("status") != "visually_verified" for p in pages):
            error(f"Complete PDF has unverified pages: {name}")
        original = root / "pdf-prof" / name
        if Path(name).name != name or not name.lower().endswith(".pdf"):
            error(f"Invalid PDF filename: {name}")
        elif original.is_file():
            if sha256(original) != source.get("sha256"):
                error(f"Source checksum changed: {name}")
            # The supplied PDFs expose page objects directly. Object-stream PDFs
            # still have their exact bytes checked, but require visual inventory.
            data = original.read_bytes()
            observed = len(re.findall(rb"/Type\s*/Page\b", data))
            if b"/ObjStm" not in data and observed:
                if observed != count:
                    error(f"Source page count differs: {name}; {observed} != {count}")
            else:
                warnings.append(f"PDF page count requires external/visual inspection: {name}")
        elif require_sources:
            error(f"Missing original PDF: {name}")
        else:
            warnings.append(f"Original absent; checksum check skipped: {name}")
        if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
            error(f"Invalid SHA-256 record: {name}")
        lecture = checked_path(source.get("lecture_file"))
        page_files = [p.get("tex_file", "") for p in pages]
        all_page_files += page_files
        if lecture and [tex_path(p) for p in inclusions(lecture)] != page_files:
            error(f"Lecture page inclusion order/coverage mismatch: {name}")
        for page in pages:
            number = page.get("page")
            if page.get("status") not in STATUSES:
                error(f"Invalid page status: {name} p{number}")
            if page.get("content_kind") not in {"substantive", "continuation", "contentless"}:
                error(f"Invalid content kind: {name} p{number}")
            path = checked_path(page.get("tex_file"))
            used_assets = []
            if path:
                contents = tex_text(path)
                labels = re.findall(r"\\source(?:page|continuation)\{([^}]+)\}\{(\d+)\}", contents)
                if labels != [(lecture_id, str(number))]:
                    error(f"Source-page label mismatch: {name} p{number}")
                used_assets = re.findall(r"\\(?:sourcefigure|includegraphics)(?:\[[^\]]*\])?\{([^}]+)\}", contents)
                for asset in used_assets:
                    checked_path(asset)
            recorded_assets = []
            for asset in page.get("assets", []):
                recorded_assets.append(asset.get("path", ""))
                checked_path(asset.get("path"))
                if asset.get("kind") not in {"diagram", "unreadable"}:
                    error(f"Invalid crop kind: {name} p{number}")
                if asset.get("lecture") != lecture_id or asset.get("page") != number:
                    error(f"Crop provenance mismatch: {name} p{number}")
            all_assets += recorded_assets
            if Counter(used_assets) != Counter(recorded_assets):
                error(f"Asset tracking differs from LaTeX: {name} p{number}")
    if len(all_page_files) != len(set(all_page_files)):
        error("Duplicate page inclusion paths")
    disk_pages = {p.relative_to(root).as_posix() for p in (root / "lectures").rglob("page-*.tex")}
    if disk_pages != set(all_page_files):
        error("Unrecorded or missing page-level LaTeX files")
    disk_assets = {p.relative_to(root).as_posix() for p in (root / "assets").rglob("*") if p.is_file()}
    if disk_assets != set(all_assets):
        error("Unrecorded or missing source assets")
    for original in sorted((root / "pdf-prof").glob("*"), key=lambda p: filename_key(p.name)):
        if original.is_file() and original.suffix.lower() == ".pdf" and original.name not in names:
            pending.append({"filename": original.name, "sha256": sha256(original), "status": "pending"})
    if pending:
        error("Unrecorded PDFs discovered; pending insertion")
    if check_build and any(s.get("status") == "complete" for s in sources):
        evidence = manifest.get("verification", {})
        if evidence.get("build_succeeded") is not True:
            error("Completed sources lack successful compilation evidence")
        if evidence.get("inputs_sha256") != input_digest(root):
            error("LaTeX/assets changed since the verified build; compile and review again")
        pdf = root / "build/main.pdf"
        if pdf.is_file():
            if sha256(pdf) != evidence.get("compiled_pdf_sha256"):
                error("Compiled PDF differs from the verified build")
        else:
            warnings.append("Compiled PDF absent; stored build evidence checked, rebuild locally")
    return {"errors": errors, "warnings": warnings, "pending_sources": pending,
            "pdf_count": len(sources), "source_pages": total,
            "visually_verified_pages": sum(p.get("status") == "visually_verified" for s in sources for p in s.get("pages", []))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-sources", action="store_true")
    parser.add_argument("--skip-build", action="store_true", help="Validate an unfinished project before recording a build")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.root, args.require_sources, not args.skip_build)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, prefix in [("errors", "ERROR"), ("warnings", "NOTE")]:
            for message in result[key]:
                print(f"{prefix}: {message}")
        for source in result["pending_sources"]:
            print(f"PENDING: {source['filename']}")
        if not result["errors"]:
            print(f"OK: {result['pdf_count']} PDFs; {result['source_pages']} source pages; "
                  f"{result['visually_verified_pages']} visually verified")
    return bool(result["errors"])


if __name__ == "__main__":
    sys.exit(main())
