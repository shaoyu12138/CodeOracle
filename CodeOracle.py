from __future__ import annotations

import json
import random
import sys
from datetime import datetime
from typing import List, Tuple, Optional

# ===== 常量 & 默认文件路径 =====
HEXAGRAM_DATA_FILE = "assets/64_Gua_Data.json"          # 六十四卦基础数据
JIAO_SHI_DATA_FILE = "assets/64_Gua_Data_4096.json"     # 焦氏易林
PROMPT_FILE         = "assets/prompt.txt"               # 解卦提示词

# --------------------------------------------------------------------------
# ↓↓↓                 I/O 与通用工具函数（保持精简）               ↓↓↓
# --------------------------------------------------------------------------

def _load_prompts(file_path: str = PROMPT_FILE) -> List[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"警告：未找到提示词文件 {file_path}，将使用默认提示。")
        return []
    except Exception as e:
        print(f"加载提示词时出错: {e}")
        return []

def _prompt_user_input(output: List[str]) -> Tuple[str, str]:
    """仅收集问题背景与问题本身"""
    background = input("请输入您的问题背景：").strip()
    question   = input("请输入您的问题：").strip()
    output.append(f"\n## 占卜")
    output.append(f"- 问题背景：{background}")
    output.append(f"- 问题：{question}")
    output.append("\n---\n你的解卦：")
    return background, question

def _load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 时发生错误: {e}")
        return []

# --------------------------------------------------------------------------
# ↓↓↓                 铜钱法摇卦核心算法 (6‑bit)                 ↓↓↓
# --------------------------------------------------------------------------

# 阳爻 = 0, 阴爻 = 1

def _toss_coin() -> int:
    """模拟投掷一枚铜钱（0 = 阳，1 = 阴）"""
    return random.randint(0, 1)

def _toss_three_coins() -> int:
    """每次摇卦，返回铜钱总点数（阳=3分，阴=2分）"""
    coins = [_toss_coin() for _ in range(3)]
    return coins.count(0) * 3 + coins.count(1) * 2

def _interpret_line(total: int) -> tuple[int, int, bool]:
    """根据总点数返回：(本爻值, 变爻值, 是否变爻)"""
    if total == 6:      # 老阴（阴 → 阳）
        return 1, 0, True
    if total == 7:      # 少阳（阳）
        return 0, 0, False
    if total == 8:      # 少阴（阴）
        return 1, 1, False
    if total == 9:      # 老阳（阳 → 阴）
        return 0, 1, True
    raise ValueError(f"无效总点数: {total}")

def _generate_hexagram() -> tuple[int, int, int]:
    """随机摇卦，返回：(本卦, 变卦, 变爻掩码) (均为 6 位 bit 整数)"""
    ben = bian = mask = 0
    for i in range(6):           # i=0 对应初爻
        total = _toss_three_coins()
        val, new_val, changed = _interpret_line(total)
        ben  |= (val     << i)
        bian |= (new_val << i)
        if changed:
            mask |= (1 << i)
    return ben, bian, mask

def _determine_shiyao(orig_bits: int) -> int:
    """计算世爻(1‑6)：在六爻皆动且非纯乾/坤时使用"""
    lower = lambda b: b & 0b000111
    upper = lambda b: (b >> 3) & 0b000111
    is_pure = lambda b: lower(b) == upper(b)
    if is_pure(orig_bits):
        return 6
    working = orig_bits
    steps = [[1], [2], [3], [4], [5], [4], [1, 2, 3]]
    for group in steps:
        for pos in group:
            working ^= 1 << (pos - 1)
        if is_pure(working):
            return max(group)
    raise RuntimeError("世爻计算失败：七步内未得纯卦")

def _main_moving_yao(orig_bits: int, new_bits: int, mask_bits: int) -> int:
    """计算主爻编号(0=静,1‑6=爻位,7=乾坤特别)"""
    if mask_bits != (orig_bits ^ new_bits):
        raise ValueError("mask_bits必须等于orig_bits^new_bits")
    cnt = mask_bits.bit_count()
    if cnt == 0:
        return 0
    if cnt == 1:
        return mask_bits.bit_length()
    if cnt == 2:
        idxs = [i + 1 for i in range(6) if (mask_bits >> i) & 1]
        states = [(new_bits >> (i - 1)) & 1 for i in idxs]
        if states[0] != states[1]:
            return idxs[states.index(1)]
        return max(idxs)
    if cnt == 3:
        idxs = sorted(i + 1 for i in range(6) if (mask_bits >> i) & 1)
        return idxs[1]
    if cnt == 4:
        still = [i + 1 for i in range(6) if not ((mask_bits >> i) & 1)]
        return min(still)
    if cnt == 5:
        still = [i + 1 for i in range(6) if not ((mask_bits >> i) & 1)]
        return still[0]
    if cnt == 6:
        # 纯乾（全阳0）或纯坤（全阴63）触发七爻
        if orig_bits == 0 or orig_bits == (1 << 6) - 1:
            return 7
        return _determine_shiyao(orig_bits)
    raise ValueError("无效变爻数量")

def _run_hexagram() -> tuple[int, int, int, int, int]:
    """一体化调用：返回 本卦、变卦、掩码、主爻编号、世爻编号 (均为 int)"""
    ben, bian, mask = _generate_hexagram()
    moving = _main_moving_yao(ben, bian, mask)
    shi    = _determine_shiyao(ben)
    return ben, bian, mask, moving, shi

# --------------------------------------------------------------------------
# ↓↓↓                      六十四卦数据查找                     ↓↓↓
# --------------------------------------------------------------------------

def _bits_to_binstr(bits: int) -> str:
    """将 0‑63 的 int 转为 6 位二进制字符串"""
    return format(bits, "06b")

def _lookup_hexagram(binary_str: str, hexagrams: list) -> Optional[dict]:
    """按 6_BIT 字段查找卦象字典"""
    return next((g for g in hexagrams if g.get("6_BIT") == binary_str), None)

def _lookup_jiao_shi(primary: str, changed: str, data: list) -> Optional[dict]:
    return next((e for e in data if e.get("本卦") == primary and e.get("变卦") == changed), None)

# --------------------------------------------------------------------------
# ↓↓↓                 互 / 错 / 综 卦 计算 (6‑bit)                ↓↓↓
# --------------------------------------------------------------------------

def _compute_mutual_bits(bits: int) -> int:
    """互卦：取二三四爻成下卦，三四五爻成上卦"""
    s = _bits_to_binstr(bits)
    mutual_str = s[1:4] + s[2:5]  # len=6
    return int(mutual_str, 2)

def _compute_error_bits(bits: int) -> int:
    """错卦：阴阳全反"""
    return bits ^ 0b111111

def _compute_zong_bits(bits: int) -> int:
    """综卦：上下颠倒"""
    s = _bits_to_binstr(bits)
    return int(s[::-1], 2)

# --------------------------------------------------------------------------
# ↓↓↓                           展示逻辑                          ↓↓↓
# --------------------------------------------------------------------------

def _append_hexagram_desc(title: str, bits: int, hexagrams: list, output: List[str]) -> dict | None:
    """把卦象核心信息写入 output，返回卦象 dict"""
    bin_str = _bits_to_binstr(bits)
    hexagram = _lookup_hexagram(bin_str, hexagrams)
    if not hexagram:
        output.append(f"未找到 {title}：{bin_str}")
        return None

    name = hexagram.get("六十四卦名", "未知")
    # 基本信息
    output.append(f"\n===== {title} =====")
    output.append(f"卦名：{name}（{hexagram.get('六十四卦象', '无')}）")
    output.append(f"上卦：{hexagram.get('上卦', '无')}")
    output.append(f"下卦：{hexagram.get('下卦', '无')}")

    # 新增：世爻及其爻辞
    shi = _determine_shiyao(bits)
    yao_cis = hexagram.get("爻辞", [])
    shi_text = yao_cis[shi - 1] if 1 <= shi <= len(yao_cis) else "无"
    output.append(f"世爻：第 {shi} 爻")
    output.append(f"世爻爻辞：{shi_text}")

    # 继续其他信息
    output.extend([
        f"杂卦：{hexagram.get('杂卦', '无')}",
        f"卦辞：{hexagram.get('卦辞', '无')}",
        f"大象：{hexagram.get('大象', '无')}",
        f"彖传：{hexagram.get('彖传', '无')}",
    ])
    return hexagram

def _append_moving_line_info(hexagram: dict, moving_idx: int, output: List[str]):
    """附加主动爻爻辞、小象等"""
    if moving_idx in (0, 7):
        return  # 无主动爻或纯乾坤七爻特殊，按需扩展
    yarrow = hexagram.get("爻辞", [])
    line_text = yarrow[moving_idx - 1] if 0 <= moving_idx - 1 < len(yarrow) else "无"
    sx = hexagram.get("小象", [])
    sx_text = sx[moving_idx - 1] if 0 <= moving_idx - 1 < len(sx) else "无"
    output.extend([
        f"\n===== 主动爻 =====",
        f"主动爻：第 {moving_idx} 爻",
        f"爻辞：{line_text}",
        f"小象：{sx_text}"
    ])

# --------------------------------------------------------------------------
# ↓↓↓                    外部可调用的唯一函数                     ↓↓↓
# --------------------------------------------------------------------------

def perform_divination(
    hex_file: str = HEXAGRAM_DATA_FILE,
    jiao_file: str = JIAO_SHI_DATA_FILE,
    prompt_file: str = PROMPT_FILE,
) -> None:
    """对外封装完整占卜流程"""

    output: List[str] = _load_prompts(prompt_file)

    hexagrams     = _load_json(hex_file)
    jiao_shi_data = _load_json(jiao_file)
    if not hexagrams:
        print("错误：无法加载六十四卦数据，程序终止。")
        return

    _prompt_user_input(output)

    # ---- 摇卦核心 ----
    ben, bian, mask, moving_idx, _ = _run_hexagram()

    primary_hex = _append_hexagram_desc("本卦（当前状态）", ben, hexagrams, output)
    if primary_hex:
        _append_moving_line_info(primary_hex, moving_idx, output)

    # ---- 变卦 ----
    changed_hex = _append_hexagram_desc("变卦（预测结果）", bian, hexagrams, output)

    # ---- 焦氏易林 ----
    if primary_hex and changed_hex and jiao_shi_data:
        entry = _lookup_jiao_shi(primary_hex.get("六十四卦名"), changed_hex.get("六十四卦名"), jiao_shi_data)
        output.append("\n===== 焦氏易林解 =====")
        if entry:
            output.extend([
                f"本卦：{entry.get('本卦')}",
                f"变卦：{entry.get('变卦')}",
                f"焦氏易林辞：{entry.get('焦氏易林辞', '无')}",
            ])
        else:
            output.append("未找到焦氏易林记录。")

    # ---- 互 / 错 / 综 卦 ----
    mutual_bits = _compute_mutual_bits(ben)
    error_bits  = _compute_error_bits(ben)
    zong_bits   = _compute_zong_bits(ben)

    _append_hexagram_desc("互卦（内在原因）", mutual_bits, hexagrams, output)
    _append_hexagram_desc("错卦（应对策略）", error_bits,  hexagrams, output)
    _append_hexagram_desc("综卦（外在阻力）", zong_bits,   hexagrams, output)

    # ---- 保存结果 ----
    ts   = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file = f"question_{ts}.txt"
    try:
        with open(file, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"\n占卜结果已保存：{file}")
    except Exception as e:
        print(f"\n错误：无法保存结果 {file}，{e}", file=sys.stderr)

# 调试入口 ---------------------------------------------------------
if __name__ == "__main__":
    perform_divination()
