# Advanced Algorithm Design lecture notes

Editable transcription of ten source PDFs, in numerical filename order. All 139 source pages are accounted for: **15, 19, 13, 15, 12, 21, 6, 10, 15, 13**. The document uses continuous 11-point A4 typesetting, the existing lecture headings and filename bookmarks, plus an added title page and linked table of contents. The contents use Roman page numbers; lecture notes start at Arabic page 1. Original language, repetitions and apparent errors are retained.

## Build

From the project root, with a LaTeX installation containing `latexmk` and pdfLaTeX:

```sh
latexmk -pdf -outdir=build main.tex
python3 scripts/validate_sources.py
```

The compiled notes are **`build/main.pdf`**. A convenience copy is also available as `main.pdf`; refresh it after rebuilding with `cp build/main.pdf main.pdf`. The shared preamble lists the required packages (`lmodern`, `geometry`, AMS mathematics, `graphicx`, `xcolor`, `enumitem`, `booktabs`, `array`, `hyperref` and their standard dependencies). No shell escape, network service, bibliography download or original PDF is needed to compile. All diagram and handwriting assets are stored in `assets`.

The original `pdf-prof/` ignore rule is retained. Build products and temporary extraction/review files are also ignored. The compiled PDF remains available locally under `build`.

## Organization

```text
main.tex                    explicit ordered lecture inclusions
tex/preamble.tex            reusable layout and source macros
tex/frontmatter.tex         title page and linked table of contents
lectures/01/lecture.tex     filename bookmark and ordered page inclusions
lectures/01/page-001.tex    editable content from one source page
lectures/02/ … 09/          same structure, including separate 07a/ and 07b/
assets/02/ … 09/           stored source-derived diagram/fragment crops
sources.json               ordered inclusion and review record
review-notes.md             retained handwriting and contentless-page notes
scripts/                   integrity, expansion and inspection helpers
tests/test_tracking.py     corruption checks in temporary copies
build/main.pdf             compiled deliverable (ignored)
```

Each page file contains an exact source-filename comment and a `source:<lecture ID>:<page>` label. `\sourcepage{01}{1}` starts a paragraph; `\sourcecontinuation{01}{12}` places the same label without breaking a continued sentence. Source page boundaries do not force output page breaks. Diagrams use nonfloating `\sourcefigure` inclusions and stay in content order.

`sources.json` records each exact PDF filename, SHA-256, page count, lecture path and every ascending source page. Page states are `pending`, `transcribed`, and `visually_verified`. PDF states are `pending`, `in_progress`, and `complete`. An unreadable fragment may be visually verified as a faithful retained crop while its textual reading remains unresolved; the separate review notes describe it. Crop records include source page, normalized top-left-origin coordinates, kind, path and any excluded adjacent lettering that is transcribed separately.

## Add another PDF

1. Put the PDF in `pdf-prof`, using a unique numerical filename prefix, for example `10 - … .pdf`. An optional letter suffix is supported, such as `07a` and `07b`. Confirm its page count visually, including pages without extractable text.
2. Scaffold the lecture and tracking records:

   ```sh
   python3 scripts/add_source.py '07 - Additional lecture.pdf' --pages 10
   python3 scripts/validate_sources.py --skip-build
   ```

   This creates one page file per source page, an ordered lecture wrapper, an ordered `main.tex` inclusion and a checksum entry. Every new page stays **pending**. Existing content is not overwritten. The previous build record becomes stale until recompilation.
3. Inspect every source page. Transcribe readable prose, equations, proofs, pseudocode, tables, examples and annotations in their source order. Keep source errors and repetitions. Use original crops for diagrams and genuinely unresolved handwriting. Account for contentless pages in comments and metadata without adding blank pages. Set `content_kind` and `continues_from` where appropriate.
4. Store crops under `assets/<ID>/`, include them at the corresponding position and add their provenance to that page's `assets` list in `sources.json`. Describe unresolved readings in `review-notes.md`. Mark pages `transcribed`, then `visually_verified` only after comparing the source with the rendered notes, including subscripts, negations, table cells and diagram labels.
5. Compile, resolve errors or clipping, and inspect the output. Then record the current build and validate:

   ```sh
   latexmk -pdf -outdir=build main.tex
   python3 scripts/record_build.py
   python3 scripts/validate_sources.py
   python3 -m unittest discover -s tests
   ```

   `record_build.py` preserves manually assigned page states; it marks a source complete only when all its pages are visually verified and a current successful build exists. Originals that are present are checksum-checked; absent originals are reported explicitly. Add `--require-sources` to both build recording and validation to require every original PDF. It stores the compiled PDF checksum and a digest of all LaTeX inputs and assets. After changing content or crops, review the affected pages, rebuild and refresh this record.

The validator checks source order, duplicate PDFs/IDs/paths/pages, complete page coverage, source labels, inclusion order, stored assets and original checksums. Unrecorded PDFs are reported as **pending** with a nonzero exit status; the validator does not silently insert them. Use `--json` for machine-readable output. Without `--require-sources`, missing originals are reported as skipped checksum checks, allowing validation of a distributed, self-contained LaTeX project. Successful build evidence is checked against current inputs; when the compiled PDF is present, its checksum is checked too. Direct page-object counts are checked for the supplied PDFs; PDFs using compressed object streams need separate visual or PDF-tool page counting.

## Optional inspection tools

On macOS, these helpers use PDFKit and AppKit. On Linux, `pdfinfo`, `pdftotext -layout` and `pdftoppm -png` (Poppler) can be used to count, extract and render PDFs for review. They are inspection aids, not build requirements:

```sh
swift scripts/extract.swift
swift scripts/render.swift build/main.pdf build/review
```

`extract.swift` renders each source page and writes extracted text into ignored `build/extraction`. Extracted text is only an aid: lecture 06 pages 16–19 have substantive handwriting with no extracted text.

With Python and Pillow installed, create a source crop using normalized coordinates:

```sh
python3 scripts/crop.py 07 1 example 0.1,0.2,0.9,0.5
```

Use `--kind unreadable --note '…'` for a retained fragment. The helper writes a stored asset and temporary provenance to `build/extraction/crops.json`; copy the relevant record into the matching page in `sources.json`. Optional `--exclude` rectangles remove adjacent lettering already transcribed elsewhere, while preserving diagram geometry and labels. Do not omit source information. Inspect each saved crop and its rendered size.

## Latest conversion

Added the four supplied sources in order: `07a` (6 pages), `07b` (10), `08` (15), and `09` (13). The repeated subset-sum proof, unsolved exercise prompts, approximation definitions, vertex-cover algorithm and graph examples are retained. Thirteen ruled answer-space pages are tracked without inserting empty output pages. The original filename dates are retained exactly, including the 2025 dates.

Only the four new originals are currently present in `pdf-prof`; the earlier six lectures remain self-contained in LaTeX and assets. Validation checks all available originals and reports the missing ones. One ambiguous handwritten asymptotic symbol in lecture 09 is retained as an inline crop; see `review-notes.md`.

The front matter is editorial material requested for this document. Contents entries group the notes by lecture and include the existing section/subsection headings; exercise prompts use descriptive navigation labels while their printed headings stay as in the source.
