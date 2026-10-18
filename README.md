# Advanced Algorithm Design lecture notes

Editable transcription of thirteen source PDFs, in numerical filename order. All 184 source pages are accounted for: **15, 19, 13, 15, 12, 21, 6, 10, 15, 13, 17, 12, 16**. The document uses continuous 11-point A4 typesetting, the existing lecture headings and filename bookmarks, plus an added title page and linked table of contents. The contents use Roman page numbers; lecture notes start at Arabic page 1. Original language, repetitions and apparent errors are retained.

## Build

From the project root, with a LaTeX installation containing `latexmk` and pdfLaTeX:

```sh
latexmk -pdf -outdir=build main.tex
python3 scripts/validate_sources.py
```

The compiled notes are **`build/main.pdf`**. A convenience copy is also available as `main.pdf`; refresh it after rebuilding with `cp build/main.pdf main.pdf`. The shared preamble lists the required packages (`lmodern`, `geometry`, AMS mathematics, `graphicx`, `xcolor`, `enumitem`, `booktabs`, `array`, `microtype`, `titlesec`, `tcolorbox` with its `breakable` and `skins` libraries, `hyperref` and their standard dependencies). No shell escape, network service, bibliography download or original PDF is needed to compile. All diagram and handwriting assets are stored in `assets`.

The original `pdf-prof/` ignore rule is retained. Build products and temporary extraction/review files are also ignored. The compiled PDF remains available locally under `build`.

## Organization

```text
main.tex                    explicit ordered lecture inclusions
tex/preamble.tex            reusable layout and source macros
tex/frontmatter.tex         title page and linked table of contents
lectures/01/lecture.tex     filename bookmark and ordered page inclusions
lectures/01/page-001.tex    editable content from one source page
lectures/02/ … 12/          same structure, including separate 07a/ and 07b/
assets/02/ … 12/           stored source-derived diagram/fragment crops
sources.json               ordered inclusion and review record
review-notes.md             retained handwriting and contentless-page notes
scripts/                   integrity, expansion and inspection helpers
tests/test_tracking.py     corruption checks in temporary copies
build/main.pdf             compiled deliverable (ignored)
```

Each page file contains an exact source-filename comment and a `source:<lecture ID>:<page>` label. `\sourcepage{01}{1}` starts a paragraph; `\sourcecontinuation{01}{12}` places the same label without breaking a continued sentence. Source page boundaries do not force output page breaks. Diagrams use nonfloating `\sourcefigure` inclusions and stay in content order.

## Formatting

The shared preamble applies muted blue headings, consistent paragraph/list/equation spacing, and `microtype` typography while retaining the 11-point A4 layout and 25 mm margins. Definitions use `notesdefinition`; theorem statements use `notestheorem`; facts, properties, corollaries and propositions use `notesresult`. These lightly shaded, unnumbered boxes preserve the existing source labels and can break across output pages. Keep each statement's formulas and conditions inside its box, with proofs and subsequent analysis following in source order.

Problem statements use `notesproblem`, which renders aligned math rows under one large left curly brace, following the source PDFs. Keep the existing instance/question labels and all input details; wrap prose in `\text{...}` and keep formulas directly in math mode. Long descriptions may continue on additional aligned rows.

Algorithms use an amber, nonfloating `notesalgorithm` box, distinct from the blue statement boxes, containing the existing name and a `notespseudocode` environment. Keep the function signature outside `notespseudocode`. Write each instruction as `\pseudocodeline{0}{...}`, using `1`, `2`, etc. for nesting. The body starts one indentation level below the signature. Lines wrap with hanging indentation; control keywords use `\textbf`. No line numbers, additional instructions or closing keywords are generated. A block may begin in one source file and end in the next when the original statement or algorithm continues; retain every intervening source anchor and comment.

Formatting does not change the transcription's wording, mathematical expressions, repetitions, apparent errors, diagrams or content order. After formatting changes, rebuild and inspect the PDF. Refresh the verified build record only when source integrity validation passes; existing tracking discrepancies must be resolved separately.

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

Added lessons `10` (17 pages), `11` (12), and `12` (16), preserving the existing statement boxes, problem braces, pseudocode and continuous layout. The 45 added pages cover approximation pitfalls, weighted vertex cover, fair pricing, LP rounding, TSP hardness, the MST approximation and Christofides' algorithm. All readable text and mathematics are editable; 33 source-derived crops retain graph geometry and attached annotations. The blank final pages of lessons 10 and 11 are recorded without inserting empty output pages. The title page and contents now include lectures 01–12.

Seven originals (`07a`–`12`) are currently present in `pdf-prof`; the earlier six lectures remain self-contained in LaTeX and assets. Validation checks all available originals and reports the missing ones. Original wording, repetitions and apparent errors are retained; see `review-notes.md` for specific review observations and the earlier unresolved symbols.

The three older asset inclusions identified in the existing review notes (lecture 03 page 1 and lecture 04 page 7) were restored to resolve the pre-existing tracking discrepancies. No earlier source text was rewritten.

The front matter is editorial material requested for this document. Contents entries group the notes by lecture and include the existing section/subsection headings; exercise prompts use descriptive navigation labels while their printed headings stay as in the source.
