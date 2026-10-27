# v2.0.2 — engineering speech and Word compatibility

Engineering reports containing angle superscripts such as `45^\circ` or
temperatures with LaTeX spacing could fail before speech synthesis started.
The structured speech parser now handles these forms, temperatures embedded in
larger expressions, and star superscripts. It distinguishes function
composition, ordinary powers, units and unary negative temperatures. Unknown
or ambiguous structures continue to fail explicitly and preserve existing audio.

Native Word builds now set modern Word compatibility mode and expose the mode in
their diagnostic record. Formulas remain native, editable Word math; the change
does not restructure paragraphs or convert formulas to images. The old-format
prompt was resolved on the tested Android device. That device's Word Mobile
View still stretched a complex equation, while the user's vivo document reader
displayed the native formula correctly in both views; other clients require
their own visual review.

The Windows and ARM workflows continue to use the shared Pandoc engine and
separate Word/audio phases, caches and delivery records. The patch does not
change schedules or automatically resend past reports. Build success, media
decoding, manual listening, visual review and engineering acceptance remain
distinct checks. Private reports and generated files are not included in this
repository or release archive.
