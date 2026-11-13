---
name: speech-narration-builder
description: 独立预检工程原稿的朗读文本并生成正常语速 MP3，处理公式、下标、数值单位、网址及绘图符号的读法；不生成或修改 Word。
metadata:
  version: "1.1.0"
---

# 独立语音预处理与 MP3

以原始 Markdown 为语音来源，优先使用生成 Word 时的同一份冻结原稿。
只处理用户请求的音频，不为朗读重新排版或覆盖 Word。需要 Word 时交给
`word-report-builder`；不要从校核视频的识别字幕反推原稿。

先使用本技能入口预检，无需 TTS 或 Pandoc：

```text
python scripts/build.py --input SOURCE.md --preview
```

核对正文覆盖及可疑片段：绘图边框不能成为重复加减号；网址分隔符自然停顿，
不读连接号或下划线；简单下标短停顿，复杂数学保留必要边界；数值与单位相连。
保留有意义的减法、负号、标准号和尺寸，不全局删标点。
预检发现未处理的绘图线会阻止 TTS；改成清晰文字说明后再生成。
`--allow-literal-code` 只用于明确需要逐字读代码的情况。

```text
python scripts/build.py --input SOURCE.md --output REPORT.mp3 --voice zh-CN-XiaoxiaoNeural --rate +0%
```

Windows 使用 `C:/Python314/python.exe`；MP3 默认交付到 `D:/IDM下载`，
当前用户指定位置优先。ARM 使用已安装的 Python 3 和宿主媒体目录。
默认正常语速晓晓；用户明确指定其他音色或语速时遵从，不自动替换服务。
维护测试或明确仅本地输出加 `--no-cloud-archive`。

检查本次记录的 `rebuilt/reused`、语音代码指纹、请求音色语速和失败信息，
并用 ffprobe/完整解码验证音频。文字预检和解码不等于人工试听；
保持 listening 未验收，不编造已通过。旧 MP3 不会因更新自动改变；
重新生成后校核视频必须绑定新音频，不能沿用旧录音或旧时间轴。

本技能通过同级 `docx-speech-briefing-builder` 的独立语音 API 运行，
共享数学解析和音频缓存，不复制引擎；音频单独失败可重试，保留已有 Word。
宿主按既有约定备份，并在同源 Word/MP3 齐备后自动提交校核视频。
Telegram 发送交给现有交付技能；本技能不发消息、不重新渲染视频。


## 智能混合公式朗读（1.1.0）
默认 --math-mode smart：简单下标短停顿，复杂下标首次明确读“下标”、
重复时在明确可读条件下简化；纯整数分式使用“分之”表达。
--math-mode strict 可强制所有下标显式读出。先用
python scripts/build.py --input SOURCE.md --preview --math-mode smart
检查全部公式，再按同一模式生成 MP3。短停顿是标点语气，实际时长随 TTS 不同。
不要修改 Word 原公式，不要自动重新生成或覆盖已有 MP3。
