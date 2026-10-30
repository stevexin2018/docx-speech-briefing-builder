# v2.0.3 — section sketches and engineering narration

This patch addresses issues found during manual review of a daily engineering
report. It still produces one DOCX with editable native equations and one MP3.

- Labelled ASCII section sketches become readable Word paragraphs and speech.
  Decorative single and double rules are removed; layer descriptions remain.
  Other code blocks retain their literal content.
- Subscript identifiers such as `W_{m2}` no longer gain an implied multiplication
  before the digit. Diameter dimensions, text units, roughness ranges and
  micrometers receive context-aware narration. Actual formula multiplication is
  preserved.
- Numeric inch quotation marks inside math, such as `$\le 2.5"$`, become
  explicit inch units before DOCX conversion. The same expression is spoken as
  "小于等于二点五英寸".
- Both asset cache keys include the shared sketch parser.

The source reports used for validation remain private and are not included in
the release. Technical build checks do not replace visual or listening review.
