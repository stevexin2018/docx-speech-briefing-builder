import re

def convert_section_number(m):
    num_str = m.group(1)
    parts = num_str.split('.')
    return '第 ' + ' 点 '.join(parts) + ' 节 '

def clean_speech_text(text: str) -> str:
    """
    通用语音清洗引擎 (v1.2.1)：
    将工程 Markdown / 特殊字符转为自然流畅、高可读性的口语文本。
    - 精准保留数学与工程运算符号（除以、大于、小于、大于等于、小于等于、等于、不等于）；
    - 智能识别标准条款并列（Part 5.2.4/5.4.3 -> Part 5点2点4 5点4点3，UG-28/UG-29 -> UG-28 UG-29，省略斜杠）；
    - 精准识别大纲标题编号 (1. -> 第 1 点, 1.1 -> 第 1 点 1 节, 1.2 -> 第 1 点 2 节)；
    - 保持小数点逐位精准发音 (0.45 -> 零点四五) 与多级章节编号发音；
    - 彻底杜绝 ASCII 边框线、连字符误读。
    """
    if not text:
        return ""

    # 1. 预处理：行级过滤与大纲编号转换
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
            
        # 过滤掉纯符号构成的分割线、装饰线、ASCII 表格边框等 (+----+----+ 或 -------------- 或 ======)
        if re.match(r'^[-+_=\*~#|`\s]{2,}$', l):
            continue
        # 过滤 Markdown 表格对齐分割线: |:---|:---|
        if re.match(r'^\|[\s:\-\+\\|=]+\|$', l):
            continue

        # 移除 Markdown 标题符 (#, ##, ### 等) 与引用/无序列表前缀 (-, *, +)
        l = re.sub(r'^[#>*\-+]+[ \t]*', '', l)

        # 大纲与章节编号口语化转换（杜绝 1. 被吞或 1.2 读成 2）
        # 1.1 多级大纲编号 (如 1.1, 1.2, 2.1.3)
        l = re.sub(r'^(\d+(?:\.\d+)+)[ \t]*', convert_section_number, l)
        # 1.2 顶级大纲/有序列表 (如 1., 2., 1、, 1))
        l = re.sub(r'^(\d+)[.、\)][ \t]*', r'第 \1 点 ', l)

        # 移除纯外框的 | 符号 (如 ASCII 框里的 | 文字 |)
        l = re.sub(r'^\|[ \t]*', '', l)
        l = re.sub(r'[ \t]*\|$', '', l)

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

    # 4. 【关键】条款/章节/标准并列中的斜杠口语化省略（在除法识别前执行，不读“除以”，也不读“斜杠”）
    # 4.1 复合条款名并列 (如 UG-28/UG-29, UW-11/UW-12, VIII-1/VIII-2)
    text = re.sub(r'([A-Za-z]+-[\d\w]+)\s*/\s*([A-Za-z]+-[\d\w]+)', r'\1 \2', text)
    # 4.2 Part X/Part Y 或 Clause X/Clause Y
    text = re.sub(r'((?:Part|Clause|Section|Table|Fig|Figure)\s*[\w\.]+)\s*/\s*((?:Part|Clause|Section|Table|Fig|Figure)?\s*[\w\.]+)', r'\1 \2', text, flags=re.IGNORECASE)
    # 4.3 多级章节编号并列 (如 5.2.4/5.4.3 或 4.1.2/4.1.3)
    text = re.sub(r'(\b\d+(?:\.\d+)+\b)\s*/\s*(\b\d+(?:\.\d+)+\b)', r'\1 \2', text)
    # 4.4 中文条款并列 (如 第 28 条/第 29 条)
    text = re.sub(r'(第\s*\d+\s*条)\s*/\s*(第\s*\d+\s*条)', r'\1 \2', text)

    # 5. 标准与条款口语发音
    text = re.sub(r'Sec\s+VIII-1', 'Sec VIII 第 1 卷', text, flags=re.IGNORECASE)
    text = re.sub(r'UG-(\d+)', r'U G 第 \1 条', text)
    text = re.sub(r'UW-(\d+)', r'U W 第 \1 条', text)
    text = re.sub(r'UCS-(\d+)', r'U C S 第 \1 条', text)
    text = re.sub(r'UHA-(\d+)', r'U H A 第 \1 条', text)
    text = re.sub(r'QW-(\d+)', r'Q W 第 \1 条', text)

    # 6. 多级章节编号口语化 (如 5.2.4 -> 5 点 2 点 4)
    def convert_multi_dot(m):
        parts = m.group(0).split('.')
        return ' 点 '.join(parts)
    text = re.sub(r'\b\d+(?:\.\d+){2,}\b', convert_multi_dot, text)

    # 7. 小数点逐位发音 (如 0.385 -> 零点三八五)
    digit_map = {'0':'零', '1':'一', '2':'二', '3':'三', '4':'四', '5':'五', '6':'六', '7':'七', '8':'八', '9':'九'}
    def fix_decimal_speech(m):
        int_p = m.group(1)
        dec_p = m.group(2)
        int_str = '零' if int_p == '0' else int_p
        dec_str = ''.join(digit_map.get(d, d) for d in dec_p)
        return f'{int_str}点{dec_str}'
    text = re.sub(r'(\d+)\.(\d+)', fix_decimal_speech, text)

    # 8. 比例与范围 (2:1 -> 2 比 1, 10-20mm -> 10至20毫米)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*[:比]\s*(\d+(?:点[\w]+)?)', r'\1 比 \2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)%\s*[~～\-至]\s*(\d+(?:点[\w]+)?)%', r'百分之\1至百分之\2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*[~～\-至]\s*(\d+(?:点[\w]+)?)', r'\1至\2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)%', r'百分之\1', text)

    # 9. 希腊字母口语化
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

    # 10. 比较与运算符号口语化（精准保留 大于、小于、大于等于、小于等于、等于、不等于、除以、乘以）
    # 10.1 比较符
    text = re.sub(r'\\ge\b|\\geq\b|>=|≥', ' 大于等于 ', text)
    text = re.sub(r'\\le\b|\\leq\b|<=|≤', ' 小于等于 ', text)
    text = re.sub(r'!=|≠|\\ne\b|\\neq\b', ' 不等于 ', text)
    text = re.sub(r'>', ' 大于 ', text)
    text = re.sub(r'<', ' 小于 ', text)
    text = re.sub(r'==|(?<=\w)\s*=\s*(?=\w)|(?<=\s)=\s*(?=\s)', ' 等于 ', text)

    # 10.2 乘除法与加减
    text = re.sub(r'\\times\b|×|\\cdot\b|·', ' 乘以 ', text)
    text = re.sub(r'\\pm\b|±', ' 正负 ', text)
    # 除法/比值: 凡是在英文、数字、下标花括号之间的 / 均读作 除以
    text = re.sub(r'([A-Za-z0-9_\}]+)\s*/\s*([A-Za-z0-9_\{]+)', r'\1 除以 \2', text)
    # 加号
    text = re.sub(r'(?<=\w)\s*\+\s*(?=\w)', ' 加上 ', text)

    # 11. LaTeX 结构与函数
    text = re.sub(r'\\sqrt\{\\frac\{([^{}]+)\}\{([^{}]+)\}\}', r'根号下 \1 除以 \2', text)
    text = re.sub(r'\\sqrt\{([^{}]+)\}', r'根号下 \1', text)
    text = re.sub(r'\\left\(|\\right\)', '', text)
    text = re.sub(r'\\left\[|\\right\]', '', text)
    text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1 除以 \2', text)
    text = re.sub(r'\\Delta\s*t_\{?thin\}?|\\Delta\s*t_{\\text\{thin\}}', '冲压减薄裕量', text)
    text = re.sub(r'\\text\{([^{}]+)\}', r'\1', text)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)

    # 12. 温标识别
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*(?:℃|°C|\^\s*\\circ\s*\\text\{C\}|\^\s*\\circ\s*C|\\degree\s*C)', r'\1 摄氏度 ', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*(?:°F|\^\s*\\circ\s*\\text\{F\}|\^\s*\\circ\s*F|\\degree\s*F)', r'\1 华氏度 ', text)

    # 13. 单位与工程缩写
    text = text.replace('ASME', 'A S M E ')
    text = text.replace('Appendix', '附录')
    text = text.replace('MPa', ' 兆帕 ')
    text = text.replace('mm', ' 毫米 ')
    text = text.replace('RT1', ' R T 1 ')
    text = text.replace('RT2', ' R T 2 ')
    text = text.replace('RT3', ' R T 3 ')
    text = text.replace('RT4', ' R T 4 ')
    text = text.replace('RT', ' R T 无损检测 ')

    # 14. 清理孤立无用符号（保留汉字、英文字母、数字和核心中文标点）
    text = re.sub(r'[`\*•~_#|\\\'\"<>\(\)\[\]\{\}]', ' ', text)
    text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？；：、]', ' ', text)
    
    # 15. 空格与标点修剪
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([，。！？；：、])\s*([，。！？；：、])+', r'\1', text)
    text = re.sub(r'^[，。！？；：、\s]+', '', text)
    text = re.sub(r'[，。！？；：、\s]+$', '。', text)

    return text.strip()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean speech text and generate 3x audio.")
    parser.add_argument("--version", action="version", version="docx-speech-briefing-builder v1.2.1")
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
