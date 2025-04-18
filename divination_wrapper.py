"""
divination_wrapper.py
-------------------------------------------------
封装完整的周易占卜流程，对外只暴露 perform_divination
主脚本无需关心内部实现。
"""

import json
import random
import sys
from datetime import datetime
from typing import List, Tuple, Optional

# ===== 常量 & 默认文件路径 =====
HEXAGRAM_DATA_FILE = "assets/64_Gua_Data.json"            # 六十四卦基础数据
JIAO_SHI_DATA_FILE = "assets/64_Gua_Data_4096.json"       # 焦氏易林
PROMPT_FILE         = "assets/prompt.txt"                 # 解卦提示词


# --------------------------------------------------------------------------
# ↓↓↓             工具函数（保持原逻辑，仅做小幅整理）               ↓↓↓
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
    while True:
        gender_input = input("请输入性别（0为男，1为女）：").strip()
        if gender_input in ("0", "1"):
            break
        print("输入错误，请输入0或1。")

    background = input("请输入您的问题背景：").strip()
    question   = input("请输入您的问题：").strip()

    output.append(f"\n## 占卜\n- 您的问题背景：{background}")
    output.append(f"- 您的问题：{question}")
    output.append("- 你的解卦：")
    return gender_input, question


def _generate_primary_hexagram_binary(gender: str) -> str:
    """首位性别 + 6 位随机"""
    return gender + format(random.getrandbits(6), "06b")


def _normalize_hexagram_binary(binary_str: str) -> str:
    if len(binary_str) != 7:
        return "0000000"
    return binary_str if binary_str[0] == "0" else "".join("1" if b == "0" else "0" for b in binary_str)


def _load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 时发生错误: {e}")
        return []


def _lookup_hexagram(binary_str: str, hexagrams: list) -> Optional[dict]:
    return next((g for g in hexagrams if g.get("7_BIT") == binary_str), None)


def _lookup_jiao_shi(primary: str, changed: str, data: list) -> Optional[dict]:
    return next((e for e in data if e.get("本卦") == primary and e.get("变卦") == changed), None)


def _fetch_yarrow_line(binary_str: str, hexagrams: list) -> Tuple[Optional[int], str]:
    hexagram = _lookup_hexagram(binary_str, hexagrams)
    if not hexagram:
        return None, "未找到对应卦象"
    yarrow = hexagram.get("爻辞", [])
    if not yarrow:
        return None, "该卦没有爻辞"
    idx = random.randint(1, len(yarrow))
    return idx, yarrow[idx - 1]


def _mask_for_moving_lines(count: int) -> str:
    return ("1" * count).rjust(7, "0") if count > 0 else "0000000"


def _display_hexagram(
    title: str,
    binary: str,
    hexagrams: list,
    output: List[str],
    simplified: bool,
    show_moving_info: bool = True
) -> Tuple[Optional[int], Optional[str]]:
    hexagram = _lookup_hexagram(binary, hexagrams)
    if not hexagram:
        output.append(f"未找到 {title}：{binary}")
        return None, None

    name = hexagram.get("六十四卦名", "未知")
    output.extend([
        f"\n===== {title} =====",
        f"卦名：{name}（{hexagram.get('六十四卦象','无')}）",
        f"上卦：{hexagram.get('上卦','无')}",
        f"下卦：{hexagram.get('下卦','无')}",
        f"杂卦：{hexagram.get('杂卦','无')}",
        *(["二进制：" + binary] if not simplified else []),
        f"卦辞：{hexagram.get('卦辞','无')}",
        f"大象：{hexagram.get('大象','无')}",
    ])

    m_count = None
    if show_moving_info:
        m_count, y_line = _fetch_yarrow_line(binary, hexagrams)
        if m_count:
            mask = _mask_for_moving_lines(m_count)
            output.extend([
                f"动爻：第 {m_count} 爻",
                *(["动爻掩码：" + mask] if not simplified else []),
                f"爻辞：{y_line}"
            ])
            sx = hexagram.get("小象", [])
            output.append(f"小象：{sx[m_count-1] if 0 <= m_count-1 < len(sx) else '无'}")
        else:
            output.append(f"获取动爻失败：{y_line}")

    output.append(f"彖传：{hexagram.get('彖传','无')}")
    return m_count, name


def _compute_changed_hexagram(
    primary: str,
    moving_cnt: int,
    simplified: bool,
    output: List[str]
) -> str | None:
    if moving_cnt <= 0:
        output.append("\n错误：动爻数无效")
        return None

    mask      = _mask_for_moving_lines(moving_cnt)
    rand_bits = format(random.getrandbits(7), "07b")
    actual    = "".join("1" if r == "1" and m == "1" else "0" for r, m in zip(rand_bits, mask))
    or_res    = "".join("1" if p == "1" or a == "1" else "0" for p, a in zip(primary, actual))
    changed   = _normalize_hexagram_binary(or_res)

    if not simplified:
        output.extend([
            "\n----- 变卦计算 -----",
            f"本卦：{primary}",
            f"动爻掩码：{mask}",
            f"随机：{rand_bits}",
            f"实际掩码：{actual}",
            f"按位或：{or_res}",
            f"规范化：{changed}"
        ])
    return changed


# --------------------------------------------------------------------------
# ↓↓↓                     外部可调用的唯一函数                     ↓↓↓
# --------------------------------------------------------------------------

def perform_divination(
    simplified: bool = True,
    print_extra: bool = False,
    hex_file: str = HEXAGRAM_DATA_FILE,
    jiao_file: str = JIAO_SHI_DATA_FILE,
    prompt_file: str = PROMPT_FILE, 
) -> None:
    """
    封装完整占卜流程
    参数：
        simplified  # 是否隐藏二进制与计算细节
        print_extra # 是否为互/错/综卦显示动爻及爻辞
        hex_file    # 六十四卦 JSON 路径
        jiao_file   # 焦氏易林 JSON 路径
    """
    output: List[str] = _load_prompts()

    hexagrams     = _load_json(hex_file)
    jiao_shi_data = _load_json(jiao_file)
    if not hexagrams:
        print("错误：无法加载六十四卦数据，程序终止。")
        return

    gender, _ = _prompt_user_input(output)
    primary_bin = _normalize_hexagram_binary(_generate_primary_hexagram_binary(gender))

    m_cnt, primary_name = _display_hexagram(
        "本卦（当前状态）", primary_bin, hexagrams, output, simplified, True
    )

    # ---- 变卦 ----
    if m_cnt and primary_name:
        changed_bin = _compute_changed_hexagram(primary_bin, m_cnt, simplified, output)
        if changed_bin:
            _, changed_name = _display_hexagram(
                "变卦（预测结果）", changed_bin, hexagrams, output, simplified, False
            )
            if changed_name and jiao_shi_data:
                entry = _lookup_jiao_shi(primary_name, changed_name, jiao_shi_data)
                output.append("\n===== 焦氏易林解 =====")
                if entry:
                    output.extend([
                        f"本卦：{entry.get('本卦')}",
                        f"变卦：{entry.get('变卦')}",
                        f"焦氏易林辞：{entry.get('焦氏易林辞','无')}",
                    ])
                else:
                    output.append(f"未找到 {primary_name} → {changed_name} 的焦氏易林记录。")

    # ---- 互 / 错 / 综 卦 ----
    if len(primary_bin) == 7:
        mutual_bin  = _normalize_hexagram_binary("0" + primary_bin[2:5] + primary_bin[3:6])
        error_bin   = _normalize_hexagram_binary("0" + "".join("1" if b == "0" else "0" for b in primary_bin[1:]))
        zong_bin    = _normalize_hexagram_binary("0" + primary_bin[1:][::-1])

        _display_hexagram("互卦（内在原因）", mutual_bin, hexagrams, output, simplified, print_extra)
        _display_hexagram("错卦（应对策略）", error_bin, hexagrams, output, simplified, print_extra)
        _display_hexagram("综卦（外在困难）", zong_bin, hexagrams, output, simplified, print_extra)

    # ---- 保存结果 ----
    ts   = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file = f"question_{ts}.txt"
    try:
        with open(file, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"\n占卜结果已保存：{file}")
    except Exception as e:
        print(f"\n错误：无法保存结果 {file}，{e}", file=sys.stderr)
