"""
SI Unit Verbalizer (国际单位制量纲语法解析与工程口语化发音器)
================================================================
专为工程技术与标准文档口语化设计，基于文法解析与状态机将复合工程单位
（如 mg/m², μg/cm², N/mm², W/(m·K), kJ/mm, kg/m³ 等）直接编译为自然流畅的专业中文发音。
彻底终结离散单条正则匹配造成的漏网与打补丁问题。
"""

import re

# 1. 基础物理单位中文表
BASE_UNITS = {
    'm': '米',
    'g': '克',
    'Pa': '帕',
    'bar': '巴',
    'J': '焦',
    'N': '牛',
    's': '秒',
    'min': '分钟',
    'h': '小时',
    'd': '天',
    'L': '升',
    'l': '升',
    'W': '瓦',
    'mol': '摩尔',
    'Hz': '赫兹',
    'V': '伏',
    'A': '安',
    'C': '库仑',
    'K': '开尔文',
    'S': '西门子',
    'in': '英寸',
    'ft': '英尺',
    'psi': '磅每平方英寸',
    'ksi': '千磅每平方英寸',
}

# 2. SI 前缀倍数表
PREFIXES = {
    'G': '吉',
    'M': '兆',
    'k': '千',
    'c': '厘',
    'd': '分',
    'm': '毫',
    'u': '微',
    'μ': '微',
    'µ': '微',
    'n': '纳',
    'p': '皮',
}

# 3. 常见组合整体映射（工程专有名词优先）
SPECIAL_COMPOUNDS = {
    'MPa': '兆帕',
    'GPa': '吉帕',
    'kPa': '千帕',
    'Pa': '帕',
    'kJ': '千焦',
    'MJ': '兆焦',
    'GJ': '吉焦',
    'kN': '千牛',
    'MN': '兆牛',
    'mm': '毫米',
    'cm': '厘米',
    'dm': '分米',
    'km': '千米',
    'um': '微米',
    'μm': '微米',
    'µm': '微米',
    'nm': '纳米',
    'mg': '毫克',
    'μg': '微克',
    'µg': '微克',
    'ug': '微克',
    'kg': '千克',
    'mL': '毫升',
    'ml': '毫升',
    'kW': '千瓦',
    'MW': '兆瓦',
    'GW': '吉瓦',
    'mS': '毫西门子',
    'μS': '微西门子',
    'µS': '微西门子',
    'uS': '微西门子',
}

# 4. 指数映射表
EXPONENTS = {
    '2': '平方',
    '²': '平方',
    '3': '立方',
    '³': '立方',
    '4': '四次方',
    '⁴': '四次方',
}

def parse_single_unit(unit_str: str) -> str:
    """解析单个简单带幂次的单位，例如 mg, m², m^2, cm³, μg, kPa, s"""
    unit_str = unit_str.strip()
    if not unit_str:
        return ""
    
    # 提取幂次（支持 ², ³, ⁴, ^2, ^3, 2, 3 等）
    exp_text = ""
    clean_unit = unit_str
    
    exp_match = re.search(r'(?:\^?([²³⁴234]))$', unit_str)
    if exp_match:
        exp_sym = exp_match.group(1)
        exp_text = EXPONENTS.get(exp_sym, "")
        clean_unit = unit_str[:exp_match.start()].strip()
    
    # 查找单位主体
    unit_name = ""
    if clean_unit in SPECIAL_COMPOUNDS:
        unit_name = SPECIAL_COMPOUNDS[clean_unit]
    elif clean_unit in BASE_UNITS:
        unit_name = BASE_UNITS[clean_unit]
    else:
        # 尝试前缀 + 基础单位拆解
        matched = False
        for p, p_name in PREFIXES.items():
            if clean_unit.startswith(p) and len(clean_unit) > len(p):
                base = clean_unit[len(p):]
                if base in BASE_UNITS:
                    unit_name = f"{p_name}{BASE_UNITS[base]}"
                    matched = True
                    break
        if not matched:
            unit_name = clean_unit
            
    # 中文工程习惯：长度单位平方立方为前缀，如“平方米”、“平方厘米”、“立方毫米”
    length_bases = ['米', '毫米', '厘米', '分米', '千米', '微米', '纳米', '英寸', '英尺']
    if exp_text in ['平方', '立方']:
        if unit_name in length_bases:
            return f"{exp_text}{unit_name}"
        else:
            return f"{unit_name}{exp_text}"
    elif exp_text:
        return f"{unit_name}{exp_text}"
    else:
        return unit_name

def verbalize_compound_unit(num_str: str, den_str: str) -> str:
    """将复合除法单位（分子/分母）口语化，用‘每’连接"""
    num_part = parse_single_unit(num_str)
    den_part = parse_single_unit(den_str)
    if num_part and den_part:
        return f"{num_part} 每 {den_part}"
    elif num_part:
        return num_part
    elif den_part:
        return f" 每 {den_part} "
    return ""

def verbalize_text_units(text: str) -> str:
    """
    全文本量纲口语化扫描器：将字符串中所有的物理量纲转换为标准工程口语
    """
    if not text:
        return ""
    
    # 0. 剥离 LaTeX 中的单位包裹，如 \text{mg/m^2} 或 \mathrm{mm}
    text = re.sub(r'\\(?:text|mathrm)\s*\{\s*([^}]+)\s*\}', r' \1 ', text)
    
    # 1. 复合除法单位（如 20mg/m², 50 mg/m^2, 2~5μg/cm², 15kJ/mm, 100 N/mm2, 0.5 mS/m, 2.5 g/cm3）
    # 分子候选集（注意：可能直接贴在数字后面，不能加 \b 前导）
    num_pat = r'(?:mg|μg|µg|ug|kg|g|kJ|MJ|GJ|J|kN|MN|N|MPa|GPa|kPa|Pa|mS|μS|µS|uS|S|W|kW|MW|L|mL|mm|cm|m|km)'
    # 分母候选集（支持 ^2, ^3, ², ³ 等）
    den_pat = r'(?:m(?:(?:\^?[234])|[²³⁴])?|cm(?:(?:\^?[234])|[²³⁴])?|mm(?:(?:\^?[234])|[²³⁴])?|km(?:(?:\^?[234])|[²³⁴])?|in|ft|s|min|h|d|g|kg|L|mL|mol|K)'
    
    pattern_compound = fr'({num_pat})\s*/\s*({den_pat})(?![A-Za-z0-9²³⁴])'
    
    def _rep_compound(m):
        num_u = m.group(1)
        den_u = m.group(2)
        spoken = verbalize_compound_unit(num_u, den_u)
        return f" {spoken} "
        
    text = re.sub(pattern_compound, _rep_compound, text)
    
    # 2. 单独的平方与立方单位（如 100 m², 25 mm², 50 cm³, 12 m^3, 20 m²）
    pattern_pow_unit = r'([A-Za-z\u4e00-\u9fa50-9~～\-])\s*(mm|cm|dm|m|km|in|ft)\s*(?:(?:\^([234]))|([²³⁴]))(?![A-Za-z0-9²³⁴])'
    def _rep_pow(m):
        prefix = m.group(1)
        base_u = m.group(2)
        pow_s = m.group(3) or m.group(4)
        spoken = parse_single_unit(f"{base_u}{pow_s}")
        return f"{prefix} {spoken} "
    text = re.sub(pattern_pow_unit, _rep_pow, text)
    
    # 3. 单独特殊小单位及前缀单位（确保紧贴数字或在独立边界时被精准发音）
    isolated_units = [
        (r'([0-9])\s*(?:mg)(?![A-Za-z0-9])', r'\1 毫克 '),
        (r'([0-9])\s*(?:μg|µg|ug)(?![A-Za-z0-9])', r'\1 微克 '),
        (r'(?<![A-Za-z0-9])(?:μg|µg|ug)(?![A-Za-z0-9])', ' 微克 '),
        (r'([0-9])\s*(?:mL|ml)(?![A-Za-z0-9])', r'\1 毫升 '),
        (r'([0-9])\s*(?:μm|µm|um)(?![A-Za-z0-9])', r'\1 微米 '),
        (r'(?<![A-Za-z0-9])(?:μm|µm|um)(?![A-Za-z0-9])', ' 微米 '),
        (r'([0-9])\s*(?:mS)(?![A-Za-z0-9])', r'\1 毫西门子 '),
        (r'([0-9])\s*(?:μS|µS|uS)(?![A-Za-z0-9])', r'\1 微西门子 '),
        (r'(?<![A-Za-z0-9])(?:μS|µS|uS)(?![A-Za-z0-9])', ' 微西门子 '),
        (r'([0-9])\s*(?:MPa)(?![A-Za-z0-9])', r'\1 兆帕 '),
        (r'([0-9])\s*(?:GPa)(?![A-Za-z0-9])', r'\1 吉帕 '),
        (r'([0-9])\s*(?:kPa)(?![A-Za-z0-9])', r'\1 千帕 '),
        (r'([0-9])\s*(?:kJ)(?![A-Za-z0-9])', r'\1 千焦 '),
        (r'([0-9])\s*(?:J)(?![A-Za-z0-9])', r'\1 焦 '),
        (r'([0-9])\s*(?:N)(?![A-Za-z0-9])', r'\1 牛 '),
        (r'([0-9])\s*(?:W)(?![A-Za-z0-9])', r'\1 瓦 '),
        (r'([0-9])\s*(?:Pa)(?![A-Za-z0-9])', r'\1 帕 '),
        (r'([0-9])\s*(?:bar)(?![A-Za-z0-9])', r'\1 巴 '),
        (r'([0-9])\s*(?:kN)(?![A-Za-z0-9])', r'\1 千牛 '),
        (r'([0-9])\s*(?:mm)(?![A-Za-z0-9])', r'\1 毫米 '),
        (r'([0-9])\s*(?:cm)(?![A-Za-z0-9])', r'\1 厘米 '),
    ]
    for p, repl in isolated_units:
        text = re.sub(p, repl, text)
        
    return text

if __name__ == '__main__':
    samples = [
        "20mg/m²",
        "50 mg/m^2",
        "2～5μg/cm²",
        "15kJ/mm",
        "100 N/mm2",
        "电导率γ0 < 0.5 mS/m",
        "容积 250 mL 与 1000 m³",
        "粗糙度 100 μm",
        "压力 2.5 MPa 和 15 kPa",
        "总水溶性盐面密度通常要求ρA ≤ 20mg/m²",
        "相当于表面氯离子浓度限值在2～5μg/cm²范围。"
    ]
    for s in samples:
        print(f"{s:<30} -> {verbalize_text_units(s)}")
