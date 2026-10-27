# Word mobile compatibility candidate

## Device feedback on 2026-10-27

The user confirmed that the old-format prompt disappeared, while the equation
still stretched in Mobile View. Treat compatibility settings as verified for
this report/device, and the native-equation reflow attempt as failed. The user
reported vivo X200s, Android 16, OriginOS 6 and Microsoft Word
16.0.20228.20090. Do not generalize this result to every mobile client.

The minimal file-format fix is isolated on `fix/word-modern-format`; it changes
only the compatibility setting and its diagnostic field. It does not include
the experimental math defaults or paragraph transformations in this branch.

The layout transformations below remain experimental and must not be merged as
a proven Mobile View fix. The next local comparison uses a separate reading
copy with four display equations rendered as fixed-aspect-ratio PNGs; the master
retains editable native equations. This Windows Word rendering experiment is
not yet a portable Windows/ARM rendering feature or a default output policy.

Some generated DOCX files omit an explicit Word compatibility mode. Desktop
Word can identify those documents as Word 2007 mode even though the file uses
the `.docx` extension. On a phone, the old-format upgrade prompt and the mobile
view's equation layout must be tested separately: correct print layout does
not establish correct narrow-screen reflow.

## Candidate behavior

The native Word enhancement pass writes `compatibilityMode=15` (Word 2013 and
later). It fills missing document math defaults, including Cambria Math and
zero wrap indentation, without replacing explicit custom math settings.
This does not change the OOXML namespaces or convert formulas into images.

Safe body paragraphs receive these layout adjustments:

- Standalone tall inline equations become native display equations. Equations
  within ordinary prose or table cells stay inline.
- Display equations and adjacent prose use separate paragraphs. Equation line
  spacing expands automatically for fractions, radicals and delimiters.
- Recognized trailing review labels such as `【待核验】` and
  `【待核验公式模型】` move outside the equation only when they consist of
  complete top-level math runs. Their text remains beside the formula in the
  following paragraph. Mixed mathematical runs and algebraic placeholders are
  left intact.

Numbered paragraphs, headings, section breaks, bookmarks, fields and content
controls are excluded from paragraph restructuring. Fractions, roots, matrices,
delimiters, scripts and other mathematical nodes are not rebuilt or simplified.

The Word diagnostic report adds `word_layout` with compatibility mode and counts
of display paragraphs, promoted inline equations, separated mixed paragraphs
and moved status annotations. Existing code fingerprints distinguish candidate
Word caches; audio content and cache policy are unchanged.

## Real-device acceptance

Use copies of the same affected report to isolate the causes:

1. **A: compatibility only.** Change only the compatibility setting. Check
   whether the old-format prompt disappears. A separate attachment/save-copy
   prompt is not evidence of an old file format.
2. **B: compatibility and equation layout.** Apply the full candidate pass.
   Compare the affected formula in both Print Layout and Mobile View. Verify
   readable text, fraction/delimiter proportions, labels and nearby tables.

Keep the original report unchanged. Compare mathematical content and document
text, and inspect desktop pagination before sharing the copies. A successful
build, XML check or desktop render must not mark mobile visual acceptance as
passed. Record the phone OS and Word version when collecting results.

The candidate stays separate from the stable branch and Windows/ARM production
installation until real-device results are known. If Mobile View still stretches
the equation, retain that failed result and decide on a separate mobile reading
output; do not flatten the editable master or claim the issue is resolved.

Private reports, comparison DOCX files and render artifacts are not repository
fixtures. Tests in `tests/test_word_mobile_compatibility.py` use minimal synthetic
content and cover math preservation, custom settings, conservative exclusions,
idempotence and the native build integration.
