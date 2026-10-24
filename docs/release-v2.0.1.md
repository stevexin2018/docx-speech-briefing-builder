# v2.0.1 — native v2 by default

Ordinary Word generation previously still selected the compatibility renderer
unless a caller opted into v2. All direct Word CLI and Python APIs now default
to Pandoc, including the concurrent builder and worker API. The cached entry
`trial_briefing.py` keeps its filename and existing native default. Explicit
`--engine legacy` remains available. Missing dependencies and unsupported math
fail clearly without implicit engine fallback or replacement of prior outputs.

## Host migration

The Windows skill guide and ARM adapters use the native shared implementation
for ordinary calls. ARM report/early-news workflows select the shared cached
builder by default. The ASME scheduled pipeline uses the same builder for its
separate Word and audio phases, preserving delivery-history reconciliation,
learning progress and its Word-first behavior.

Unsent assets are checked against current source, engine and code fingerprints.
Confirmed deliveries remain historical records and are not rebuilt or resent
solely because software changed. Schedules, recipients, model configuration and
external publication behavior are unchanged by this migration. Host-specific
adapters are maintained separately and are not bundled in this source archive.

Human page review, listening and engineering acceptance remain independent of
technical build success. The v2.0.0 tag is retained unchanged for reproducibility.
