# Independent Word and speech products

`word-report-builder` owns DOCX layout and document checks.
`speech-narration-builder` owns expected-reading preflight and MP3 checks.
Both use this repository's parser and cache rather than maintaining divergent
copies. The original combined skill is a compatibility coordinator.

Core CLI entries are format-specific and local-only unless `--cloud-archive`
is explicitly provided:

```text
python word_report.py --input report.md --output report.docx
python speech_narration.py --input report.md --preview
python speech_narration.py --input report.md --output report.mp3
```

The Word entry has no voice/rate options. The speech entry has no Word/template
options and does not need Pandoc. Speech preflight blocks leftover drawing
borders before TTS; explicitly literal code narration can use
`--allow-literal-code`. This is not proof of complete spoken correctness.
The existing combined CLI/API interfaces remain supported.

Python hosts can use `briefing_products.build_word_report` and
`build_speech_audio`. Host adapters opt into existing archival with
`cloud_archive=True`; each successful phase is frozen independently.
No alternate voice/service is selected automatically. Technical and manual
acceptance remain separate. An audio failure leaves an existing Word untouched.

Skill distribution templates are versioned under `skill-distribution/`, using
non-discoverable filenames to avoid duplicate nested skill discovery. Export:

```text
python tools/export_product_skills.py --output /task/staging
```

Publish those two staged folders through the host's shared skill manager.
The installed launchers find the single sibling core and enable that host's
existing archival by default; `--no-cloud-archive` is for local-only work/tests.
Do not copy models, credentials, reports, or caches into a skill package.

The ASME daily host pipeline keeps Word at 08:00 and speech at 08:20. Its
source directory needs an explicit origin rule for the original Telegram bot.
The verified audio phase completes the Word/audio pair and can then submit a
review video. A `queued_not_yet_verified` archive receipt is not completed video
delivery. Rendering, cloud validation and original-bot delivery remain the video
worker's responsibility, and reuse the exact MP3 rather than synthesizing it.
