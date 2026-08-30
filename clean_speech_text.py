import re

def clean_speech_text(text: str) -> str:
    """
    通用语音清洗引擎：将工程 Markdown / 特殊字符转为自然流畅、高可读性的口语文本。
    彻底杜绝 ASCII 边框线、连字符、减号被朗读为'至至至...'或'加加加...'。
    """
    if not text:
        return ""

    # 1. 预处理：行级过滤，彻底剥离 ASCII 边框线、分割线、Markdown 伪表格线
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
            
        # 过滤掉纯符号构成的分割线、装饰线、ASCII 表格边框等 (+----+----+ 或 -------------- 或 ======)
        if re.match(r'^[\-+_=\*~#|`\s]{2,}$', l):
            continue
        # 过滤 Markdown 表格对齐分割线: |:---|:---|
        if re.match(r'^\|[\s:\-\+\|=]+\|$', l):
            continue

        # 移除 Markdown 标题符 (#, ##, ### 等) 与引用/列表前缀
        l = re.sub(r'^[#>\*\-\+]+\s*', '', l)
        l = re.sub(r'^\d+[\.\)]\s*', '', l)

        # 移除纯外框的 | 符号 (如 ASCII 框里的 | 文字 |)
        l = re.sub(r'^\|\s*', '', l)
        l = re.sub(r'\s*\|$', '', l)

        # 优化标准与条款口语发音
        l = re.sub(r'Sec\s+VIII-1', 'Sec VIII 第 1 卷', l, flags=re.IGNORECASE)
        l = re.sub(r'UG-(\d+)', r'U G 第 \1 条', l)
        l = re.sub(r'UW-(\d+)', r'U W 第 \1 条', l)
        l = re.sub(r'UCS-(\d+)', r'U C S 第 \1 条', l)
        l = re.sub(r'UHA-(\d+)', r'U H A 第 \1 条', l)
        l = re.sub(r'QW-(\d+)', r'Q W 第 \1 条', l)
        
        # 确保每个独立段落/列表项末尾有明确标点，在 TTS 中产生自然停顿
        if not l.endswith(("。", "！", "？", "；", "：")):
            l += "。"
        cleaned_lines.append(l)

    # 拼接段落
    text = " 。 ".join(cleaned_lines)

    # 2. 移除粗体/斜体/行内代码等 Markdown 标记
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # 3. 彻底消除连续重复的无意义符号（防止触发重复发音）
    text = re.sub(r'[\-+_=~*#|]{2,}', ' ', text)

    # 4. 精准范围与比例转换（只有在数字之间时才转为“至”或“比”）
    # 4.1 百分比范围: 10%~20% 或 10%-20%
    text = re.sub(r'(\d+(?:\.\d+)?)%\s*[~～\-至]\s*(\d+(?:\.\d+)?)%', r'百分之\1至百分之\2', text)
    text = re.sub(r'(\d+(?:\.\d+)?)%', r'百分之\1', text)
    # 4.2 数值范围: 10~20 或 10-20 (排除负数情况，要求两边都是数字)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*[~～\-]\s*(\d+(?:\.\d+)?)', r'\1至\2', text)
    # 4.3 比例 2:1 -> 2 比 1
    text = re.sub(r'(\d+)\s*:\s*(\d+)', r'\1 比 \2', text)

    # 5. 特定复杂公式口语化
    text = text.replace(r't = \frac{P \cdot R}{S \cdot E - 0.6P}', 't 等于 P 乘以 R 除以 S 乘以 E 减去 0.6 倍 P')
    text = text.replace(r't = \frac{P \cdot D}{2S \cdot E - 0.2P}', 't 等于 P 乘以 D 除以 2 倍 S 乘以 E 减去 0.2 倍 P')
    text = text.replace(r't = \frac{P \cdot L \cdot M}{2S \cdot E - 0.2P}', 't 等于 P 乘以 L 乘以 M 除以 2 倍 S 乘以 E 减去 0.2 倍 P')

    # 希腊字母口语化
    greek_tts_map = {
        r'\alpha': ' 阿尔法 ', r'\beta': ' 贝塔 ', r'\gamma': ' 伽马 ', r'\Gamma': ' 伽马 ',
        r'\delta': ' 德尔塔 ', r'\Delta': ' 德尔塔 ', r'\epsilon': ' 艾普西隆 ', r'\varepsilon': ' 艾普西隆 ',
        r'\zeta': ' 截塔 ', r'\eta': ' 艾塔 ', r'\theta': ' 西塔 ', r'\Theta': ' 西塔 ',
        r'\iota': ' 约塔 ', r'\kappa': ' 卡帕 ', r'\lambda': ' 兰姆达 ', r'\Lambda': ' 兰姆达 ',
        r'\mu': ' 缪 ', r'\nu': ' 纽 ', r'\xi': ' 克西 ', r'\Xi': ' 克西 ',
        r'\pi': ' 派 ', r'\Pi': ' 派 ', r'\rho': ' 柔 ', r'\sigma': ' 西格玛 ',
        r'\Sigma': ' 西格玛 ', r'\tau': ' 套 ', r'\upsilon': ' 宇普西龙 ', r'\phi': ' 斐 ',
        r'\Phi': ' 斐 ', r'\varphi': ' 斐 ', r'\chi': ' 希 ', r'\psi': ' 普西 ',
        r'\Psi': ' 普西 ', r'\omega': ' 欧米伽 ', r'\Omega': ' 欧米伽 ',
        'α': ' 阿尔法 ', 'β': ' 贝塔 ', 'γ': ' 伽马 ', 'Γ': ' 伽马 ',
        'δ': ' 德尔塔 ', 'Δ': ' 德尔塔 ', 'ε': ' 艾普西隆 ',
        'ζ': ' 截塔 ', 'η': ' 艾塔 ', 'θ': ' 西塔 ', 'Θ': ' 西塔 ',
        'ι': ' 约塔 ', 'κ': ' 卡帕 ', 'λ': ' 兰姆达 ', 'Λ': ' 兰姆达 ',
        'μ': ' 缪 ', 'ν': ' 纽 ', 'ξ': ' 克西 ', 'Ξ': ' 克西 ',
        'π': ' 派 ', 'Π': ' 派 ', 'ρ': ' 柔 ', 'σ': ' 西格玛 ',
        'Σ': ' 西格玛 ', 'τ': ' 套 ', 'υ': ' 宇普西龙 ', 'φ': ' 斐 ',
        'Φ': ' 斐 ', 'χ': ' 希 ', 'ψ': ' 普西 ', 'Ψ': ' 普西 ',
        'ω': ' 欧米伽 ', 'Ω': ' 欧米伽 '
    }
    for k, v in greek_tts_map.items():
        if k.startswith('\\'):
            text = re.sub(re.escape(k) + r'\b', v, text)
        else:
            text = text.replace(k, v)

    # 6. LaTeX 结构与函数
    text = re.sub(r'\\sqrt\{\\frac\{([^{}]+)\}\{([^{}]+)\}\}', r'根号下 \1 除以 \2', text)
    text = re.sub(r'\\sqrt\{([^{}]+)\}', r'根号下 \1', text)
    text = re.sub(r'\\left\(|\\right\)', '', text)
    text = re.sub(r'\\left\[|\\right\]', '', text)
    text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1 除以 \2', text)
    text = re.sub(r'\\Delta\s*t_\{?thin\}?|\\Delta\s*t_{\\text\{thin\}}', '冲压减薄裕量', text)
    text = re.sub(r'\\text\{([^{}]+)\}', r'\1', text)

    # 7. 温标识别
    text = re.sub(r'(\d+(?:\.\d+)?)\s*(?:℃|°C|\^\s*\\circ\s*\\text\{C\}|\^\s*\\circ\s*C|\\degree\s*C)', r'\1 摄氏度 ', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*(?:°F|\^\s*\\circ\s*\\text\{F\}|\^\s*\\circ\s*F|\\degree\s*F)', r'\1 华氏度 ', text)

    # 8. 小数点逐位发音
    digit_map = {'0':'零', '1':'一', '2':'二', '3':'三', '4':'四', '5':'五', '6':'六', '7':'七', '8':'八', '9':'九'}
    def fix_decimal_speech(m):
        int_p = m.group(1)
        dec_p = m.group(2)
        int_str = '零' if int_p == '0' else int_p
        dec_str = ''.join(digit_map.get(d, d) for d in dec_p)
        return f'{int_str}点{dec_str}'
    
    text = re.sub(r'(\d+)\.(\d+)', fix_decimal_speech, text)

    # 9. 运算与比较符号
    text = re.sub(r'\\le\b|\\leq\b|≤', ' 小于等于 ', text)
    text = re.sub(r'\\ge\b|\\geq\b|≥', ' 大于等于 ', text)
    text = re.sub(r'\\times\b|×', ' 乘以 ', text)
    text = re.sub(r'\\cdot\b|·', ' 乘以 ', text)
    text = re.sub(r'\\pm\b|±', ' 正负 ', text)
    text = text.replace('=', ' 等于 ')
    # 只有当 + 位于变量或数字之间时替换为加上，单独的 + 消除
    text = re.sub(r'(?<=\w)\s*\+\s*(?=\w)', ' 加上 ', text)
    text = text.replace('+', ' ')

    # 剥离 LaTeX 的 $ 标记
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    text = text.replace('$', '')

    # 10. 单位与工程缩写
    text = text.replace('ASME', 'A S M E ')
    text = text.replace('Appendix', '附录')
    text = text.replace('MPa', ' 兆帕 ')
    text = text.replace('mm', ' 毫米 ')
    text = text.replace('RT1', ' R T 1 ')
    text = text.replace('RT2', ' R T 2 ')
    text = text.replace('RT3', ' R T 3 ')
    text = text.replace('RT4', ' R T 4 ')
    text = text.replace('RT', ' R T 无损检测 ')

    # 11. 终极符号清洗：清除孤立的符号、括号、反斜杠、多余标点
    text = re.sub(r'[`\*•~_#|\+\-\\\/]', ' ', text)
    text = re.sub(r'[\'\"\(\)\[\]\{\}\<\>]', ' ', text)
    # 只保留汉字、英文字母、数字和核心中文标点
    text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？；：、]', ' ', text)
    
    # 清理多余空格与重复标点
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([，。！？；：、])\s*([，。！？；：、])+', r'\1', text)
    text = re.sub(r'^[，。！？；：、\s]+', '', text)
    text = re.sub(r'[，。！？；：、\s]+$', '。', text)

    return text.strip()

if __name__ == "__main__":
    import argparse
    import asyncio
    parser = argparse.ArgumentParser(description="Clean speech text and generate 3x audio.")
    parser.add_argument("--version", action="version", version="docx-speech-briefing-builder v1.1.0")
    parser.add_argument("--input", help="Input markdown file")
    parser.add_argument("--output", help="Output mp3 file")
    parser.add_argument("--rate", default="+200%", help="Speech rate")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = clean_speech_text(raw)
        if args.output:
            import subprocess
            cmd = ["edge-tts", "--voice", "zh-CN-XiaoxiaoNeural", f"--rate={args.rate}", "--text", cleaned, "--write-media", args.output]
            subprocess.run(cmd, check=True)
            print(f"Audio saved to {args.output}")
        else:
            print(cleaned)
