---
name: word-report-builder
description: 将 Markdown 工程原稿独立生成为原生可编辑公式 DOCX，处理 Word 排版、表格、单位、示意图文字化和文档检查；不生成语音。
metadata:
  version: "1.0.0"
---

# 独立 Word 报告

只处理用户请求的 Word 输出。读取原始 Markdown，保留数学和工程内容；
原生公式使用 Pandoc，依赖或公式不支持时保留已有文件并报告失败。
不要为排版顺带生成或替换 MP3。

入口为本技能 `scripts/build.py`：

```text
python scripts/build.py --input SOURCE.md --output REPORT.docx --title 标题
```

Windows 使用 `C:/Python314/python.exe`；Word 默认交付目录为 `D:/IDM下载`，
当前用户指定位置优先。ARM 使用已安装的 Python 3 和宿主媒体目录。
模板可传 `--reference-doc`，Pandoc 可传 `--pandoc`。只在明确要求时选
`--engine legacy`，不自动降级。维护测试或明确仅本地输出加 `--no-cloud-archive`。

检查标题、正文结尾、全部表格及公式，读取本次 `.briefing` 诊断：
特别检查 `ASCII_SCHEMATIC_NORMALIZED`、未识别代码/示意图和原始 LaTeX。
示意图转文字需保留尺寸、材料、警示和重复构件，不能全局删除减号。
复杂版式交付前在目标客户端或渲染预览检查；技术成功不代表视觉或工程验收。
不因本任务安装依赖或更改云盘认证。

本技能通过同级 `docx-speech-briefing-builder` 的独立 Word API 运行，
共用解析和缓存，不复制引擎。需要格式支持细节时，读取该核心的
`docs/v2-engine.md`；宿主归档细节见 `references/host-workflow.md`。
宿主按既有约定冻结原稿和 Word 并备份；单独 Word 尚不能提交完整校核视频。

用户同时要求语音时，由 `speech-narration-builder` 处理同一原稿，复用同一
中文 basename。两项都已验证后宿主才配对入队。Telegram 发送交给现有交付
技能；本技能不发送附件、不标记人工验收、不另行启动视频。
