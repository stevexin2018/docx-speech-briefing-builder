---
name: docx-speech-briefing-builder
description: Word 与语音旧调用的兼容协调入口；Word 排版交给 word-report-builder，朗读预处理及 MP3 交给 speech-narration-builder。共享核心解析、缓存和宿主归档。
metadata:
  version: "2.0.5"
  updated: "2026-11-13"
---

# Word 与语音的兼容协调入口

按用户要求的输出选择独立技能：

- 只要 Word：读取同级 `word-report-builder/SKILL.md`，调用其
  `scripts/build.py --input SOURCE.md --output REPORT.docx`。
- 只要语音：读取同级 `speech-narration-builder/SKILL.md`，先预检朗读文本，
  再调用其 `scripts/build.py --input SOURCE.md --output REPORT.mp3`。
- 同时要 Word 和语音：两项分别处理同一份已冻结原稿，各自生成、缓存、记录和验收；
  两项成功后由宿主按原稿身份配对。语音失败保留 Word，禁止拿旧 MP3 凑配。

同级技能目录位于本技能目录的父目录，不是本仓库内的子目录。公共 Python
解析模块继续在本 Git 仓库维护，避免两个技能各自复制并修补同一套公式规则。
新入口分别为 `word_report.py`、`speech_narration.py`；可独立使用 CLI 或
`briefing_products.build_word_report` / `build_speech_audio` API。
纯核心入口默认不联网归档；已安装独立技能的宿主脚本按既有约定归档。

旧 `trial_briefing.py`、`build_briefing.py`、`render_docx.py`、
`clean_speech_text.py`、`references/host_briefing.py` 的 CLI/API 继续兼容，
不批量重生成、不重新发送已有附件。旧用法见
[兼容工作流](docs/combined-compatibility.md)。仅在维护旧调用时读取它；
日常新请求使用独立技能。

Word、语音成功不等于人工排版验收、试听或工程合规确认。视频制作复用既有
Word 和音频，不重新 TTS。Telegram 交付遵循 `telegram-briefing-delivery`，
视频由原机器人绑定的统一队列异步处理；不要通过另一个规划 Agent 转发。

Windows 的核心和交付位置见现有
[宿主说明](references/codex-shared-usage.md)；ARM 不硬编码 Windows 路径。
记录中的语音代码指纹会使旧读法缓存失效，但不会自动修改已经交付的 MP3。
