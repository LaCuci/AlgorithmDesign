# Source transcription review notes

These editorial tracking notes are not included in the lecture PDF. The lecture content contains only material from the supplied PDFs. The title page and table of contents are separately requested editorial front matter.

## Retained unresolved handwriting

| Source | Page | Fragment | Treatment |
| --- | ---: | --- | --- |
| `03 - Wed Sep 30 2026.pdf` | 1 | Short red handwritten symbol immediately before “Formal languages” in the recap | Retained inline as `assets/03/page-001-formal-language-symbol.png`; no mathematical interpretation or replacement was supplied. |
| `09 - Wed Oct 15 2025.pdf` | 6 | Circled handwritten asymptotic symbol before the clique approximation expression `(|V|^(1−ε))` | Retained inline as `assets/09/page-006-asymptotic-symbol.png`; its textual interpretation remains unresolved. The source attribution “Arora et al. 1990” is retained as written. |

These fragments remain open for a future textual reading. Their source placements and appearances have been visually checked; retaining the original makes the page fully accounted for without guessing.

## Page accounting and continuations

- All thirteen source PDFs have page coverage recorded individually in `sources.json`: 15, 19, 13, 15, 12, 21, 6, 10, 15, 13, 17, 12, 16 pages (184 total).
- Lecture 06 pages 16–19 have no extractable text. Their subset-sum proof and examples were transcribed from the visible handwriting, including the repeated example and column sums.
- Lecture 06 page 20 contains a trailing closing parenthesis and box borders. The parenthesis is retained immediately after page 19's content, without a forced page break.
- Lecture 06 page 21 contains box borders and a tiny isolated ink stroke, with no substantive content. It has a page file, source label and verified record, without blank-page filler.
- Sentence and proof continuations are recorded where source pages divide a passage. In particular, lecture 01 page 12 and lecture 06 pages 6, 19 and 20 use inline source markers.

## Faithfulness and figures

Apparent source errors, inconsistent indices, repetitions, original exercise prompts and administrative information are retained. The lecture text adds no corrections, explanations or external material. Source notation is transcribed where readable. Diagrams and their labels are source-derived crops; adjacent annotation relationships are retained with their corresponding diagrams or typeset text. Where a neighboring line intrudes into a diagram's rectangle, its separately transcribed lettering is excluded from the asset; the exact excluded regions are recorded in the crop provenance.

The supplied source pages and rendered notes were visually reviewed. Integrity checks and compilation evidence are recorded separately in `sources.json`; the validator verifies structural coverage and file integrity, not the semantic accuracy of handwriting recognition.

## Added sources 07a–09

- Lecture 07a repeats the subset-sum construction and proof; the repetition is retained. Pages 5 and 6 continue the example and proof from the preceding source pages. The digit construction is an original crop, and the numerical example is an editable table.
- Lecture 07b pages 2, 5, 7 and 9 contain ruled answer space only. Lecture 08 pages 2, 3, 6, 7, 8, 10, 11, 13 and 14 contain no substantive content; page 6 has a tiny isolated red ink stroke. All thirteen pages have source labels and contentless records. No solutions are added.
- Lecture 08 page 4 quantifies the dominating-set definition over `V′` in the original. This apparent error is preserved. Its graph annotations and the class diagram on page 1 are retained as crops.
- Lecture 09 page 12 repeats the selected-edge annotation `{e,f}` at the third graph state, although the highlighted edge is `{d,g}`. The original crop preserves both the annotation and graph. Page 13's maximal-matching quantification is retained exactly as written.
- The source filenames, including their original dates and the `07a`/`07b` suffixes, are unchanged. New source pages were inspected from Poppler renders; all 44 added source pages were compared with the compiled notes and marked visually verified, including source labels for the contentless pages. Earlier source review records are retained from the previous conversion because those original PDFs are currently absent.

The final integrity check also found three already-recorded assets omitted from the existing LaTeX: the lecture 03 page 1 symbol and the two lecture 04 page 7 verifier examples. Their inclusions were restored and the affected output pages inspected. Crop exclusions for the additions are recorded in `sources.json`; two small regions use a recorded blue-ink mask to remove adjacent prose while retaining overlapping diagram labels.

## Document front matter

A title page and linked table of contents were added at the user's request. The contents group entries by lecture and use descriptive labels for exercises. The printed lecture text and headings are unchanged, and lecture pagination starts at 1 after the Roman-numbered contents.

## Added sources 10–12

- Added 45 source pages: lesson 10 has 17, lesson 11 has 12, and lesson 12 has 16. Lesson 10 page 17 and lesson 11 page 12 are blank; their source markers and contentless records are retained without adding blank output pages.
- All handwritten prose, formulas, proofs, algorithm instructions and recaps were inspected from Poppler source renders. Thirty-three source-derived diagram crops preserve graph geometry, weights, labels, highlighted choices and arrows. Adjacent prose is transcribed separately; exclusions and selective ink masks are recorded with each crop. The spliced-cycle sequences (lesson 12 page 9) and the shortcut example sequences (lesson 12 page 15) are editable beside their graph crops.
- The source's apparent errors are retained. Examples include the `w'(v')` term in lesson 10 page 10, the `e` not in `E'` assertion in lesson 11 page 5, the inconsistent `K` arguments in lesson 11 page 6, and the `c(T*)` denominator in the intermediate approximation bound on lesson 12 page 5. The clique hardness attribution on lesson 10 page 4 remains “Feige et al. 1991.” These are transcription observations, not corrections to the lecture.
- Lesson 11 pages 10–11 continue the full-preorder-walk definition across page files, with its source anchor retained inside the definition box. Proofs and derivations continue in source order; the repeated recaps and examples in lesson 12 are preserved.
- No new handwriting fragment required an unresolved textual reading. Original filenames and dates, including `10 -Mon Oct 19 2026.pdf`, are unchanged.
- The new source pages and their rendered LaTeX were visually compared, including the formulas, pseudocode, diagrams and the two contentless pages. Earlier source verification states are preserved because the first six original PDFs are absent. The older three recorded-but-omitted asset inclusions described above were restored and their rendered placement checked again.
